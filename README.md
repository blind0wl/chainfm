# Football Manager Player Analysis Tool

A comprehensive tool for analyzing Football Manager exported player data, computing role suitability scores, and generating interactive HTML reports.

## Features

- **Automatic file detection**: Finds the latest FM export file in your specified folder
- **Comprehensive role analysis**: Computes suitability scores for 80+ tactical roles
- **Interactive HTML reports**: Color-coded scores, position filters, and role legends
- **Formation analysis**: Suggests optimal formations based on your squad
- **Modular architecture**: Clean, maintainable code split into logical modules

## Quick Start

1. **Export your squad from FM**: Use the default HTML export format
2. **Run the analysis**:
   ```bash
   python chainfm.py
   ```
3. **Open the generated HTML file** in your browser to view the interactive report

## Installation

### Requirements
- Python 3.7+
- pandas
- numpy

### Setup
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install pandas numpy
   ```
3. Run the tool:
   ```bash
   python chainfm.py --folder "path/to/your/fm/exports"
   ```

## Usage

### Basic Usage
```bash
# Use default folder
python chainfm.py

# Specify custom folder
python chainfm.py --folder "C:\FM\Exports"

# Enable debug logging
python chainfm.py --debug
```

### Configuration

The tool uses a configuration system that can be customized. To create a configuration file:

```python
from config import create_default_config_file
create_default_config_file()
```

This creates `fm_config.ini` with customizable settings for:
- File paths
- Score thresholds
- Display options
- Logging settings

## Project Structure

The tool is organized into several modules for maintainability:

```
FM/
├── chainfm.py              # Main script and command-line interface
├── config.py               # Configuration settings and user preferences  
├── file_utils.py           # File operations and FM data reading
├── data_processor.py       # Score computation and data transformation
├── role_definitions.py     # Tactical role calculations and mappings
├── html_generator.py       # Interactive HTML report generation
├── chainfm_old.py          # Original monolithic script (backup)
└── README.md              # This file
```

### Module Overview

- **`chainfm.py`**: Main entry point with command-line interface and workflow orchestration
- **`config.py`**: Centralized configuration management with user customization support
- **`file_utils.py`**: Handles finding, reading, and validating FM export files
- **`data_processor.py`**: Core data processing logic including attribute parsing and score computation
- **`role_definitions.py`**: Complete tactical role database with calculation formulas
- **`html_generator.py`**: Creates interactive HTML reports with styling and JavaScript

## Features in Detail

### Role Analysis
The tool computes suitability scores (0-20) for every major FM tactical role:
- **Goalkeepers**: GKD, SKD, SKS, SKA
- **Defenders**: All fullback, wing-back, and centre-back variations
- **Midfielders**: Playmakers, destroyers, box-to-box, wide roles
- **Forwards**: Target men, poachers, false 9s, wide forwards

### Interactive Reports
Generated HTML reports include:
- **Color-coded scores**: Green (excellent) to red (poor) based on thresholds
- **Position filters**: Quick filtering by GK/D/M/F positions
- **Role legend**: Toggle role columns on/off with detailed descriptions
- **Formation analyzer**: Find best formations for your squad
- **Responsive design**: Works on desktop and mobile devices

### Data Processing
- **Robust parsing**: Handles various FM export formats and scouting report ranges
- **Missing data handling**: Gracefully handles incomplete player data
- **Attribute validation**: Ensures data quality and consistency
- **Performance optimization**: Efficient processing of large squads

## Customization

### Adding New Roles
To add a new tactical role:

1. Edit `role_definitions.py`:
```python
roles['new_role'] = RoleDefinition('new_role', 'NEW',
    ['key_attr1', 'key_attr2'],        # Key attributes (5x weight)
    ['green_attr1', 'green_attr2'],    # Important attributes (3x weight)  
    ['blue_attr1', 'blue_attr2']       # Useful attributes (1x weight)
)
```

2. Add display names:
```python
ROLE_DISPLAY_NAMES['new_role'] = 'NEW'
FULL_ROLE_DESCRIPTIONS['NEW'] = 'New Role Description'
```

### Modifying Score Thresholds
Edit `config.py` or create `fm_config.ini`:
```ini
[Processing]
excellent_threshold = 16.0
good_threshold = 13.0
average_threshold = 9.0
poor_threshold = 6.0
```

### Custom Styling
Modify the CSS in `html_generator.py` or override styles in the generated HTML.

## Troubleshooting

### Common Issues

**"No files found"**
- Ensure FM exports are in HTML format
- Check the folder path is correct
- Verify file permissions

**"Missing required Python package"**
- Install dependencies: `pip install pandas numpy`
- Ensure Python 3.7+ is installed

**"Invalid FM data format"**
- Export squad data from FM (not player search results)
- Use default FM export settings
- Check the HTML file contains a data table

### Debug Mode
Run with `--debug` flag for detailed logging:
```bash
python chainfm.py --debug
```

### Log Files
Enable file logging in configuration:
```python
Config.ENABLE_FILE_LOGGING = True
```

## Contributing

The modular architecture makes the tool easy to extend:

1. **Bug fixes**: Focus on the relevant module
2. **New features**: Add to appropriate module or create new ones
3. **Role updates**: Modify `role_definitions.py`
4. **UI changes**: Edit `html_generator.py`

## Version History

- **v2.0**: Complete refactor with modular architecture
- **v1.0**: Original monolithic script

## License

This tool is provided as-is for FM community use. Please respect Sports Interactive's terms of service when using FM data. This project was inspired from https://github.com/squirrelplays and their previous work with a local python script for FM24 stat weighting.