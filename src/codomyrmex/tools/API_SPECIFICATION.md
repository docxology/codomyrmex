# Tools Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `tools` module provides a suite of command-line utilities and helper functions for project analysis, dependency management, and code quality assessment.

## 2. Core Components

### 2.1 Analysis Functions
- **`analyze_project_structure(root_path: str) -> dict`**: Scans the project directory and returns a structural report.
- **`analyze_code_quality(files: List[str]) -> dict`**: Runs quality metrics on specified files.
- **`analyze_project_dependencies(root_path: str) -> dict`**: Analyzes imports and external requirements.

### 2.2 Dependency Management
- **`check_dependencies(requirements_file: str) -> bool`**: Validates installed packages against requirements.
- **`consolidate_dependencies(files: List[str]) -> dict`**: Merges multiple dependency files into a canonical list.
- **`add_deprecation_notice(file_path: str, package: str) -> None`**: marks a package as deprecated in requirements files.

### 2.3 Classes
- **`DependencyAnalyzer`**: Class for detecting circular imports and dependency graph issues.

## 3. CLI Entry Points
The module exports several main functions intended for CLI usage:
- `analyze_project_main`
- `dependency_analyzer_main`
- `dependency_checker_main`
- `dependency_consolidator_main`
- `validate_dependencies_main`
- `add_deprecation_notices_main`

## 4. Usage Example

```python
from codomyrmex.tools import analyze_project_structure, check_dependencies

# Analyze structure
report = analyze_project_structure("./src")
print(f"Found {len(report['modules'])} modules")

# Check deps
if check_dependencies("requirements.txt"):
    print("Dependencies valid")
else:
    print("Missing dependencies")
```
