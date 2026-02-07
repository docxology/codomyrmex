# Static Analysis Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Static Analysis Module for Codomyrmex.


## Installation

```bash
pip install codomyrmex
```

## Key Features

- `analyze_codebase()` — Alias for analyze_project for backward compatibility.
- `analyze_code_quality()` — Analyze code quality for workflow integration.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `complexity` | Static Analysis Complexity Module |
| `linting` | Static Analysis Linting Module |

## Quick Start

```python
from codomyrmex.static_analysis import analyze_codebase, analyze_code_quality

# Use the module
result = analyze_codebase()
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
uv run python -m pytest src/codomyrmex/tests/ -k static_analysis -v
```

## Navigation

- **Source**: [src/codomyrmex/static_analysis/](../../../src/codomyrmex/static_analysis/)
- **Parent**: [Modules](../README.md)
