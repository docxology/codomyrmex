# Model Context Protocol Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model Context Protocol Module for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `adapters` | MCP adapters submodule. |
| `discovery` | MCP Tool Discovery Module |
| `schemas` | Model Context Protocol schema definitions. |
| `validators` | MCP Schema Validators Module |


## Installation

```bash
pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.model_context_protocol import *  # See source for specific imports
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
uv run python -m pytest src/codomyrmex/tests/ -k model_context_protocol -v
```

## Related Modules

- [Exceptions](../exceptions/README.md)

## Navigation

- **Source**: [src/codomyrmex/model_context_protocol/](../../../src/codomyrmex/model_context_protocol/)
- **Parent**: [Modules](../README.md)
