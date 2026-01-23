# Codomyrmex Agents - src/codomyrmex/tools

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Tools module provides development utilities and helper tools for project analysis, dependency management, and maintenance tasks. These are command-line utilities designed to support development workflows and project maintenance operations.

## Active Components

- `__init__.py` - Module entry point exporting analysis functions and CLI entry points
- `analyze_project.py` - Project structure and code quality analysis
- `dependency_analyzer.py` - Module dependency analysis with circular import detection
- `dependency_checker.py` - Dependency validation utilities
- `dependency_consolidator.py` - Dependency consolidation analysis
- `validate_dependencies.py` - Dependency validation CLI
- `add_deprecation_notices.py` - Add deprecation notices to requirements.txt files
- `dependency_consolidation_report.md` - Generated dependency consolidation report
- `API_SPECIFICATION.md` - API documentation
- `SPEC.md` - Technical specification

## Key Classes

- **DependencyAnalyzer** - Analyzes module dependencies for circular imports and hierarchy violations
  - `scan_module(module_name)` - Scan a module for imports
  - `scan_all_modules()` - Scan all modules in the repository
  - `detect_circular_dependencies()` - Find circular import chains
  - `validate_dependency_hierarchy()` - Check against allowed dependency rules
  - `generate_report()` - Generate human-readable analysis report
  - `generate_mermaid_graph()` - Generate Mermaid diagram of dependencies
  - `analyze()` - Run complete dependency analysis

## Operating Contracts

- Project analysis functions (`analyze_project_structure`, `analyze_dependencies`, `analyze_code_quality`) scan from project root
- DependencyAnalyzer uses AST parsing to extract imports from Python files
- Allowed dependencies are defined per-module to enforce layer separation
- Circular dependency detection uses graph traversal algorithms
- Reports are output in Markdown format with optional Mermaid diagrams
- Exit codes: 0 for success/no issues, 1 for issues detected
- Uses `logging_monitoring` for consistent logging
- Integrates with `environment_setup`, `static_analysis`, and `system_discovery` modules

## Signposting

- **Parent Directory**: [codomyrmex](../README.md) - Main package documentation
- **Related Modules**:
  - [static_analysis/](../static_analysis/README.md) - Code quality analysis
  - [environment_setup/](../environment_setup/README.md) - Environment configuration
  - [system_discovery/](../system_discovery/README.md) - System introspection
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
