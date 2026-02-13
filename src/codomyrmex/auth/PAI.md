# Personal AI Infrastructure — Auth Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Authentication module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.auth import Authenticator, Token, TokenManager, authenticate, authorize, get_authenticator
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Authenticator` | Class | Authenticator |
| `Token` | Class | Token |
| `TokenManager` | Class | Tokenmanager |
| `APIKeyManager` | Class | Apikeymanager |
| `PermissionRegistry` | Class | Permissionregistry |
| `TokenValidator` | Class | Tokenvalidator |
| `authenticate` | Function/Constant | Authenticate |
| `authorize` | Function/Constant | Authorize |
| `get_authenticator` | Function/Constant | Get authenticator |

## PAI Algorithm Phase Mapping

| Phase | Auth Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
