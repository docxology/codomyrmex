# Codomyrmex Agents — src/codomyrmex/tools

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Utility tools and helpers for project analysis, dependency management, and validation. Provides dependency analysis, consolidation, validation, project analysis, and deprecation notice management.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `add_deprecation_notices.py` – Add deprecation notices to code
- `analyze_project.py` – Project analysis utilities
- `dependency_analyzer.py` – Dependency analysis
- `dependency_checker.py` – Dependency checking
- `dependency_consolidation_report.md` – Dependency consolidation report
- `dependency_consolidator.py` – Dependency consolidation
- `validate_dependencies.py` – Dependency validation

## Key Classes and Functions

### DependencyAnalyzer (`dependency_analyzer.py`)
- `DependencyAnalyzer()` – Analyze project dependencies
- `analyze_dependencies(project_path: str) -> DependencyReport` – Analyze dependencies
- `find_conflicts(dependencies: list) -> list[Conflict]` – Find dependency conflicts

### DependencyChecker (`dependency_checker.py`)
- `DependencyChecker()` – Check dependency availability
- `check_dependency(name: str, version: str = None) -> bool` – Check if dependency is available
- `check_all_dependencies(requirements: list) -> dict[str, bool]` – Check all dependencies

### DependencyConsolidator (`dependency_consolidator.py`)
- `DependencyConsolidator()` – Consolidate dependencies
- `consolidate(requirements_files: list[str]) -> dict` – Consolidate from multiple files
- `generate_report(consolidated: dict) -> str` – Generate consolidation report

### ProjectAnalyzer (`analyze_project.py`)
- `ProjectAnalyzer()` – Analyze project structure
- `analyze(project_path: str) -> ProjectAnalysis` – Analyze project
- `get_project_metrics(project_path: str) -> dict` – Get project metrics

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation