# Identity Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Persona management and bio-cognitive verification for agent identity and authentication.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **BioCognitiveVerifier** — Verifies identity based on behavioral biometrics.
- **Identity** — Main class for identity functionality.
- **IdentityManager** — Manages user personas and identity switching.
- **VerificationLevel** — Level of identity verification.
- **Persona** — Represents a distinct identity persona.
- `create_identity()` — Create a new Identity instance.

## Quick Start

```python
from codomyrmex.identity import BioCognitiveVerifier, Identity, IdentityManager

instance = BioCognitiveVerifier()
```

## Source Files

- `biocognitive.py`
- `identity.py`
- `manager.py`
- `persona.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k identity -v
```

## Navigation

- **Source**: [src/codomyrmex/identity/](../../../src/codomyrmex/identity/)
- **Parent**: [Modules](../README.md)
