# Privacy Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Data sanitization via crumb cleaning and anonymous routing via mixnet patterns.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **CrumbCleaner** — Sanitizes data by removing tracking crumbs and metadata.
- **Packet** — Packet
- **MixNode** — A single node in the mixnet overlay.
- **MixnetProxy** — Manages anonymous routing through the mixnet.
- **Privacy** — Main class for privacy functionality.
- `create_privacy()` — Create a new Privacy instance.

## Quick Start

```python
from codomyrmex.privacy import CrumbCleaner, Packet, MixNode

instance = CrumbCleaner()
```

## Source Files

- `crumbs.py`
- `mixnet.py`
- `privacy.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k privacy -v
```

## Navigation

- **Source**: [src/codomyrmex/privacy/](../../../src/codomyrmex/privacy/)
- **Parent**: [Modules](../README.md)
