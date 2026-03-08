# Identity Module - Agent Guide

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Secure Cognitive Agent module handling all identity-related operations. Ensures actions can be attributed to specific, verifiable personas without leaking the underlying user's true identity unless explicitly authorized. Supports a 3-tier trust model (Blue/Grey/Black) and behavioral biometric verification via Z-score statistical analysis. The `Identity` class orchestrates pluggable authentication providers (password, token, bio-cognitive), session management with expiry and refresh, and audit logging. The `IdentityManager` manages the persona registry and active context switching, while `BioCognitiveVerifier` uses keystroke dynamics and decision latency baselines for continuous identity verification.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `Persona`, `VerificationLevel`, `IdentityManager`, `BioCognitiveVerifier`, `cli_commands` |
| `identity.py` | `Identity` orchestrator with session management, pluggable `AuthProvider` backends (`PasswordProvider`, `TokenProvider`), `AuthToken`, `AuthEvent` audit log |
| `manager.py` | `IdentityManager` -- persona registry, active persona switching, create/register/revoke/promote/export operations |
| `persona.py` | `Persona` dataclass (id, name, level, attributes, crumbs, capabilities) and `VerificationLevel` enum |
| `biocognitive.py` | `BioCognitiveVerifier` -- Z-score behavioral verification, metric recording, enrollment, confidence scoring |

## Key Classes

- **Identity** -- Top-level orchestrator with pluggable auth providers, session tokens with TTL, scope-based access, and event auditing (`login()`, `logout()`, `validate_token()`, `refresh_token()`, `register_provider()`, `process()`)
- **IdentityManager** -- Persona registry and context switcher (`create_persona()`, `register_persona()`, `set_active_persona()`, `get_persona()`, `list_personas()`, `revoke_persona()`, `promote_persona()`, `export_persona()`)
- **Persona** -- Dataclass representing a distinct identity with id, name, level, attributes, crumbs, and capabilities (`add_attribute()`, `add_crumb()`, `add_capability()`, `has_capability()`, `to_dict()`)
- **VerificationLevel** -- Enum with tiers: `UNVERIFIED`, `ANON` (grey), `VERIFIED_ANON` (black), `KYC` (blue)
- **BioCognitiveVerifier** -- Statistical behavioral verification using Z-score analysis (`record_metric()`, `verify()`, `enroll()`, `get_confidence()`, `create_challenge()`)
- **AuthProvider** -- Abstract base class for pluggable authentication backends (`authenticate()`)
- **PasswordProvider** -- Password-based auth using salted SHA-256 hashing (`register()`, `authenticate()`)
- **TokenProvider** -- API-key/bearer token auth (`create_token()`, `revoke_token()`, `authenticate()`)
- **AuthToken** -- Dataclass for session tokens with expiry (`is_expired`, `remaining_seconds`)
- **AuthEvent** -- Dataclass for audit log entries (user_id, event_type, timestamp, metadata)

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

### Session Authentication

```python
from codomyrmex.identity.identity import Identity, PasswordProvider

ident = Identity()
pw = PasswordProvider()
pw.register("alice", "s3cret")
ident.register_provider("password", pw)

token = ident.login("alice", {"user_id": "alice", "password": "s3cret"}, provider="password")
assert token is not None
assert ident.validate_token(token.token)
ident.logout(token.token)
```

## Agent Guidelines

1. **Privacy First**: Never log or expose persona mappings.
2. **Verification**: Always verify before sensitive operations using `BioCognitiveVerifier`.
3. **Tier Awareness**: Respect persona tier limitations (KYC vs. Anonymous).
4. **Context Maintenance**: Use `IdentityManager.set_active_persona()` to maintain correct context.
5. **Session Hygiene**: Always call `logout()` when sessions are no longer needed.
6. **Provider Registration**: Register auth providers before calling `login()`.

## Operating Contracts

- `IdentityManager.create_persona()` raises `ValueError` if a persona with the same ID already exists
- `IdentityManager.register_persona()` raises `ValueError` if a persona with the same ID already exists
- `IdentityManager.set_active_persona()` raises `ValueError` if the persona ID is not found in the registry
- `Identity.login()` returns `None` (not an exception) if the provider is unknown or credentials are invalid
- `Identity.validate_token()` returns `False` and evicts the session if the token is expired
- `Identity.refresh_token()` returns `None` if the old token is expired or not found
- `BioCognitiveVerifier.verify()` returns `False` if no baseline exists for the user/metric pair
- `BioCognitiveVerifier.verify()` returns `True` during enrollment phase (fewer than 10 samples)
- `BioCognitiveVerifier` keeps a sliding window of the last 100 samples per user/metric
- `Persona.to_dict()` exports `crumbs_count` (integer) instead of raw crumbs data for privacy
- **DO NOT** expose raw crumbs or persona-to-user mappings in logs or API responses
- **DO NOT** bypass `BioCognitiveVerifier` for sensitive operations in production

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Identity management, persona lifecycle, credential provisioning, session management | TRUSTED |
| **Architect** | Read + Design | Identity architecture review, IAM design, federation strategy | OBSERVED |
| **QATester** | Validation | Identity verification testing, credential validation, access control verification | OBSERVED |
| **Researcher** | Read-only | Inspect persona metadata via `export_persona()`, review audit logs, query confidence scores | SAFE |

### Engineer Agent
**Use Cases**: Managing identities during BUILD/EXECUTE, provisioning service credentials, promoting personas, configuring auth providers, managing session lifecycles.

### Architect Agent
**Use Cases**: Designing IAM strategies, reviewing identity federation, planning access control, evaluating verification level tier structure.

### QATester Agent
**Use Cases**: Verifying identity management correctness during VERIFY, testing access control boundaries, validating bio-cognitive verification accuracy, testing session expiry and token refresh flows.

### Researcher Agent
**Use Cases**: Inspecting persona metadata via `export_persona()` and `list_personas()`, reviewing audit logs for authentication event analysis, querying `get_confidence()` scores for behavioral verification research.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/identity.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/identity.cursorrules)
