# Pai Pm Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: April 2026

## Overview

Codomyrmex pai_pm module — PAI Project Manager server wrapper.

Agent coordination for this module: [AGENTS.md](AGENTS.md).

## Quick Start

```python
from codomyrmex.pai_pm import HAS_BUN, PaiPmServerManager

if HAS_BUN:
    manager = PaiPmServerManager()
    print(manager.is_running())
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/pai_pm/](../../../src/codomyrmex/pai_pm/)
- **Parent**: [Modules](../README.md)
