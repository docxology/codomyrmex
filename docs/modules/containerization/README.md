# Containerization Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Containerization Module for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `docker` | Docker container management utilities. |
| `kubernetes` | Kubernetes submodule for containerization. |
| `registry` | Registry submodule for containerization. |
| `security` | Security submodule for containerization. |


## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.containerization import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/containerization/](../../../src/codomyrmex/containerization/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k containerization -v
```
