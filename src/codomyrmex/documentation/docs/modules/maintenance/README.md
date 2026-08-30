<!-- readme: generated -->

# maintenance

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/maintenance/`

## Overview

Tools Module for Codomyrmex.

The Tools module provides development utilities and helper tools for project analysis,
dependency management, and maintenance tasks. These are command-line utilities
designed to support development workflows and project maintenance.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.
- Integrates with `static_analysis` for code quality analysis.
- Works with `system_discovery` for system introspection.

Available functions:
- analyze_project_structure: Analyze project structure and file organization
- analyze_project_dependencies: Analyze project dependencies
- analyze_code_quality: Analyze code quality metrics
- check_dependencies: Check and validate project dependencies
- consolidate_dependencies: Analyze dependencies for consolidation
- add_deprecation_notice: Add deprecation notice to requirements.txt files

Available classes:
- DependencyAnalyzer: Analyze module dependencies and detect circular imports

Data structures:
- DependencyAnalyzer: Analyzes module dependencies for circular imports
- ProjectAnalyzer: Analyzes project structure and code quality
- DependencyValidator: Validates dependency configurations

## Public Exports

`maintenance` exports 15 public symbols via `__all__`:

`DependencyAnalyzer`, `add_deprecation_notice`, `add_deprecation_notices_main`, `analyze_code_quality`, `analyze_project_dependencies`, `analyze_project_main`, `analyze_project_structure`, `check_dependencies`, `consolidate_dependencies`, `dependency_analyzer_main`, `dependency_checker_main`, `dependency_consolidator_main`, `deps`, `health`, `validate_dependencies_main`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../maintenance/](../../../../maintenance/)
