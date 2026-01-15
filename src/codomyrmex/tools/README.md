# Tools Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## 1. Overview
The `tools` module provides a suite of command-line utilities and reusable scripts for maintaining, analyzing, and improving the Codomyrmex codebase. These tools form the backbone of the project's development workflow.

## 2. Available Tools

### 2.1 Dependency Management
- **`dependency_analyzer.py`**: Scans the codebase to detect circular imports, missing dependencies, and graph complexity.
- **`dependency_checker.py`**: Validates installed packages against `requirements.txt` to ensure environment consistency.
- **`dependency_consolidator.py`**: Merges dependencies from multiple source files into a canonical requirements list.
- **`validate_dependencies.py`**: Verifies that all imports in the source code are declared in the project configuration.
- **`add_deprecation_notices.py`**: Automates the tagging of deprecated packages in requirements files.

### 2.2 Project Analysis
- **`analyze_project.py`**: Performs a structural scan of the project, reporting on file counts, types, and module organization.

## 3. Usage Examples

```bash
# Analyze project dependencies
python -m codomyrmex.tools.dependency_analyzer

# Check environment health
python -m codomyrmex.tools.dependency_checker requirements.txt

# Consolidate requirements
python -m codomyrmex.tools.dependency_consolidator
```

## 4. API Reference
For programmatic usage of these tools, refer to the [API Specification](API_SPECIFICATION.md).

## 5. Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
