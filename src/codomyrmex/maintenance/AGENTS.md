# Agent Guidelines - Maintenance

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Project maintenance utilities: dependency analysis, circular import detection, requirements consolidation, and deprecation management.

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

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `maintenance_health_check` | Run a simple health check and return its status | Safe |
| `maintenance_list_tasks` | List all registered maintenance tasks and their status | Safe |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
