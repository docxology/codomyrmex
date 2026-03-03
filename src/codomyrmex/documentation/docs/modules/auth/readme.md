# Auth

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Auth module provides authentication and authorization infrastructure for the codomyrmex platform, including API key management, OAuth integration, token-based authentication, token validation, and Role-Based Access Control (RBAC). It sits at the Core layer, providing security primitives consumed by API, cloud, and agent modules.

## Architecture Overview

```
auth/
├── __init__.py              # Public API (authenticate, authorize, get_authenticator)
├── core/
│   └── authenticator.py     # Authenticator singleton with authenticate/authorize
├── providers/
│   └── api_key_manager.py   # APIKeyManager for API key lifecycle
├── rbac/
│   └── permissions.py       # PermissionRegistry for RBAC
└── tokens/
    ├── token.py             # Token and TokenManager classes
    └── validator.py         # TokenValidator for token verification
```

## Key Classes and Functions

**`Authenticator`** -- Singleton authenticator with `authenticate(credentials)` and `authorize(token, resource, permission)`.

**`Token`** / **`TokenManager`** -- Token creation, storage, and lifecycle management.

**`APIKeyManager`** -- API key generation, validation, and revocation.

**`PermissionRegistry`** -- RBAC permission definitions and checks.

**`TokenValidator`** -- Token signature and expiration verification.

### Convenience Functions

- `authenticate(credentials: dict) -> Token | None`
- `authorize(token: Token | str, resource: str, permission: str) -> bool`
- `get_authenticator() -> Authenticator`

## Usage Examples

```python
from codomyrmex.auth import authenticate, authorize

token = authenticate({"api_key": "my-key"})
if token:
    allowed = authorize(token, "modules", "read")
```

## Related Modules

- [`api`](../api/readme.md) -- API authentication middleware integration
- [`security`](../security/readme.md) -- Security scanning and auditing
- [`encryption`](../encryption/readme.md) -- Cryptographic operations for token signing

## Navigation

- **Source**: [src/codomyrmex/auth/](../../../../src/codomyrmex/auth/)
- **Parent**: [All Modules](../README.md)
