# Identity Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

Persona management and bio-cognitive verification for agent identity.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Verify identity claims and inspect persona states | `IdentityManager.get_persona()` |
| **EXECUTE** | Identity operations including registration and promotion | `IdentityManager.create_persona()` |
| **VERIFY** | Validate identity assertions via bio-cognitive challenges | `BioCognitiveVerifier.verify()` |

PAI agents access this module via direct Python import through the MCP bridge. The QATester agent uses `BioCognitiveVerifier` during VERIFY to validate agent authenticity, while the Engineer agent manages persona lifecycle during EXECUTE.

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
- **`Identity`** — High-level orchestrator with session and audit logging.
- **`IdentityManager`** — Manages user personas and identity switching.
- **`VerificationLevel`** — Enum: UNVERIFIED, ANON, VERIFIED_ANON, KYC.
- **`Persona`** — Represents a distinct identity persona.

### Functions
- **`create_identity()`** — Create a new `Identity` instance.

## Quick Start

```python
from codomyrmex.identity import (
    Persona, VerificationLevel, IdentityManager, BioCognitiveVerifier
)

# 1. Create and manage personas
manager = IdentityManager()

persona = manager.create_persona(
    id="agent-001",
    name="ResearchAssistant",
    level=VerificationLevel.ANON,
    capabilities=["search", "summarize", "cite"]
)

manager.set_active_persona("agent-001")
active = manager.active_persona

# 2. Bio-cognitive verification
verifier = BioCognitiveVerifier()

# Record 20+ samples for a reliable baseline
for sample in [0.12, 0.11, 0.13, 0.12, 0.12] * 4:
    verifier.record_metric("agent-001", "keystroke_flight_time", sample)

# Check confidence
confidence = verifier.get_confidence("agent-001")

# Verify current behavior
is_authentic = verifier.verify("agent-001", "keystroke_flight_time", 0.125)

# Update trust level based on verification
if is_authentic and confidence > 0.8:
    manager.promote_persona("agent-001", VerificationLevel.VERIFIED_ANON)
```

## API Exports

| Class | Description |
|-------|-------------|
| `Persona` | Agent identity with capabilities, crumbs, and trust level |
| `VerificationLevel` | 3-tier trust model (Anon, Verified Anon, KYC) |
| `IdentityManager` | Register, switch, and promote personas |
| `BioCognitiveVerifier` | Statistical behavioral biometric verification |
| `Identity` | Orchestrator with session TTL and audit logs |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/identity/ -v
```

## Documentation

- [Module Documentation](../../../docs/modules/identity/README.md)
- [Agent Guide](AGENTS.md)
- [Specification](SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
