# Agent Guidelines - Maintenance

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Project maintenance utilities covering dependency analysis, circular import detection, requirements
consolidation, and deprecation management. Provides `DependencyAnalyzer` for AST-based import
scanning and layer violation detection, and two MCP tools (`maintenance_health_check`,
`maintenance_list_tasks`) for system health monitoring.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `DependencyAnalyzer`, `analyze_project_structure`, `analyze_code_quality`, `check_dependencies` |
| `dependency_analyzer.py` | `DependencyAnalyzer` — AST-based import scanner and circular dependency detector |
| `analyze_project.py` | `analyze_project_structure()`, `analyze_code_quality()` |
| `dependency_checker.py` | `check_dependencies()` — dependency validation |
| `dependency_consolidator.py` | Requirements file consolidation utilities |
| `mcp_tools.py` | MCP tools: `maintenance_health_check`, `maintenance_list_tasks` |

## Key Classes

- **DependencyAnalyzer** — AST-based import scanner and circular dependency detector
- **analyze_project_structure()** — Project directory and file analysis
- **analyze_code_quality()** — Code quality metrics
- **check_dependencies()** — Dependency validation
- **dependency_consolidator** — Requirements file consolidation

## Agent Instructions

1. **Analyze first** — Run `DependencyAnalyzer` to understand import graph
2. **Check violations** — Use `validate_dependency_hierarchy()` for layer violations
3. **Consolidate deps** — Use consolidator to find scattered requirements.txt
4. **Deprecation notices** — Add notices to legacy requirements.txt pointing to pyproject.toml
5. **Log results** — Generate reports via `generate_report()`

## Common Patterns

```python
from codomyrmex.maintenance.dependency_analyzer import DependencyAnalyzer
from codomyrmex.maintenance.analyze_project import (
    analyze_project_structure,
    analyze_code_quality,
)
from codomyrmex.maintenance.dependency_checker import check_dependencies

# Analyze dependency graph
analyzer = DependencyAnalyzer(".")
analyzer.scan_all_modules()
circular = analyzer.detect_circular_dependencies()
violations = analyzer.validate_dependency_hierarchy()

report = analyzer.generate_report()
print(report)

# Project structure analysis
structure = analyze_project_structure()
quality = analyze_code_quality()

# Dependency validation
deps = check_dependencies()
```

## Testing Patterns

```python
from codomyrmex.maintenance.dependency_analyzer import DependencyAnalyzer

analyzer = DependencyAnalyzer(".")
result = analyzer.analyze()
assert "modules" in result
assert "circular_dependencies" in result
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `maintenance_health_check` | Run a simple health check and return its status | SAFE |
| `maintenance_list_tasks` | List all registered maintenance tasks and their status | SAFE |

## Operating Contracts

- `DependencyAnalyzer` requires `scan_all_modules()` before calling `detect_circular_dependencies()` or `validate_dependency_hierarchy()`
- `analyze_project_structure()` and `analyze_code_quality()` operate on the current working directory
- `maintenance_health_check` is a point-in-time snapshot — run it, don't cache the result
- `DependencyAnalyzer.generate_report()` returns a formatted string — log or print, don't parse it
- **DO NOT** modify `requirements.txt` files; point deprecated ones to `pyproject.toml` instead

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `maintenance_health_check`, `maintenance_list_tasks` | TRUSTED |
| **Architect** | Read + Design | `maintenance_list_tasks` — task queue review, maintenance schedule design | OBSERVED |
| **QATester** | Validation | `maintenance_health_check` — system health verification during VERIFY phase | OBSERVED |
| **Researcher** | Read-only | `maintenance_health_check`, `maintenance_list_tasks` — inspect system health and task state | SAFE |

### Engineer Agent
**Use Cases**: Running health checks during VERIFY, managing maintenance task queues, scheduling system upkeep.

### Architect Agent
**Use Cases**: Reviewing maintenance schedules, designing health check strategies, planning upkeep workflows.

### QATester Agent
**Use Cases**: Running health checks to confirm system operational status, validating maintenance completeness.

### Researcher Agent
**Use Cases**: Inspecting system health status and maintenance task catalog during research and analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
