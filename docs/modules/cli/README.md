# CLI Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

This module provides the command-line interface for the Codomyrmex development platform.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `completions` | Shell Completions submodule. |
| `formatters` | CLI Output Formatters. |
| `handlers` | CLI command handlers. |
| `parsers` | Argument Parsers submodule. |
| `themes` | CLI Themes submodule. |


## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.cli import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/cli/](../../../src/codomyrmex/cli/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cli -v
```
