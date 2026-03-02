# Identity Module - Agent Guide

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Secure Cognitive Agent module handling all identity-related operations. Ensures actions can be attributed to specific, verifiable personas without leaking the underlying user's true identity unless explicitly authorized. Supports a 3-tier trust model and behavioral biometric verification.

## Key Components

| Component | Description |
|-----------|-------------|
| `IdentityManager` | 3-tier persona management (Blue/Grey/Black) |
| `BioCognitiveVerifier` | Behavioral and biometric verification (Z-score based) |
| `Persona` | Individual identity container with capabilities and crumbs |
| `Identity` | High-level orchestrator for sessions and audit logging |

## Active Files

- `__init__.py` - Module initialization and exports
- `manager.py` - Core persona management
- `biocognitive.py` - Bio-cognitive verification
- `persona.py` - Persona data structure
- `identity.py` - Base identity class and session management
- `README.md` - Human documentation
- `SPEC.md` - Functional specification

## Usage for Agents

### Persona Management

```python
from codomyrmex.identity import IdentityManager, VerificationLevel

manager = IdentityManager()
# Create a high-trust persona (Blue Tier)
p_kyc = manager.create_persona("p_legal", "Legal Identity", VerificationLevel.KYC)

# Switch context
manager.set_active_persona("p_legal")
```

### Bio-Cognitive Verification

```python
from codomyrmex.identity import BioCognitiveVerifier

verifier = BioCognitiveVerifier()
# Record user pattern (training phase)
for i in range(20):
    verifier.record_metric(user_id="u1", metric="keystroke_flight_time", value=0.12)

# Verify user based on behavioral patterns
is_valid = verifier.verify(user_id="u1", metric="keystroke_flight_time", current_value=0.13)
# Outlier detection
is_invalid = verifier.verify(user_id="u1", metric="keystroke_flight_time", current_value=0.50)
```

## Agent Guidelines

1. **Privacy First**: Never log or expose persona mappings.
2. **Verification**: Always verify before sensitive operations using `BioCognitiveVerifier`.
3. **Tier Awareness**: Respect persona tier limitations (KYC vs. Anonymous).
4. **Context Maintenance**: Use `IdentityManager.set_active_persona()` to maintain correct context.

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry (audit logs) and update TODO queues when necessary.

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Identity management, persona lifecycle, credential provisioning | TRUSTED |
| **Architect** | Read + Design | Identity architecture review, IAM design, federation strategy | OBSERVED |
| **QATester** | Validation | Identity verification testing, credential validation, access control verification | OBSERVED |

### Engineer Agent
**Use Cases**: Managing identities during BUILD/EXECUTE, provisioning service credentials, promoting personas.

### Architect Agent
**Use Cases**: Designing IAM strategies, reviewing identity federation, planning access control.

### QATester Agent
**Use Cases**: Verifying identity management correctness during VERIFY, testing access control boundaries, validating bio-cognitive performance.

## Navigation Links

- **📁 Parent**: [codomyrmex/](../README.md)
- **🏠 Root**: [../../../README.md](../../../README.md)
- **🔗 Related**: [wallet/](../wallet/) | [defense/](../defense/) | [privacy/](../privacy/)
