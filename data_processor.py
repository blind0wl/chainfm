"""
Data processing module for Football Manager player analysis.

This module handles attribute parsing, score computation, and data transformation
for FM exported data.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Callable
import logging

from role_definitions import get_role_definitions, get_expected_role_order

logger = logging.getLogger(__name__)


def parse_attribute_value(val) -> float:
    """
    Parse FM attribute values from scouting reports.

    Handles various formats:
    - 14
    - "13-16" or with unicode dashes
    - "14 (13-16)" -> 14
    - "N/A", "-", "—" -> 0
    
    Args:
        val: The value to parse (can be numeric, string, or None)
        
    Returns:
        Parsed numeric value as float
    """
    # Fast-path for numeric values
    if isinstance(val, (int, float, np.integer, np.floating)):
        try:
            return float(val)
        except Exception:
            return 0.0

    if val is None:
        return 0.0

    s = str(val).strip()
    if not s:
        return 0.0

    # Common non-values
    if s.upper() in {"N/A", "NA", "NONE", "-", "—"}:
        return 0.0

    # Normalize unicode dashes to '-'
    s_norm = s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")

    # If there's a number at the start, prefer it (e.g., "14 (13-16)")
    m_head = re.match(r"\s*(\d{1,3})(?:\D|$)", s_norm)
    if m_head:
        try:
            return float(m_head.group(1))
        except Exception:
            pass

    # Otherwise, if it's a range like "13-16", take midpoint
    nums = re.findall(r"\d{1,3}", s_norm)
    if len(nums) >= 2 and "-" in s_norm:
        try:
            a, b = int(nums[0]), int(nums[1])
            return (a + b) / 2.0
        except Exception:
            pass

    # If at least one integer, take the first
    if nums:
        try:
            return float(nums[0])
        except Exception:
            return 0.0

    # Fallback: try pandas conversion
    try:
        v = pd.to_numeric(s_norm, errors='coerce')
        return float(v) if pd.notna(v) else 0.0
    except Exception:
        return 0.0


def coerce_attribute_series(series: pd.Series, col_name: str) -> pd.Series:
    """
    Convert an attribute column to numeric values robustly.

    Args:
        series: The pandas Series to convert
        col_name: Name of the column for logging purposes
        
    Returns:
        Series with numeric values, NaN filled with 0
    """
    if series.dtype.kind in {"i", "u", "f"}:
        return series.fillna(0)

    # Identify values that are non-numeric before parsing
    non_num_mask = pd.to_numeric(series, errors='coerce').isna()
    parsed = series.map(parse_attribute_value)

    # Debug examples for troubleshooting
    try:
        if non_num_mask.any():
            examples = list(pd.unique(series[non_num_mask].dropna().astype(str)))[:5]
            if examples:
                logger.debug(f"Parsed non-numeric values in '{col_name}': {examples}")
    except Exception:
        pass

    return pd.Series(parsed, index=series.index).fillna(0.0)


def safe_get_attribute(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Return a numeric Series for column or zeros if missing.

    Args:
        df: DataFrame to get column from
        col: Column name to retrieve
        
    Returns:
        Numeric Series with robust parsing applied
    """
    if col in df.columns:
        return coerce_attribute_series(df[col], col)
    
    # Return Series of zeros with same length as df
    return pd.Series([0.0] * len(df), index=df.index)


def compute_derived_attributes(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Compute derived attributes from basic FM attributes.
    
    Args:
        df: DataFrame containing FM data
        
    Returns:
        Dictionary of derived attribute Series
    """
    get = lambda c: safe_get_attribute(df, c)
    
    derived = {}
    
    # Speed composite (Pace + Acceleration)
    derived['Spd'] = (get('Pac') + get('Acc')) / 2
    
    # Work Rate composite (Work Rate + Stamina)
    derived['Work'] = (get('Wor') + get('Sta')) / 2
    
    # Jump mapping (if 'Jum' exists, map to 'Jmp' for display)
    if 'Jum' in df.columns:
        derived['Jmp'] = df['Jum']
    else:
        derived['Jmp'] = pd.Series([0] * len(df), index=df.index)
    
    # Strength for display (map from Str if it exists)
    derived['str'] = get('Str')
    
    logger.info(f"Computed {len(derived)} derived attributes")
    return derived


def compute_role_scores(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Compute all role suitability scores for players.
    
    Args:
        df: DataFrame containing FM data with attributes
        
    Returns:
        Dictionary of role score Series
    """
    get = lambda c: safe_get_attribute(df, c)
    role_definitions = get_role_definitions()
    role_scores = {}
    
    logger.info(f"Computing scores for {len(role_definitions)} roles")
    
    for role_name, role_def in role_definitions.items():
        try:
            # Compute scores more directly using vectorized operations
            scores = []
            for idx in range(len(df)):
                # Get player attributes as scalars
                key_sum = sum(get(attr).iloc[idx] for attr in role_def.key_attrs)
                green_sum = sum(get(attr).iloc[idx] for attr in role_def.green_attrs)
                blue_sum = sum(get(attr).iloc[idx] for attr in role_def.blue_attrs)
                
                score = ((key_sum * 5) + (green_sum * 3) + (blue_sum * 1)) / role_def.total_weight
                scores.append(round(float(score), 1))
            
            role_scores[role_name] = pd.Series(scores, index=df.index, dtype='float64')
            
        except Exception as e:
            logger.warning(f"Failed to compute scores for role {role_name}: {e}")
            role_scores[role_name] = pd.Series([0.0] * len(df), index=df.index, dtype='float64')
    
    logger.info(f"Successfully computed scores for {len(role_scores)} roles")
    return role_scores


# def compute_composite_scores(df: pd.DataFrame) -> Dict[str, pd.Series]:
#     """
#     Compute composite position scores (e.g., FB, CB).
#     
#     Args:
#         df: DataFrame containing FM data
#         
#     Returns:
#         Dictionary of composite score Series
#     """
#     get = lambda c: safe_get_attribute(df, c)
#     composite_defs = get_composite_scores()
#     composite_scores = {}
#     
#     for comp_name, comp_def in composite_defs.items():
#         key_sum = sum(get(attr) for attr in comp_def['key_attrs'])
#         green_sum = sum(get(attr) for attr in comp_def['green_attrs'])
#         blue_sum = sum(get(attr) for attr in comp_def['blue_attrs'])
#         
#         total_weight = (len(comp_def['key_attrs']) * 5 + 
#                        len(comp_def['green_attrs']) * 3 + 
#                        len(comp_def['blue_attrs']) * 1)
#         
#         score = (((key_sum * 5) + (green_sum * 3) + (blue_sum * 1)) / total_weight).round(1)
#         composite_scores[comp_name] = score
#     
#     logger.info(f"Computed {len(composite_scores)} composite scores")
#     return composite_scores


def compute_best_role_summary(df: pd.DataFrame, role_columns: List[str]) -> Dict[str, pd.Series]:
    """
    Compute best role and best score for each player.
    
    Args:
        df: DataFrame containing all computed scores
        role_columns: List of column names that are role scores
        
    Returns:
        Dictionary with 'Best_Score' and 'Best_Role' Series
    """
    if not role_columns:
        logger.warning("No role columns provided for best role computation")
        return {
            'Best_Score': pd.Series([0] * len(df), index=df.index),
            'Best_Role': pd.Series([''] * len(df), index=df.index)
        }
    
    # Filter to only include columns that exist in the DataFrame
    available_role_cols = [col for col in role_columns if col in df.columns]
    
    if not available_role_cols:
        logger.warning("No available role columns found in DataFrame")
        return {
            'Best_Score': pd.Series([0] * len(df), index=df.index),
            'Best_Role': pd.Series([''] * len(df), index=df.index)
        }
    
    # Ensure we only consider numeric columns for max calculation
    numeric_role_cols = []
    for col in available_role_cols:
        try:
            # Convert to numeric if not already
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            if df[col].dtype.kind in 'biufc':  # numeric types
                numeric_role_cols.append(col)
            else:
                logger.debug(f"Skipping non-numeric role column: {col} (dtype: {df[col].dtype})")
        except Exception as e:
            logger.debug(f"Error processing role column {col}: {e}")
    
    if not numeric_role_cols:
        logger.warning("No numeric role columns found")
        return {
            'Best_Score': pd.Series([0] * len(df), index=df.index),
            'Best_Role': pd.Series([''] * len(df), index=df.index)
        }
    
    # Calculate best scores and roles using only numeric columns
    best_scores = df[numeric_role_cols].max(axis=1, numeric_only=True)
    best_roles = df[numeric_role_cols].idxmax(axis=1)
    
    logger.info(f"Computed best roles from {len(numeric_role_cols)} role columns")
    
    return {
        'Best_Score': best_scores,
        'Best_Role': best_roles
    }


def process_fm_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main processing function that computes all scores and transformations.
    
    Args:
        df: Raw FM DataFrame
        
    Returns:
        Processed DataFrame with all computed scores
    """
    if df is None or df.empty:
        logger.error("Cannot process empty or None DataFrame")
        return pd.DataFrame()
    
    logger.info(f"Processing FM data: {len(df)} players, {len(df.columns)} columns")
    
    # Work on a copy to avoid modifying original
    result_df = df.copy()
    
    # Compute derived attributes
    derived_attrs = compute_derived_attributes(result_df)
    
    # Compute role scores
    role_scores = compute_role_scores(result_df)
    
    # Composite scores commented out - no longer needed
    # composite_scores = compute_composite_scores(result_df)
    
    # Combine all new columns
    new_columns = {**derived_attrs, **role_scores}
    
    # Add new columns to result DataFrame
    for col_name, col_data in new_columns.items():
        result_df[col_name] = col_data
    
    # Compute best role summary
    role_column_names = list(role_scores.keys())
    best_role_data = compute_best_role_summary(result_df, role_column_names)
    
    # Add best role columns
    for col_name, col_data in best_role_data.items():
        result_df[col_name] = col_data
    
    logger.info(f"Processing complete: {len(result_df.columns)} total columns")
    return result_df


def get_display_columns() -> List[str]:
    """
    Get the ordered list of columns for display purposes.
    
    Returns:
        List of column names in display order
    """
    return [
        # Basic player info
        'Name', 'Age', 'Club', 'Position',
        
        # Derived stats
        'Spd', 'str', 'Work', 'Jmp',
        
        # All role scores in logical order
        *get_expected_role_order(),
        
        # Composite scores
        'fb', 'cb',
        
        # Summary
        'Best_Score', 'Best_Role'
    ]


def filter_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter DataFrame to only include available display columns in the correct order.
    
    Args:
        df: DataFrame to filter
        
    Returns:
        Filtered DataFrame with columns in display order
    """
    wanted_columns = get_display_columns()
    available_columns = [col for col in wanted_columns if col in df.columns]
    
    logger.info(f"Filtered to {len(available_columns)} display columns from {len(df.columns)} total")
    
    return df[available_columns]


def remove_uid_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove UID columns from DataFrame.
    
    Args:
        df: DataFrame to clean
        
    Returns:
        DataFrame with UID columns removed
    """
    uid_columns = [col for col in df.columns if 'uid' in col.lower()]
    
    if uid_columns:
        logger.info(f"Removing UID columns: {uid_columns}")
        df = df.drop(columns=uid_columns)
    
    return df


def validate_processed_data(df: pd.DataFrame) -> bool:
    """
    Validate that processed data contains expected structure.
    
    Args:
        df: Processed DataFrame to validate
        
    Returns:
        True if validation passes
    """
    if df is None or df.empty:
        logger.error("Processed data is empty")
        return False
    
    # Check for essential columns
    essential_columns = ['Name', 'Best_Score', 'Best_Role']
    missing_essential = [col for col in essential_columns if col not in df.columns]
    
    if missing_essential:
        logger.error(f"Missing essential processed columns: {missing_essential}")
        return False
    
    # Check that we have some role scores
    role_names = get_expected_role_order()
    found_roles = [role for role in role_names if role in df.columns]
    
    if len(found_roles) < 10:  # Expect at least 10 roles
        logger.warning(f"Few role scores found: {len(found_roles)}")
        return False
    
    logger.info("Processed data validation passed")
    return True


logger.info("Data processing module loaded successfully")