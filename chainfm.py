"""
Football Manager Player Analysis Tool

A comprehensive tool for analyzing Football Manager exported player data,
computing role suitability scores, and generating interactive HTML reports.

Usage:
    python chainfm.py [--folder PATH]

The tool will automatically find the latest FM export file in the specified
folder and generate a detailed analysis report.
"""

import sys
import os
import argparse
import logging
from typing import Optional

# Prevent Python from writing .pyc files into __pycache__ in the target folder.
# This avoids error when the script is run in folders where the user
# does not have permission to create files (OneDrive sync folders can be problematic).
sys.dont_write_bytecode = True

# Import our modular components
from config import Config, setup_logging
from file_utils import find_latest_file, read_fm_data, validate_fm_data
from data_processor import process_fm_data, filter_display_columns, remove_uid_columns, validate_processed_data
from html_generator import create_html_report

logger = logging.getLogger(__name__)


def main(folder: str = None) -> bool:
    """
    Main function to process FM data and generate analysis report.
    
    Args:
        folder: Directory path to search for FM export files
        
    Returns:
        True if processing completed successfully, False otherwise
    """
    
    # Use provided folder or default from config
    if folder is None:
        folder = Config.get_default_folder()
    
    # Ensure folder path is clean
    folder = folder.rstrip('\\/')
    
    logger.info(f"Starting FM analysis in folder: {folder}")
    
    try:
        # Step 1: Find the latest FM export file
        logger.info("Searching for latest FM export file...")
        latest_file = find_latest_file(folder, prefer_html=Config.PREFER_HTML_FILES)
        
        if not latest_file:
            logger.error(f"No suitable FM export files found in {folder}")
            print(f"No files found in {folder}")
            return False
        
        logger.info(f"Found file: {latest_file}")
        
        # Step 2: Read the FM data
        logger.info("Reading FM data...")
        raw_data = read_fm_data(latest_file)
        
        if raw_data is None:
            logger.error("Failed to read FM data from file")
            print("Failed to read data from file")
            return False
        
        # Step 3: Validate the raw data
        logger.info("Validating FM data...")
        if not validate_fm_data(raw_data):
            logger.error("FM data validation failed")
            print("Invalid FM data format")
            return False
        
        logger.info(f"Successfully loaded {len(raw_data)} players with {len(raw_data.columns)} columns")
        
        # Step 4: Process the data (compute all scores)
        logger.info("Processing player data and computing role scores...")
        processed_data = process_fm_data(raw_data)
        
        if processed_data.empty:
            logger.error("Data processing failed")
            print("Failed to process player data")
            return False
        
        # Step 5: Clean up the data for display
        logger.info("Preparing data for display...")
        
        # Remove UID columns if configured
        if Config.HIDE_UID_COLUMNS:
            processed_data = remove_uid_columns(processed_data)
        
        # Filter to display columns in the correct order
        display_data = filter_display_columns(processed_data)
        
        # Step 6: Validate processed data
        if not validate_processed_data(display_data):
            logger.warning("Processed data validation failed, but continuing...")
        
        # Step 7: Generate HTML report
        logger.info("Generating HTML report...")
        html_content = create_html_report(display_data)
        
        # Step 8: Save the report
        output_path = Config.get_output_path(folder)
        
        logger.info(f"Saving report to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info("Analysis completed successfully!")
        print(f"Analysis complete! Report saved to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}", exc_info=True)
        print(f"Error: {e}")
        return False


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="Convert FM exported HTML to comprehensive player analysis report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chainfm.py                           # Use default folder
  python chainfm.py --folder "C:\\FM\\Data"   # Use specific folder
  python chainfm.py -f /path/to/fm/exports    # Short form
        """
    )
    
    parser.add_argument(
        "--folder", "-f",
        default=None,
        help=f"Folder to search for latest exported HTML (default: {Config.DEFAULT_FOLDER})"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="FM Player Analysis Tool v2.0"
    )
    
    return parser


def configure_logging_from_args(args: argparse.Namespace):
    """Configure logging based on command line arguments."""
    
    if args.debug:
        # Override config for debug mode
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")


def print_startup_info():
    """Print information about the tool at startup."""
    
    print("=" * 60)
    print("Football Manager Player Analysis Tool")
    print("=" * 60)
    print(f"Version: 2.0")
    print(f"Default folder: {Config.DEFAULT_FOLDER}")
    print(f"Log level: {Config.LOG_LEVEL}")
    print("=" * 60)
    print()


def validate_environment() -> bool:
    """Validate that the environment is set up correctly."""
    
    try:
        # Check if required modules can be imported
        import pandas as pd
        import numpy as np
        
        logger.debug("Environment validation passed")
        return True
        
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        print(f"Error: Missing required Python package: {e}")
        print("Please install required packages: pip install pandas numpy")
        return False


if __name__ == "__main__":
    try:
        # Set up logging first
        setup_logging(Config)
        
        # Print startup information
        print_startup_info()
        
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Parse command line arguments
        parser = setup_argument_parser()
        args = parser.parse_args()
        
        # Configure logging based on arguments
        configure_logging_from_args(args)
        
        # Run main processing
        success = main(args.folder)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)