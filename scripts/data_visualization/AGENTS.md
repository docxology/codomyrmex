# Codomyrmex Agents — scripts/data_visualization

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Data visualization automation scripts providing command-line interfaces for generating charts, plots, and visual representations from data files. This script module enables automated visualization workflows for Codomyrmex projects.

The data_visualization scripts serve as the primary interface for data analysts and developers to create visualizations from various data sources.

## Module Overview

### Key Capabilities
- **Chart Generation**: Create various types of charts from data files
- **Multiple Formats**: Support for CSV, JSON, and other data formats
- **Git Visualization**: Specialized charts for version control data
- **Mermaid Diagrams**: Generate text-based diagrams for documentation
- **Flexible Output**: Support for multiple image formats and display options

### Key Features
- Command-line interface with argument parsing
- Integration with core data visualization modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for visualization tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the data visualization orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options] <data_file>
```

**Available Commands:**
- `line-plot` - Generate line plots from data
- `scatter-plot` - Generate scatter plots from data
- `bar-chart` - Generate bar charts from data
- `histogram` - Generate histograms from data
- `pie-chart` - Generate pie charts from data
- `heatmap` - Generate heatmaps from data
- `git-visualize` - Generate Git repository visualizations

**Global Options:**
- `--output, -o` - Output file path
- `--show` - Display plot interactively

```python
def parse_data_file(file_path: Path)
```

Parse data from various file formats into usable data structures.

**Parameters:**
- `file_path` (Path): Path to the data file to parse

**Returns:** Parsed data in appropriate format for visualization

```python
def handle_line_plot(args) -> None
```

Handle line plot generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `data_file` (str): Path to data file
  - `x_column` (str, optional): Column name for x-axis data
  - `y_column` (str, optional): Column name for y-axis data
  - `title` (str, optional): Plot title
  - `x_label` (str, optional): X-axis label
  - `y_label` (str, optional): Y-axis label
  - `color` (str, optional): Line color
  - `output_path` (str, optional): Output file path

**Returns:** None (generates and saves/displays line plot)

```python
def handle_scatter_plot(args) -> None
```

Handle scatter plot generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `data_file` (str): Path to data file
  - `x_column` (str, optional): Column name for x-axis data
  - `y_column` (str, optional): Column name for y-axis data
  - `title` (str, optional): Plot title
  - `x_label` (str, optional): X-axis label
  - `y_label` (str, optional): Y-axis label
  - `color` (str, optional): Point color
  - `marker` (str, optional): Point marker style
  - `output_path` (str, optional): Output file path

**Returns:** None (generates and saves/displays scatter plot)

```python
def handle_bar_chart(args) -> None
```

Handle bar chart generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `data_file` (str): Path to data file
  - `categories_column` (str, optional): Column name for categories
  - `values_column` (str, optional): Column name for values
  - `title` (str, optional): Chart title
  - `x_label` (str, optional): X-axis label
  - `y_label` (str, optional): Y-axis label
  - `color` (str, optional): Bar color
  - `output_path` (str, optional): Output file path

**Returns:** None (generates and saves/displays bar chart)

```python
def handle_histogram(args) -> None
```

Handle histogram generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `data_file` (str): Path to data file
  - `column` (str, optional): Column name for data
  - `bins` (int, optional): Number of bins. Defaults to 10
  - `title` (str, optional): Histogram title
  - `x_label` (str, optional): X-axis label
  - `y_label` (str, optional): Y-axis label
  - `color` (str, optional): Bar color
  - `output_path` (str, optional): Output file path

**Returns:** None (generates and saves/displays histogram)

```python
def handle_pie_chart(args) -> None
```

Handle pie chart generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `data_file` (str): Path to data file
  - `labels_column` (str, optional): Column name for labels
  - `values_column` (str, optional): Column name for values
  - `title` (str, optional): Chart title
  - `colors` (list, optional): List of colors for slices
  - `output_path` (str, optional): Output file path

**Returns:** None (generates and saves/displays pie chart)

```python
def handle_heatmap(args) -> None
```

Handle heatmap generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `data_file` (str): Path to data file
  - `title` (str, optional): Heatmap title
  - `x_label` (str, optional): X-axis label
  - `y_label` (str, optional): Y-axis label
  - `cmap` (str, optional): Colormap name
  - `output_path` (str, optional): Output file path

**Returns:** None (generates and saves/displays heatmap)

```python
def handle_git_visualize(args) -> None
```

Handle Git repository visualization commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `repo_path` (str): Path to Git repository
  - `visualization_type` (str, optional): Type of visualization ("branch_structure", "commit_timeline", etc.)
  - `output_path` (str, optional): Output file path

**Returns:** None (generates and saves Git repository visualization)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Logging Integration**: Use centralized logging for all operations
4. **Data Validation**: Validate input data formats and structures
5. **Output Handling**: Properly handle different output formats and destinations

### Module-Specific Guidelines

#### Data Processing
- Support multiple data file formats (CSV, JSON, Excel, etc.)
- Validate data structure and content before visualization
- Handle missing or invalid data gracefully
- Provide data type inference and conversion

#### Chart Generation
- Apply appropriate default styling for different chart types
- Support customization through command-line options
- Handle different data dimensions and sizes
- Provide meaningful error messages for visualization failures

#### Git Visualization
- Support various Git repository analysis types
- Generate meaningful visualizations from Git data
- Handle large repositories efficiently
- Provide clear legends and annotations

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Data Sharing**: Coordinate data processing with other analysis scripts
3. **Output Integration**: Share generated visualizations with documentation
4. **Git Integration**: Coordinate Git data access with Git operations scripts

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Data Testing**: Scripts handle various data formats and edge cases
3. **Visualization Testing**: Generated charts are accurate and readable
4. **Integration Testing**: Scripts work with core visualization modules

## Version History

- **v0.1.0** (December 2025) - Initial data visualization automation scripts with chart generation and Git visualization capabilities