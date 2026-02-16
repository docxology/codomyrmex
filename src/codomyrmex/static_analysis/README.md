# Static Analysis Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Static analysis module for analyzing source code without executing it. Provides a `StaticAnalyzer` that runs multi-language analysis detecting syntax errors, security vulnerabilities, complexity issues, and code quality problems. Includes a dedicated Pyrefly integration for Python type checking, support for multiple analysis types (quality, security, performance, style), configurable severity levels, and computed code metrics. Results include structured `AnalysisResult` objects with file locations, severity, and suggested fixes.

## Key Exports

### Pyrefly Integration

- **`PyreflyRunner`** -- Runs the Pyrefly type checker on Python source files and directories
- **`PyreflyResult`** -- Structured result from a Pyrefly analysis run containing issues and summary
- **`PyreflyIssue`** -- Individual issue found by Pyrefly with file, line, message, and severity
- **`run_pyrefly()`** -- Convenience function to run Pyrefly analysis on a target path
- **`check_pyrefly_available()`** -- Checks whether the Pyrefly binary is installed and accessible

### Static Analyzer

- **`StaticAnalyzer`** -- Main analyzer class that orchestrates multiple analysis tools and aggregates results
- **`analyze_file()`** -- Analyzes a single file and returns an `AnalysisResult`
- **`analyze_project()`** -- Analyzes an entire project directory and returns an `AnalysisSummary`
- **`analyze_codebase()`** -- Alias for `analyze_project()` for backward compatibility
- **`analyze_code_quality()`** -- Workflow-friendly wrapper that returns a dictionary with success status, issues count, errors, and warnings
- **`get_available_tools()`** -- Returns list of installed analysis tools and their capabilities

### Data Types

- **`AnalysisResult`** -- Individual analysis finding with file path, line number, message, severity, and fix suggestion
- **`AnalysisSummary`** -- Aggregated summary of all analysis results with counts by severity and type
- **`CodeMetrics`** -- Computed code quality metrics (lines of code, complexity, maintainability index)
- **`AnalysisType`** -- Enum for analysis categories: quality, security, performance, style, complexity, documentation
- **`SeverityLevel`** -- Enum for issue severity: info, warning, error, critical
- **`Language`** -- Enum for supported programming languages (Python, JavaScript, TypeScript, Go, Rust, etc.)

## Directory Contents

- `static_analyzer.py` -- StaticAnalyzer class, analyze_file, analyze_project, data types, and enums
- `pyrefly_runner.py` -- PyreflyRunner for Python type checking integration
- `exceptions.py` -- Static analysis exception classes
- `complexity/` -- Code complexity analysis tools (cyclomatic, cognitive complexity)
- `linting/` -- Linting integrations and rule configurations
- `pyproject.toml` -- Dependencies managed via root `pyproject.toml` and `uv`

## Quick Start

```python
from codomyrmex.static_analysis import analyze_codebase, analyze_code_quality

# Alias for analyze_project for backward compatibility.
result = analyze_codebase()

# Analyze code quality for workflow integration.
output = analyze_code_quality()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k static_analysis -v
```

## Navigation

- **Full Documentation**: [docs/modules/static_analysis/](../../../docs/modules/static_analysis/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
