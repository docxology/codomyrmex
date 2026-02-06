# Plugin System Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Plugin discovery, loading, and lifecycle management.

## Key Features

- **Discovery** — Auto-discover plugins
- **Loading** — Dynamic plugin loading
- **Lifecycle** — Init, start, stop hooks
- **Registry** — Plugin registry

## Quick Start

```python
from codomyrmex.plugin_system import PluginManager, Plugin

manager = PluginManager()
manager.discover("./plugins/")
manager.load_all()

for plugin in manager.list():
    print(f"{plugin.name}: {plugin.version}")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/plugin_system/](../../../src/codomyrmex/plugin_system/)
- **Parent**: [Modules](../README.md)
