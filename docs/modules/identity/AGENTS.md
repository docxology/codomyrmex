# Identity Module — Agent Coordination

## Purpose

Identity Module.

## Key Capabilities

- Identity operations and management

## Agent Usage Patterns

```python
from codomyrmex.identity import *

# Agent uses identity capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/identity/](../../../src/codomyrmex/identity/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`BioCognitiveVerifier`** — Verifies identity based on behavioral biometrics.
- **`Identity`** — Main class for identity functionality.
- **`IdentityManager`** — Manages user personas and identity switching.
- **`VerificationLevel`** — Level of identity verification.
- **`Persona`** — Represents a distinct identity persona.
- **`create_identity()`** — Create a new Identity instance.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k identity -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
