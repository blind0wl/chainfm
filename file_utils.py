"""
File utilities for Football Manager data processing.

This module handles file discovery, reading, and basic validation
for FM exported HTML files.
"""

import os
import glob
import pandas as pd
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def find_latest_file(folder: str, prefer_html: bool = True) -> Optional[str]:
    """
    Find the most recently created/modified file in the specified folder.
    
    Args:
        folder: Directory path to search in
        prefer_html: If True, prefer HTML files over other formats
        
    Returns:
        Path to the most recent suitable file, or None if no files found
    """
    if not os.path.exists(folder):
        logger.error(f"Folder does not exist: {folder}")
        return None
        
    candidates = []
    
    if prefer_html:
        # Prefer HTML exports first
        patterns = ('*.html', '*.htm')
        for pattern in patterns:
            candidates.extend(glob.glob(os.path.join(folder, pattern)))
    
    # If no HTML files found, fall back to any regular file
    if not candidates:
        candidates = [p for p in glob.glob(os.path.join(folder, '*')) 
                     if os.path.isfile(p)]
    else:
        candidates = [p for p in candidates if os.path.isfile(p)]
    
    if not candidates:
        logger.warning(f"No suitable files found in {folder}")
        return None
    
    # Filter out files that look like our own output (UUID filenames)
    # and prefer files that contain expected FM data
    real_exports = []
    for candidate in candidates:
        if _looks_like_fm_export(candidate) and not _is_generated_output(candidate):
            real_exports.append(candidate)
    
    # If we found real exports, prefer the newest of them
    if real_exports:
        latest = max(real_exports, key=os.path.getctime)
        logger.info(f"Found FM export file: {latest}")
        return latest
    
    # Fallback: pick newest regular file
    latest = max(candidates, key=os.path.getctime)
    logger.info(f"Using fallback file: {latest}")
    return latest


def _looks_like_fm_export(file_path: str) -> bool:
    """
    Check if a file appears to be a Football Manager export by examining its contents.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file appears to be an FM export
    """
    try:
        tables = pd.read_html(file_path, header=0, keep_default_na=False)
        if not tables:
            return False
            
        # Check if the first table has expected FM columns
        cols = tables[0].columns
        fm_indicators = ['Pac', 'Acc', 'Name', 'Age', 'Position', 'Club']
        return any(indicator in cols for indicator in fm_indicators)
        
    except Exception as e:
        logger.debug(f"Failed to read {file_path} as HTML table: {e}")
        return False


def _is_generated_output(file_path: str) -> bool:
    """
    Check if a file appears to be generated output (e.g., UUID filename).
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file appears to be generated output
    """
    filename = os.path.basename(file_path)
    name_without_ext = filename.split('.')[0]
    
    # Check for our own generated files
    if filename.startswith('fm_analysis_'):
        return True
    
    # Check if filename is alphanumeric only (likely a UUID)
    return name_without_ext.isalnum() and len(name_without_ext) > 20


def read_fm_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Read Football Manager data from an HTML file.
    
    Args:
        file_path: Path to the HTML file containing FM data
        
    Returns:
        DataFrame containing the FM data, or None if reading failed
    """
    try:
        logger.info(f"Reading FM data from: {file_path}")
        tables = pd.read_html(file_path, header=0, keep_default_na=False)
        
        if not tables:
            logger.error(f"No tables found in {file_path}")
            return None
            
        data = tables[0]
        logger.info(f"Successfully read {len(data)} rows and {len(data.columns)} columns")
        return data
        
    except Exception as e:
        logger.error(f"Failed to read FM data from {file_path}: {e}")
        return None


def validate_fm_data(df: pd.DataFrame) -> bool:
    """
    Validate that a DataFrame contains expected FM data structure.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if the DataFrame appears to contain valid FM data
    """
    if df is None or df.empty:
        logger.error("DataFrame is None or empty")
        return False
    
    # Check for essential columns
    essential_columns = ['Name']
    missing_essential = [col for col in essential_columns if col not in df.columns]
    
    if missing_essential:
        logger.error(f"Missing essential columns: {missing_essential}")
        return False
    
    # Check for some expected FM attribute columns
    expected_attributes = ['Pac', 'Acc', 'Str', 'Sta', 'Wor']
    found_attributes = [col for col in expected_attributes if col in df.columns]
    
    if len(found_attributes) < 2:
        logger.warning(f"Few expected FM attributes found: {found_attributes}")
        return False
    
    logger.info("FM data validation passed")
    return True


def get_available_attributes(df: pd.DataFrame) -> List[str]:
    """
    Get a list of available FM attributes from the DataFrame.
    
    Args:
        df: DataFrame containing FM data
        
    Returns:
        List of column names that appear to be FM attributes
    """
    if df is None:
        return []
    
    # Common FM attributes
    fm_attributes = [
        'Acc', 'Aer', 'Agg', 'Agi', 'Ant', 'App', 'Bal', 'Bra', 'Cmd', 'Cmp', 'Cnt', 'Cor',
        'Cro', 'Dec', 'Det', 'Dri', 'Fin', 'Fir', 'Fla', 'Han', 'Hea', 'Jum', 'Kic', 'Ldr',
        'Lon', 'Mar', 'Nat', 'OtB', 'Pac', 'Pas', 'Pos', 'Ref', 'Sta', 'Str', 'Tck', 'Tea',
        'Tec', 'TRO', 'Vis', 'Wor', '1v1', 'Thr', 'CA', 'PA'
    ]
    
    available = [attr for attr in fm_attributes if attr in df.columns]
    logger.info(f"Found {len(available)} FM attributes: {available}")
    return available