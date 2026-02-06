# Personal AI Infrastructure — System Discovery Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The System Discovery module provides PAI integration for system introspection.

## PAI Capabilities

### Service Discovery

Find running services:

```python
from codomyrmex.system_discovery import SystemScanner

scanner = SystemScanner()
services = scanner.discover_services()

for svc in services:
    print(f"{svc.name}: {svc.port}")
```

### Health Checks

Check service health:

```python
from codomyrmex.system_discovery import SystemScanner

scanner = SystemScanner()
health = scanner.health_check("api_server")
print(f"Status: {health.status}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `SystemScanner` | Discover services |
| `health_check` | Check health |
| `Inventory` | System inventory |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
