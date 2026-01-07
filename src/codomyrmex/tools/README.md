# tools

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Utility tools and helpers for project analysis, dependency management, and validation. Provides dependency analysis, consolidation, validation, project analysis, and deprecation notice management.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `add_deprecation_notices.py` – File
- `analyze_project.py` – File
- `dependency_analyzer.py` – File
- `dependency_checker.py` – File
- `dependency_consolidation_report.md` – File
- `dependency_consolidator.py` – File
- `validate_dependencies.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.tools import (
    analyze_project_structure,
    analyze_project_dependencies,
    analyze_code_quality,
    check_dependencies,
    DependencyAnalyzer,
)

# Analyze project structure
structure = analyze_project_structure()
print(f"Total files: {structure['total_files']}")

# Analyze dependencies
deps = analyze_project_dependencies()
print(f"Dependencies: {len(deps['dependencies'])}")

# Analyze code quality
quality = analyze_code_quality()
print(f"Code quality score: {quality['score']}")

# Check dependencies
results = check_dependencies()
for dep, status in results.items():
    print(f"{dep}: {'✓' if status else '✗'}")

# Use dependency analyzer
analyzer = DependencyAnalyzer()
report = analyzer.analyze_dependencies("src/")
print(f"Circular imports found: {len(report.circular_imports)}")
```

