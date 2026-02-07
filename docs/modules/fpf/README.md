# FPF (Filesystem Processing Framework) Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

First Principles Framework (FPF) module.

## Key Features

- **FPFClient** — High-level client for working with FPF specifications.
- `load_from_file()` — Load and parse FPF specification from a local file.
- `fetch_and_load()` — Fetch latest FPF specification from GitHub and load it.
- `search()` — Search for patterns.
- `get_pattern()` — Get a pattern by ID.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `constraints` | Constraint Definitions submodule. |
| `models` | Domain Models submodule. |
| `optimization` | Constraint Optimization submodule. |
| `reasoning` | First Principles Framework reasoning utilities. |

## Quick Start

```python
from codomyrmex.fpf import FPFClient

# Initialize
instance = FPFClient()
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `FPFClient` | High-level client for working with FPF specifications. |

### Functions

| Function | Description |
|----------|-------------|
| `load_from_file()` | Load and parse FPF specification from a local file. |
| `fetch_and_load()` | Fetch latest FPF specification from GitHub and load it. |
| `search()` | Search for patterns. |
| `get_pattern()` | Get a pattern by ID. |
| `export_json()` | Export the specification to JSON. |
| `build_context()` | Build context string for prompt engineering. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/fpf/](../../../src/codomyrmex/fpf/)
- **Parent**: [Modules](../README.md)
