# Scrape Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Scrape Module for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `firecrawl` | Firecrawl integration for the scrape module. |


## Installation

```bash
pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.scrape import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/scrape/](../../../src/codomyrmex/scrape/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k scrape -v
```
