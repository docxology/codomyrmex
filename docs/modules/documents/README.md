# Documents Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Documents Module for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `core` | Core document operations. |
| `formats` | Format-specific document handlers. |
| `metadata` | Document metadata operations. |
| `models` | Document data models. |
| `search` | Document search and indexing operations. |
| `transformation` | Document transformation operations. |
| `utils` | Document utilities. |


## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.documents import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |
| `tutorials/` | Tutorials |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k documents -v
```

## Navigation

- **Source**: [src/codomyrmex/documents/](../../../src/codomyrmex/documents/)
- **Parent**: [Modules](../README.md)
