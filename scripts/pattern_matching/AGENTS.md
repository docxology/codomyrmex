# Codomyrmex Agents — scripts/pattern_matching

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

Pattern matching automation scripts providing command-line interfaces for code analysis, pattern detection, and structural analysis. This script module enables automated pattern recognition across codebases.

The pattern_matching scripts serve as the primary interface for developers and analysts performing code pattern analysis and structural insights.

## Module Overview

### Key Capabilities
- **Pattern Analysis**: Automated detection of code patterns and anti-patterns
- **Structural Analysis**: Code structure and relationship analysis
- **Dependency Mapping**: Module and function dependency identification
- **Code Metrics**: Complexity and maintainability metrics calculation
- **Analysis Reporting**: Structured reports on code patterns and issues

### Key Features
- Command-line interface with argument parsing
- Integration with core pattern matching modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for analysis tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the pattern matching orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `analyze` - Perform pattern analysis on code
- `full-analysis` - Comprehensive codebase analysis

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--output-format, -f` - Output format (json, text, html)

```python
def handle_analyze(args) -> None
```

Handle pattern analysis commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `target_path` (str): Path to code file or directory to analyze
  - `pattern_types` (list, optional): Types of patterns to detect
  - `output_file` (str, optional): Path to save analysis results

**Returns:** None (performs pattern analysis and outputs results)

```python
def handle_full_analysis(args) -> None
```

Handle comprehensive analysis commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `target_path` (str): Root path for comprehensive analysis
  - `include_metrics` (bool, optional): Include code metrics in analysis. Defaults to True
  - `include_dependencies` (bool, optional): Include dependency analysis. Defaults to True
  - `output_file` (str, optional): Path to save comprehensive analysis results

**Returns:** None (performs comprehensive analysis and outputs results)

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
3. **Analysis Accuracy**: Ensure pattern detection accuracy and relevance
4. **Performance**: Handle large codebases efficiently
5. **Output Quality**: Provide actionable and understandable analysis results

### Module-Specific Guidelines

#### Pattern Analysis
- Support multiple programming languages and frameworks
- Provide configurable pattern detection rules
- Handle both simple and complex pattern types
- Include confidence scores for pattern matches

#### Code Metrics
- Calculate standard code quality metrics
- Provide complexity analysis and maintainability scores
- Include trend analysis capabilities
- Support custom metric definitions

#### Dependency Analysis
- Map module and function dependencies
- Identify circular dependencies and coupling issues
- Provide visualization of dependency graphs
- Support different dependency scopes

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
2. **Code Analysis**: Coordinate with static_analysis scripts
3. **Reporting**: Share analysis results with documentation scripts
4. **Quality Gates**: Provide data for CI/CD quality checks

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Analysis Testing**: Pattern detection works accurately
3. **Performance Testing**: Scripts handle large codebases efficiently
4. **Output Testing**: Results are actionable and well-formatted
5. **Integration Testing**: Scripts work with core pattern matching modules

## Version History

- **v0.1.0** (December 2025) - Initial pattern matching automation scripts with analysis and detection capabilities