# Cloud Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cloud Services Module for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `aws` | AWS integration submodule. |
| `azure` | Azure integration submodule. |
| `coda_io` | Coda.io API Client Submodule. |
| `common` | Cloud common utilities. |
| `gcp` | GCP integration submodule. |
| `infomaniak` | Infomaniak Public Cloud Integration. |


## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.cloud import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/cloud/](../../../src/codomyrmex/cloud/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cloud -v
```
