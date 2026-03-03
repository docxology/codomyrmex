# Maintenance Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Maintenance module provides code health analysis, RASP documentation auditing, dependency management, and deprecation notice management for keeping the codomyrmex codebase healthy and well-documented.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | System health checks at cycle start; task queue inspection | `maintenance_health_check`, `maintenance_list_tasks` |
| **VERIFY** | Confirm system health post-execution before LEARN phase | `maintenance_health_check` |

PAI's OBSERVE phase opens with `maintenance_health_check` to confirm system health before processing begins. `maintenance_list_tasks` provides a pending task queue for PLAN phase awareness. QATester uses `maintenance_health_check` during VERIFY to confirm operational status.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

### Analysis

| Export | Type | Purpose |
|--------|------|---------|
| `analyze_code_quality` | Function | Code quality metrics (complexity, duplication, coverage) |
| `analyze_project_structure` | Function | Directory structure analysis |
| `generate_analysis_report` | Function | Generate comprehensive project report |

### Dependencies

| Export | Type | Purpose |
|--------|------|---------|
| `DependencyAnalyzer` | Class | Dependency graph analysis |
| `check_dependencies` | Function | Check for outdated or vulnerable dependencies |

### Health & Deprecation

| Export | Type | Purpose |
|--------|------|---------|
| `deps` | Module | Dependency management utilities |
| `health` | Module | Code health metrics and monitoring |
| `add_deprecation_notice` | Function | Add deprecation notices to functions |

## Quick Start

```python
from codomyrmex.maintenance import analyze_code_quality, DependencyAnalyzer, check_dependencies

# Analyze code quality
metrics = analyze_code_quality(path="src/codomyrmex/agents")

# Check dependencies
issues = check_dependencies()

# Analyze dependency graph
analyzer = DependencyAnalyzer()
graph = analyzer.analyze("src/codomyrmex")
```

## Architecture

```
maintenance/
├── __init__.py                      # All exports
├── analyze_project.py               # Code quality and structure analysis
├── add_deprecation_notices.py       # Deprecation notice management
├── deps/
│   ├── dependency_analyzer.py       # Dependency graph analysis
│   ├── dependency_checker.py        # Outdated dependency detection
│   └── dependency_consolidator.py   # Dependency consolidation
├── health/                          # Health metric tracking
└── tests/                           # Zero-Mock tests
```

## Navigation

- **Extended Docs**: [docs/modules/maintenance/](../../../docs/modules/maintenance/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
