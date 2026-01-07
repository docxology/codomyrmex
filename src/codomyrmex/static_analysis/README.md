# static_analysis

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Automated code quality assessment without execution. Orchestrates parsers and analyzers to detect syntax errors, security vulnerabilities, complexity issues, and code quality problems. Provides language-agnostic architecture allowing plugging in analyzers for any language with graceful failure handling.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `docs/` – Subdirectory
- `pyrefly_runner.py` – File
- `requirements.txt` – File
- `static_analyzer.py` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.static_analysis import (
    StaticAnalyzer,
    analyze_file,
    analyze_project,
)

# Analyze a single file
analyzer = StaticAnalyzer()
result = analyze_file("src/my_module.py")
print(f"Issues found: {len(result.issues)}")
for issue in result.issues:
    print(f"  {issue.severity}: {issue.message} at line {issue.line}")

# Analyze entire project
project_result = analyze_project("src/")
print(f"Total issues: {project_result.summary.total_issues}")
print(f"Code quality score: {project_result.summary.quality_score}")

# Get available analysis tools
tools = analyzer.get_available_tools()
print(f"Available tools: {tools}")
```

