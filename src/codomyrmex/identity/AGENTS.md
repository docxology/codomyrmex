# Identity Module - Agent Guide

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Secure Cognitive Agent module handling all identity-related operations. Ensures actions can be attributed to specific, verifiable personas without leaking the underlying user's true identity unless explicitly authorized.

## Key Components

| Component | Description |
|-----------|-------------|
| `IdentityManager` | 3-tier persona management (Blue/Grey/Black) |
| `BioCognitiveVerifier` | Behavioral and biometric verification |
| `Persona` | Individual identity container |
| `RevocationManager` | Credential revocation handling |

## Active Files

- `__init__.py` - Module initialization and exports
- `manager.py` - Core persona management
- `biocognitive.py` - Bio-cognitive verification
- `identity.py` - Base identity class
- `README.md` - Human documentation
- `SPEC.md` - Functional specification

## Usage for Agents

### Persona Management

```python
from codomyrmex.identity import IdentityManager, VerificationLevel

manager = IdentityManager()
# Create a high-trust persona
p_kyc = manager.create_persona("p_legal", "Legal Identity", VerificationLevel.KYC)

# Switch context
manager.set_active_persona("p_legal")
```

### Verification

```python
from codomyrmex.identity import BioCognitiveVerifier

verifier = BioCognitiveVerifier()
# Verify user based on behavioral patterns
is_valid = verifier.verify(user_id="u1", metric="keystroke", current_value=0.15)
```

## Agent Guidelines

1. **Privacy First**: Never log or expose persona mappings
2. **Verification**: Always verify before sensitive operations
3. **Tier Awareness**: Respect persona tier limitations

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent**: [codomyrmex/](../README.md)
- **🏠 Root**: [../../../README.md](../../../README.md)
- **🔗 Related**: [wallet/](../wallet/) | [defense/](../defense/) | [privacy/](../privacy/)
