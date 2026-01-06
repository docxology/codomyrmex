# Static Analysis Examples

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
Demonstrates code quality analysis and static code checking using the Codomyrmex Static Analysis module.

## Overview

The Static Analysis module provides comprehensive code quality checking, including syntax validation, style checking, complexity analysis, and security scanning.

## Examples

### Basic Usage (`example_basic.py`)

- Analyze individual Python files for issues
- Run project-wide static analysis
- Check available analysis tools
- Filter results by severity levels
- Generate detailed analysis reports

**Tested Methods:**
- `analyze_file()` - Analyze a single file (from `test_static_analysis.py`)
- `analyze_project()` - Analyze entire project (from `test_static_analysis.py`)
- `get_available_tools()` - Check tool availability (from `test_static_analysis.py`)

## Configuration

```yaml
analysis:
  target_file: src/codomyrmex/__init__.py  # Single file to analyze
  project_path: src/                       # Project directory
  analysis_types: [basic, style, complexity]
  severity_filter: all                     # Filter by severity
  include_patterns: ["*.py"]               # File patterns to include
  exclude_patterns: ["*/tests/*"]          # Patterns to exclude

tools:
  python:
    pylint: true
    flake8: true
    mypy: false
```

## Running

```bash
cd examples/static_analysis
python example_basic.py
```

## Expected Output

The example will:
1. Check which analysis tools are available
2. Analyze the specified Python file
3. Run project-wide analysis
4. Display summary of issues found
5. Save detailed results to JSON file

Check the log file at `logs/static_analysis_example.log` for detailed analysis output.

## Analysis Types

- **Basic**: Syntax errors, import issues, basic code quality
- **Style**: PEP 8 compliance, code formatting, style issues
- **Complexity**: Cyclomatic complexity, maintainability metrics
- **Security**: Potential security vulnerabilities

## Integration with CI/CD

The static analysis module integrates with CI/CD pipelines to:
- Automatically check code quality on commits
- Block merges with critical issues
- Generate quality reports
- Track code quality trends

## Related Documentation

- [Module README](../../src/codomyrmex/static_analysis/README.md)
- [Unit Tests](../../testing/unit/test_static_analysis.py)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)