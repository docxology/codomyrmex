# Terminal Interface Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

This module provides interactive terminal interfaces and utilities for

## Submodules

| Submodule | Description |
|-----------|-------------|
| `commands` | Command registry submodule. |
| `completions` | Autocomplete submodule. |
| `rendering` | Output rendering submodule. |
| `shells` | Terminal shell management utilities. |
| `utils` | Terminal utilities submodule. |


## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.terminal_interface import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/terminal_interface/](../../../src/codomyrmex/terminal_interface/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k terminal_interface -v
```
