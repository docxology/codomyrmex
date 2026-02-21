# Orchestrator Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

This module provides functionality for discovering, configuring, and running

## Submodules

| Submodule | Description |
|-----------|-------------|
| `engines` | Workflow engine implementations. |
| `monitors` | Execution Monitors submodule. |
| `pipelines` | Orchestrator Pipelines Module |
| `schedulers` | Task Schedulers submodule. |
| `state` | State Submodule |
| `templates` | Templates Submodule |
| `triggers` | Triggers Submodule |
| `workflows` | Workflow Definitions submodule. |

## Quick Start

```python
from codomyrmex.orchestrator import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k orchestrator -v
```

## Navigation

- **Source**: [src/codomyrmex/orchestrator/](../../../src/codomyrmex/orchestrator/)
- **Parent**: [Modules](../README.md)
