"""
Configuration settings for Football Manager player analysis.

This module contains all configurable settings including default paths,
output preferences, and analysis parameters.
"""

import os
from typing import Dict, List

# Default configuration settings
class Config:
    """Configuration class containing all settings for FM analysis."""
    
    # File handling settings
    DEFAULT_FOLDER = r"C:\Users\Fluff\OneDrive\Desktop\FM"
    PREFER_HTML_FILES = True
    OUTPUT_FILENAME_PREFIX = "fm_analysis_"
    
    # Data processing settings
    MINIMUM_SCORE = 0.0
    MAXIMUM_SCORE = 20.0
    SCORE_DECIMAL_PLACES = 1
    
    # HTML output settings
    INCLUDE_LEGEND = True
    INCLUDE_FORMATION_ANALYZER = True
    ENABLE_POSITION_FILTERS = True
    ENABLE_SCORE_COLORING = True
    
    # Score color thresholds (0-20 scale)
    SCORE_THRESHOLDS = {
        'excellent': 15.0,  # Green
        'good': 12.0,       # Orange
        'average': 8.0,     # Yellow
        'poor': 5.0         # Red
    }
    
    # Logging settings
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    ENABLE_FILE_LOGGING = False
    LOG_FILE = "fm_analysis.log"
    
    # Performance settings
    MAX_PLAYERS_FOR_PROCESSING = 10000
    ENABLE_PROGRESS_INDICATORS = True
    
    # Column display settings
    HIDE_UID_COLUMNS = True
    HIDE_RAW_ATTRIBUTES = False  # Set to True to hide raw FM attributes in output
    
    # Formation analysis settings
    FORMATION_ANALYSIS_ENABLED = True
    MAX_FORMATIONS_TO_ANALYZE = 6
    
    @classmethod
    def get_default_folder(cls) -> str:
        """Get the default folder path, creating it if it doesn't exist."""
        if not os.path.exists(cls.DEFAULT_FOLDER):
            try:
                os.makedirs(cls.DEFAULT_FOLDER, exist_ok=True)
            except OSError:
                # Fall back to current directory if default can't be created
                return os.getcwd()
        return cls.DEFAULT_FOLDER
    
    @classmethod
    def get_output_path(cls, folder: str, filename_suffix: str = "") -> str:
        """Generate output file path with timestamp."""
        import uuid
        unique_id = uuid.uuid4().hex
        filename = f"{cls.OUTPUT_FILENAME_PREFIX}{filename_suffix}{unique_id}.html"
        return os.path.join(folder, filename)
    
    @classmethod
    def get_log_config(cls) -> Dict:
        """Get logging configuration."""
        return {
            'level': cls.LOG_LEVEL,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'enable_file': cls.ENABLE_FILE_LOGGING,
            'filename': cls.LOG_FILE
        }


# Essential FM attributes that should always be processed if available
ESSENTIAL_ATTRIBUTES = [
    'Acc', 'Pac', 'Sta', 'Wor', 'Str', 'Jum', 'Bal', 'Agi',
    'Fir', 'Pas', 'Tec', 'Dri', 'Fin', 'Hea', 'Lon', 'Mar',
    'Tck', 'Ant', 'Cmp', 'Dec', 'OtB', 'Pos', 'Tea', 'Vis'
]

# Optional FM attributes that may not be present in all exports
OPTIONAL_ATTRIBUTES = [
    'Aer', 'Agg', 'App', 'Bra', 'Cmd', 'Cnt', 'Cor', 'Cro',
    'Det', 'Fla', 'Han', 'Kic', 'Ldr', 'Nat', 'Ref', 'TRO',
    'Thr', '1v1', 'CA', 'PA', 'Age'
]

# Player information columns (non-attribute data)
PLAYER_INFO_COLUMNS = [
    'Name', 'Age', 'Club', 'Position', 'Nationality', 'Height',
    'Weight', 'Wage', 'Transfer Value', 'Contract Expires'
]

# Raw FM attributes to exclude from best role calculation
RAW_FM_ATTRIBUTES = ESSENTIAL_ATTRIBUTES + OPTIONAL_ATTRIBUTES

# Composite attributes (calculated from raw attributes)
COMPOSITE_ATTRIBUTES = ['Spd', 'Work', 'Jmp', 'str']

# Display column priorities (higher number = higher priority)
COLUMN_PRIORITIES = {
    'Name': 1000,
    'Age': 900,
    'Club': 800,
    'Position': 700,
    'Best_Score': 600,
    'Best_Role': 500,
    'Spd': 400,
    'str': 390,
    'Work': 380,
    'Jmp': 370
}

# Position groupings for filtering
POSITION_GROUPS = {
    'GK': ['GK'],
    'D': ['DC', 'DL', 'DR', 'D', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'WB'],
    'M': ['MC', 'ML', 'MR', 'DM', 'AM', 'AMC', 'AML', 'AMR', 'M'],
    'F': ['ST', 'STC', 'STL', 'STR', 'CF', 'LF', 'RF', 'F']
}

# Error handling settings
ERROR_HANDLING = {
    'continue_on_missing_attributes': True,
    'continue_on_parsing_errors': True,
    'default_value_for_missing': 0.0,
    'max_errors_before_abort': 100
}

# Development and debugging settings
DEBUG_SETTINGS = {
    'print_column_info': False,
    'print_processing_steps': False,
    'save_intermediate_files': False,
    'validate_calculations': False
}


def load_user_config(config_file: str = "fm_config.ini") -> Dict:
    """
    Load user configuration from file if it exists.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dictionary of user configuration settings
    """
    user_config = {}
    
    if os.path.exists(config_file):
        try:
            import configparser
            parser = configparser.ConfigParser()
            parser.read(config_file)
            
            # Convert to dictionary
            for section in parser.sections():
                user_config[section] = dict(parser[section])
                
        except Exception as e:
            print(f"Warning: Could not load user config from {config_file}: {e}")
    
    return user_config


def create_default_config_file(config_file: str = "fm_config.ini"):
    """
    Create a default configuration file for user customization.
    
    Args:
        config_file: Path where to create the configuration file
    """
    config_content = """[Paths]
# Default folder to search for FM exports
default_folder = C:\\Users\\Fluff\\OneDrive\\Desktop\\FM

[Processing]
# Score thresholds for color coding (0-20 scale)
excellent_threshold = 15.0
good_threshold = 12.0
average_threshold = 8.0
poor_threshold = 5.0

# Number of decimal places for scores
score_decimals = 1

[Display]
# Show/hide various elements
include_legend = true
include_formation_analyzer = true
enable_position_filters = true
enable_score_coloring = true
hide_uid_columns = true
hide_raw_attributes = false

[Logging]
# Logging level: DEBUG, INFO, WARNING, ERROR
log_level = INFO
enable_file_logging = false
log_file = fm_analysis.log

[Performance]
# Maximum number of players to process
max_players = 10000
show_progress = true
"""
    
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"Created default configuration file: {config_file}")
    except Exception as e:
        print(f"Warning: Could not create config file {config_file}: {e}")


def setup_logging(config: Config = Config):
    """
    Set up logging based on configuration.
    
    Args:
        config: Configuration object with logging settings
    """
    import logging
    
    log_config = config.get_log_config()
    
    # Configure logging level
    level = getattr(logging, log_config['level'].upper(), logging.INFO)
    
    # Set up logging format
    formatter = logging.Formatter(log_config['format'])
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_config['enable_file']:
        try:
            file_handler = logging.FileHandler(log_config['filename'])
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")


# Initialize logging with default configuration
setup_logging()