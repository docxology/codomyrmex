# Codomyrmex Agents — scripts/code_review

## Signposting
- **Parent**: [Scripts](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Code review automation scripts providing command-line interfaces for automated code quality analysis, review generation, and quality assessment. This script module enables systematic code review workflows for Codomyrmex projects.

The code_review scripts serve as the primary interface for developers and teams to perform automated code quality analysis and generate review feedback.

## Module Overview

### Key Capabilities
- **File Analysis**: Analyze individual files for code quality issues
- **Project Analysis**: Perform comprehensive project-wide code review
- **Report Generation**: Generate detailed review reports and recommendations
- **Quality Metrics**: Calculate code quality and maintainability scores
- **Multi-Language Support**: Support for various programming languages

### Key Features
- Command-line interface with argument parsing
- Integration with core code review modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for review tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the code review orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `analyze-file` - Analyze a single file for code quality issues
- `analyze-project` - Perform comprehensive project analysis
- `generate-report` - Generate detailed review reports

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--output, -o` - Output file path

```python
def handle_analyze_file(args) -> None
```

Handle file analysis commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `file_path` (str): Path to the file to analyze
  - `language` (str, optional): Programming language (auto-detected if not provided)
  - `output_format` (str, optional): Output format ("json", "text", "html"). Defaults to "text"
  - `severity_threshold` (str, optional): Minimum severity level to report ("info", "warning", "error")

**Returns:** None (outputs analysis results to stdout or file)

```python
def handle_analyze_project(args) -> None
```

Handle project analysis commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `project_path` (str): Path to the project root directory
  - `include_patterns` (list, optional): File patterns to include in analysis
  - `exclude_patterns` (list, optional): File patterns to exclude from analysis
  - `output_format` (str, optional): Output format ("json", "text", "html"). Defaults to "text"
  - `parallel` (bool, optional): Enable parallel processing. Defaults to False

**Returns:** None (outputs comprehensive project analysis results)

```python
def handle_generate_report(args) -> None
```

Handle report generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `analysis_data` (str): Path to analysis data file or directory
  - `report_type` (str, optional): Type of report ("summary", "detailed", "metrics"). Defaults to "summary"
  - `output_path` (str, optional): Output path for generated report
  - `format` (str, optional): Report format ("markdown", "html", "pdf"). Defaults to "markdown"

**Returns:** None (generates and outputs review reports)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities


### Additional Files
- `SPEC.md` – Spec Md

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Logging Integration**: Use centralized logging for all operations
4. **Data Validation**: Validate input files and analysis parameters
5. **Output Consistency**: Provide consistent output formats across commands

### Module-Specific Guidelines

#### File Analysis
- Support analysis of various file types and programming languages
- Provide detailed issue descriptions with line numbers and suggestions
- Include severity levels and confidence scores for findings
- Support both individual file and batch processing

#### Project Analysis
- Perform comprehensive analysis across entire codebases
- Support configurable analysis scopes and patterns
- Provide aggregate metrics and trends
- Enable parallel processing for large projects

#### Report Generation
- Generate actionable reports with specific recommendations
- Include code quality metrics and improvement suggestions
- Support multiple output formats for different audiences
- Provide historical comparison capabilities

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
2. **Analysis Coordination**: Share analysis results with other quality tools
3. **Report Integration**: Combine reports from multiple analysis sources
4. **CI/CD Integration**: Provide analysis results for automated quality gates

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Analysis Testing**: Code analysis produces accurate results
3. **Report Testing**: Generated reports are well-formatted and informative
4. **Integration Testing**: Scripts work with core code review modules

## Version History

- **v0.1.0** (December 2025) - Initial code review automation scripts with analysis and reporting capabilities