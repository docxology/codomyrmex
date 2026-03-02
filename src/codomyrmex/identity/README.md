# Identity Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Persona management and bio-cognitive verification for agent identity.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Verify identity claims and inspect persona states | Direct Python import |
| **EXECUTE** | Identity operations including registration and promotion | Direct Python import |
| **VERIFY** | Validate identity assertions via bio-cognitive challenges | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The QATester agent uses BioCognitiveVerifier during VERIFY to validate agent authenticity, while the Engineer agent manages persona lifecycle during EXECUTE.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`BioCognitiveVerifier`** — Verifies identity based on behavioral biometrics.
- **`Identity`** — Main class for identity functionality.
- **`IdentityManager`** — Manages user personas and identity switching.
- **`VerificationLevel`** — Level of identity verification.
- **`Persona`** — Represents a distinct identity persona.

### Functions
- **`create_identity()`** — Create a new Identity instance.

## Quick Start

```python
from codomyrmex.identity import (
    Persona, VerificationLevel, IdentityManager, BioCognitiveVerifier
)

# Create and manage personas
manager = IdentityManager()

persona = Persona(
    id="agent-001",
    name="ResearchAssistant",
    capabilities=["search", "summarize", "cite"],
    trust_level=VerificationLevel.VERIFIED
)

manager.register(persona)
active = manager.get("agent-001")

# Bio-cognitive verification
verifier = BioCognitiveVerifier()

# Challenge-response verification
challenge = verifier.create_challenge(persona)
response = agent.respond_to_challenge(challenge)
is_authentic = verifier.verify(persona, response)

# Update trust level based on verification
if is_authentic:
    manager.promote("agent-001", VerificationLevel.TRUSTED)
```

## Exports

| Class | Description |
|-------|-------------|
| `Persona` | Agent identity with capabilities |
| `VerificationLevel` | Enum: unverified, verified, trusted |
| `IdentityManager` | Register and manage personas |
| `BioCognitiveVerifier` | Challenge-response authentication |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k identity -v
```

## Documentation

- [Module Documentation](../../../docs/modules/identity/README.md)
- [Agent Guide](../../../docs/modules/identity/AGENTS.md)
- [Specification](../../../docs/modules/identity/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
