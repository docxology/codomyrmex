# Personal AI Infrastructure — Static Analysis Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Static Analysis module provides automated code quality analysis without executing code. It includes a general-purpose `StaticAnalyzer`, a Pyrefly integration for Python-specific analysis, and supports multiple programming languages and analysis types (quality, security, performance). This is a **Core Layer** module central to the PAI VERIFY phase.

## PAI Capabilities

### Code Analysis

Analyze individual files or entire projects:

```python
from codomyrmex.static_analysis import (
    StaticAnalyzer, analyze_file, analyze_project,
    get_available_tools,
)

# Analyze a single file
result = analyze_file("src/main.py")

# Analyze an entire project
summary = analyze_project("src/")

# List available analysis tools
tools = get_available_tools()

# Use the analyzer class directly
analyzer = StaticAnalyzer()
result = analyzer.analyze("src/")
```

### Pyrefly Integration

Python-specific analysis using the Pyrefly tool:

```python
from codomyrmex.static_analysis import (
    PyreflyRunner, run_pyrefly, check_pyrefly_available,
)

if check_pyrefly_available():
    result = run_pyrefly("src/")
    for issue in result.issues:
        print(f"{issue.file}:{issue.line} — {issue.message}")
```

### Workflow Integration

For automated pipeline use:

```python
from codomyrmex.static_analysis import analyze_code_quality

result = analyze_code_quality(path="src/")
# Returns: {"success": True, "issues_count": 5, "errors": [...], "warnings": [...]}
```

### CLI Commands

```bash
codomyrmex static_analysis analyze [path]  # Analyze code quality at path
codomyrmex static_analysis tools           # List available analysis tools
```

## Key Exports

| Category | Exports | Purpose |
|----------|---------|---------|
| **Core Analyzer** | `StaticAnalyzer`, `analyze_file`, `analyze_project`, `analyze_codebase`, `analyze_code_quality`, `get_available_tools` | Main analysis functions |
| **Pyrefly** | `PyreflyRunner`, `PyreflyResult`, `PyreflyIssue`, `run_pyrefly`, `check_pyrefly_available` | Python-specific analysis |
| **Data Types** | `AnalysisResult`, `AnalysisSummary`, `CodeMetrics`, `AnalysisType`, `SeverityLevel`, `Language` | Structured result types |

### Analysis Types

| `AnalysisType` | What It Checks |
|----------------|---------------|
| Quality | Code style, formatting, best practices |
| Security | Potential vulnerabilities, unsafe patterns |
| Performance | Inefficient patterns, resource usage |

### Severity Levels

`SeverityLevel`: `info` | `warning` | `error` | `critical`

### Supported Languages

The `Language` enum defines supported programming languages for analysis.

## MCP Integration

The MCP server's `analyze_python_file` tool delegates to this module's analysis capabilities for Python AST analysis, providing structure inspection (classes, functions, imports, metrics) through the MCP protocol.

## PAI Algorithm Phase Mapping

| Phase | Static Analysis Contribution |
|-------|----------------------------|
| **OBSERVE** | `get_available_tools()` — discover what analysis capabilities are available |
| **VERIFY** | `analyze_file`, `analyze_project`, `run_pyrefly` — validate code quality against standards |
| **LEARN** | `CodeMetrics`, `AnalysisSummary` — capture quality trends over time |

## Architecture Role

**Core Layer** — Depends on `logging_monitoring` and `environment_setup` (Foundation). Used by the VERIFY phase of the PAI Algorithm to validate code artifacts meet quality standards.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
