# Agent Guidelines - Auth

## Module Overview

Authentication and authorization with OAuth, JWT, and API keys.

## Key Classes

- **Authenticator** — Multi-method authentication
- **APIKeyManager** — API key generation and validation
- **TokenManager** — JWT token handling
- **PermissionChecker** — Authorization checks

## Agent Instructions

1. **Validate all input** — Never trust user-provided tokens
2. **Use short expiry** — JWT tokens should expire quickly
3. **Rotate API keys** — Regularly rotate credentials
4. **Log auth events** — Use audit logging for auth
5. **Fail securely** — Generic error messages, log details

## Common Patterns

```python
from codomyrmex.auth import (
    Authenticator, APIKeyManager, TokenManager, requires_auth
)

# Authenticate request
auth = Authenticator()
user = auth.authenticate(request.headers.get("Authorization"))
if not user:
    raise AuthError("Invalid credentials")

# API key validation
keys = APIKeyManager()
if not keys.validate(api_key):
    raise AuthError("Invalid API key")

# JWT token management
tokens = TokenManager(secret="your-secret")
token = tokens.create(user_id=user.id, expires_in=3600)
claims = tokens.verify(token)

# Decorator for routes
@requires_auth(permissions=["read:data"])
def get_data():
    return data
```

## Testing Patterns

```python
# Verify token creation and verification
tokens = TokenManager(secret="test")
token = tokens.create(user_id="u1")
claims = tokens.verify(token)
assert claims["user_id"] == "u1"

# Verify API key validation
keys = APIKeyManager()
key = keys.generate()
assert keys.validate(key)
assert not keys.validate("invalid")
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
