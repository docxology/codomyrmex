# System Discovery Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Introspection and discovery of system components and services.

## Key Features

- **Services** — Discover services
- **Health** — Health checks
- **Inventory** — System inventory
- **Topology** — Service topology

## Quick Start

```python
from codomyrmex.system_discovery import SystemScanner

scanner = SystemScanner()
services = scanner.discover_services()

for svc in services:
    health = scanner.health_check(svc)
    print(f"{svc.name}: {health.status}")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/system_discovery/](../../../src/codomyrmex/system_discovery/)
- **Parent**: [Modules](../README.md)
