# tools

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Development utilities and helper tools for project analysis, dependency management, and maintenance tasks. Provides command-line utilities that analyze project structure, detect circular imports, validate dependency configurations, and consolidate scattered requirements files into a centralized `pyproject.toml` setup.

## Key Exports

### Analysis Functions

- **`analyze_project_structure()`** -- Analyze project directory structure and file organization
- **`analyze_project_dependencies()`** -- Analyze project dependencies from pyproject.toml and requirements files
- **`analyze_code_quality()`** -- Analyze code quality metrics across the project
- **`check_dependencies()`** -- Check and validate that all declared project dependencies are satisfiable
- **`consolidate_dependencies()`** -- Analyze scattered requirements.txt files for consolidation into pyproject.toml
- **`add_deprecation_notice()`** -- Add deprecation notices to legacy requirements.txt files pointing to pyproject.toml

### Classes

- **`DependencyAnalyzer`** -- Scans Python source files via AST to extract imports, build a dependency graph, and detect circular import chains

### CLI Entry Points

- **`analyze_project_main()`** -- CLI entry point for project structure and code quality analysis
- **`dependency_analyzer_main()`** -- CLI entry point for circular import detection
- **`dependency_checker_main()`** -- CLI entry point for dependency validation
- **`dependency_consolidator_main()`** -- CLI entry point for requirements consolidation
- **`validate_dependencies_main()`** -- CLI entry point for dependency validation scripts
- **`add_deprecation_notices_main()`** -- CLI entry point for batch deprecation notice insertion

## Directory Contents

- `analyze_project.py` -- Project structure analysis, dependency scanning, and code quality reporting
- `dependency_analyzer.py` -- AST-based import extraction and circular dependency detection
- `dependency_checker.py` -- Validates that project dependencies are installed and satisfiable
- `dependency_consolidator.py` -- Analyzes module-level requirements.txt files for consolidation
- `validate_dependencies.py` -- Dependency validation entry point
- `add_deprecation_notices.py` -- Adds deprecation notices to legacy requirements.txt files
- `dependency_consolidation_report.md` -- Generated report from dependency consolidation analysis

## Navigation

- **Full Documentation**: [docs/modules/tools/](../../../docs/modules/tools/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
