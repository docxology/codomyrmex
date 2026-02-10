# Website Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Website generation, static site building, and web content management utilities.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **DataProvider** — Aggregates data from various system modules to populate the website.
- **WebsiteGenerator** — Generates the static website.
- **WebsiteServer** — Enhanced HTTP server that supports API endpoints for dynamic functionality.

## Quick Start

```python
from codomyrmex.website import DataProvider, WebsiteGenerator, WebsiteServer

instance = DataProvider()
```

## Source Files

- `data_provider.py`
- `generator.py`
- `server.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |
| `tutorials/` | Tutorials |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k website -v
```

## Navigation

- **Source**: [src/codomyrmex/website/](../../../src/codomyrmex/website/)
- **Parent**: [Modules](../README.md)
