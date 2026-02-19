# Utilities Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Utilities Package.

## Key Features

- `ensure_directory()` — Ensure a directory exists, creating it if necessary.
- `safe_json_loads()` — Safely parse JSON with a fallback default.
- `safe_json_dumps()` — Safely serialize to JSON with fallback.
- `hash_content()` — Generate hash of content.

## Quick Start

```python
from codomyrmex.utils import ensure_directory, safe_json_loads, safe_json_dumps

# Use the module
result = ensure_directory()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Functions

| Function | Description |
|----------|-------------|
| `ensure_directory()` | Ensure a directory exists, creating it if necessary. |
| `safe_json_loads()` | Safely parse JSON with a fallback default. |
| `safe_json_dumps()` | Safely serialize to JSON with fallback. |
| `hash_content()` | Generate hash of content. |
| `hash_file()` | Generate hash of file contents. |
| `timing_decorator()` | Decorator to measure function execution time. |
| `retry()` | Decorator for retrying failed operations with exponential backoff. |
| `get_timestamp()` | Get current timestamp as formatted string. |
| `truncate_string()` | Truncate string to maximum length with suffix. |
| `get_env()` | Get environment variable with options. |
| `flatten_dict()` | Flatten a nested dictionary. |
| `deep_merge()` | Deep merge two dictionaries. |
| `wrapper()` | wrapper |
| `decorator()` | decorator |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k utils -v
```

## Navigation

- **Source**: [src/codomyrmex/utils/](../../../src/codomyrmex/utils/)
- **Parent**: [Modules](../README.md)
