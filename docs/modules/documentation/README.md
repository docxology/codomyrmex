# Documentation Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Documentation Module for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `scripts` | Documentation generation scripts. |


## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.documentation import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/documentation/](../../../src/codomyrmex/documentation/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k documentation -v
```
