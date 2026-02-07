# Auth Module

**Version**: v0.1.0 | **Status**: Active

Authentication with API keys, tokens, OAuth, and access control.


## Installation

```bash
pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Functions
- **`authenticate()`** — Authenticate with credentials.
- **`authorize()`** — Check if token has permission.
- **`get_authenticator()`** — Get an authenticator instance.

## Quick Start

```python
from codomyrmex.auth import (
    authenticate, authorize, Authenticator, Token, APIKeyManager
)

# Authenticate with credentials
token = authenticate({"username": "user", "password": "secret"})
if token:
    print(f"Authenticated: {token.user_id}, expires: {token.expires_at}")

# Check authorization
if authorize(token, resource="documents", permission="write"):
    save_document()

# API key management
key_manager = APIKeyManager()
api_key = key_manager.create(user_id="user-123", scopes=["read", "write"])
print(f"API Key: {api_key.key}")

# Validate API key
is_valid = key_manager.validate(api_key.key)
key_manager.revoke(api_key.key)
```

## Token Management

```python
from codomyrmex.auth import TokenManager, TokenValidator

manager = TokenManager(secret="your-secret")
token = manager.create(user_id="user-123", roles=["admin"])

validator = TokenValidator(secret="your-secret")
claims = validator.validate(token.jwt)
```

## Exports

| Class | Description |
|-------|-------------|
| `Authenticator` | Main authentication handler |
| `Token` | JWT token with claims |
| `TokenManager` | Create and refresh tokens |
| `TokenValidator` | Validate and decode tokens |
| `APIKeyManager` | API key CRUD operations |
| `PermissionRegistry` | Define and check permissions |
| `authenticate(creds)` | Authenticate with credentials |
| `authorize(token, res, perm)` | Check permission |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k auth -v
```


## Documentation

- [Module Documentation](../../../docs/modules/auth/README.md)
- [Agent Guide](../../../docs/modules/auth/AGENTS.md)
- [Specification](../../../docs/modules/auth/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
