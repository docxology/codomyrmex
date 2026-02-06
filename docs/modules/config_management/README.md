# Config Management Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Configuration loading, validation, and environment management.

## Key Features

- **Multi-Source** — YAML, JSON, env vars
- **Layering** — defaults → file → env
- **Validation** — Schema validation
- **Secrets** — Secure secret handling

## Quick Start

```python
from codomyrmex.config_management import ConfigLoader

config = ConfigLoader.load(
    path="config.yaml",
    environment="production",
    env_prefix="APP_"
)

db_host = config.get("database.host")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/config_management/](../../../src/codomyrmex/config_management/)
- **Parent**: [Modules](../README.md)
