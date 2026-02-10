# Templating Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Templating module for Codomyrmex.

## Key Features

- **TemplatingError** — Raised when templating operations fail.
- `get_default_engine()` — Get or create default template engine instance.
- `render()` — Render a template string with context data.
- `render_file()` — Load and render a template file.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `context` | Context builders submodule. |
| `engines` | Template engine implementations. |
| `filters` | Template filters submodule. |
| `loaders` | Template loaders submodule. |

## Quick Start

```python
from codomyrmex.templating import TemplatingError

# Initialize
instance = TemplatingError()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `TemplatingError` | Raised when templating operations fail. |

### Functions

| Function | Description |
|----------|-------------|
| `get_default_engine()` | Get or create default template engine instance. |
| `render()` | Render a template string with context data. |
| `render_file()` | Load and render a template file. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |



## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k templating -v
```

## Related Modules

- [Exceptions](../exceptions/README.md)

## Navigation

- **Source**: [src/codomyrmex/templating/](../../../src/codomyrmex/templating/)
- **Parent**: [Modules](../README.md)
