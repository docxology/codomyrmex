# Tools Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tool calling framework with registration, validation, execution, and composable tool chains.


## Installation

```bash
pip install codomyrmex
```

## Key Features

- **DependencyAnalyzer** — Analyzes module dependencies for circular imports and hierarchy violations.
- `get_module_name()` — Extract module name from file path.
- `get_dependency_location()` — Determine where dependencies are located in pyproject.toml.
- `add_deprecation_notice()` — Add deprecation notice to requirements.txt file.
- `main()` — Main function.

## Quick Start

```python
from codomyrmex.tools import DependencyAnalyzer

instance = DependencyAnalyzer()
```

## Source Files

- `add_deprecation_notices.py`
- `analyze_project.py`
- `dependency_analyzer.py`
- `dependency_checker.py`
- `dependency_consolidator.py`
- `validate_dependencies.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tools -v
```

## Navigation

- **Source**: [src/codomyrmex/tools/](../../../src/codomyrmex/tools/)
- **Parent**: [Modules](../README.md)
