# Codomyrmex Agents — scripts/static_analysis

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

Static analysis automation scripts providing command-line interfaces for code quality analysis, security scanning, and structural validation. This script module enables automated static analysis workflows for the Codomyrmex platform.

The static_analysis scripts serve as the primary interface for developers and CI/CD systems to perform comprehensive code analysis and quality assessment.

## Module Overview

### Key Capabilities
- **File Analysis**: Analyze individual files for code quality issues
- **Project Analysis**: Comprehensive analysis of entire codebases
- **Tool Integration**: Support for multiple static analysis tools
- **Quality Metrics**: Generate detailed quality and security reports
- **Tool Discovery**: List available analysis tools and capabilities

### Key Features
- Command-line interface with argument parsing
- Integration with core static analysis modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for analysis tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the static analysis orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `analyze-file` - Analyze individual files
- `analyze-project` - Analyze entire projects
- `list-tools` - List available analysis tools

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--output, -o` - Output file path

```python
def handle_analyze_file(args) -> bool
```

Handle file analysis command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `file` (str): Path to file to analyze
  - `output` (str, optional): Output file path
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if analysis completed successfully, False otherwise

**Raises:**
- `FileNotFoundError`: When specified file does not exist
- `StaticAnalysisError`: When analysis operations fail

```python
def handle_analyze_project(args) -> bool
```

Handle project analysis command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `path` (str, optional): Path to project directory. Defaults to current directory
  - `output` (str, optional): Output file path
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if analysis completed successfully, False otherwise

**Raises:**
- `FileNotFoundError`: When specified project directory does not exist
- `StaticAnalysisError`: When analysis operations fail

```python
def handle_list_tools(args) -> bool
```

Handle tool listing command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if tool listing completed successfully, False otherwise

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
3. **Analysis Accuracy**: Ensure accurate static analysis results
4. **Performance**: Handle large codebases efficiently
5. **Security**: Handle analysis results securely

### Module-Specific Guidelines

#### File Analysis
- Support multiple file types and programming languages
- Provide detailed analysis results with severity levels
- Include suggestions for code improvements
- Handle analysis errors gracefully

#### Project Analysis
- Support comprehensive project-wide analysis
- Provide aggregate metrics and summaries
- Handle large projects efficiently
- Generate detailed reports with actionable insights

#### Tool Integration
- Support multiple static analysis tools
- Provide tool capability information
- Handle tool availability and configuration
- Ensure consistent output formatting

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
2. **Quality Integration**: Share results with code scripts
3. **Security Integration**: Coordinate with security scripts
4. **CI/CD Integration**: Provide analysis results for automated pipelines

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Analysis Testing**: Static analysis produces accurate results
3. **Performance Testing**: Scripts handle large codebases efficiently
4. **Output Testing**: Analysis results are well-formatted and actionable
5. **Integration Testing**: Scripts work with core static analysis modules

## Version History

- **v0.1.0** (December 2025) - Initial static analysis automation scripts with file and project analysis capabilities