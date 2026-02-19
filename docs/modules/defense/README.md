# Defense Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Active countermeasures and containment strategies including rabbit hole detection, sandboxing, and threat response.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **ActiveDefense** — Active defense system against cognitive exploits.
- **Defense** — Main class for defense functionality.
- **RabbitHole** — A simulated environment to contain and waste the time of attackers.
- `create_defense()` — Create a new Defense instance.

## Quick Start

```python
from codomyrmex.defense import ActiveDefense, Defense, RabbitHole

instance = ActiveDefense()
```

## Source Files

- `active.py`
- `defense.py`
- `rabbithole.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k defense -v
```

## Navigation

- **Source**: [src/codomyrmex/defense/](../../../src/codomyrmex/defense/)
- **Parent**: [Modules](../README.md)
