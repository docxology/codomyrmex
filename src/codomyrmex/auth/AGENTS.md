# Agent Guidelines - Auth

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Authentication and authorization with signed tokens, API keys, and Role-Based Access Control (RBAC).

## Key Components

| Component | Description |
|-----------|-------------|
| `Authenticator` | Main singleton entry point for authentication and authorization. |
| `PermissionRegistry` | Manages role-based and resource-based access control. |
| `TokenManager` | Lifecycle and secure signing (HMAC-SHA256) for authentication tokens. |
| `APIKeyManager` | Secure generation, validation, and rotation of API keys. |

## Usage for Agents

### Authentication and User Management

```python
from codomyrmex.auth import Authenticator

auth = Authenticator()

# 1. Register a user (typically done during BUILD phase)
auth.register_user("agent_alpha", "secure_password", roles=["editor"])

# 2. Authenticate with credentials (during EXECUTE phase)
token = auth.authenticate({"username": "agent_alpha", "password": "secure_password"})

if token:
    # 3. Check authorization (using signed token)
    is_allowed = auth.authorize(token, resource="secure_data", permission="read")
    # or using signed token string (JWT)
    is_allowed = auth.authorize(token.jwt, resource="secure_data", permission="read")
```

### RBAC Management

```python
# During setup (OBSERVE/BUILD)
auth.permissions.register_role("reader", ["data.read"])
auth.permissions.register_role("editor", ["data.write"])
auth.permissions.add_inheritance("editor", "reader")

# Assign role to user
auth.permissions.assign_role("agent_alpha", "editor")

# Check permission
has_perm = auth.permissions.check("agent_alpha", "data.read")  # True via inheritance
```

### API Key Management

```python
# Generate an API key for persistent access
api_key = auth.api_key_manager.generate("agent_alpha", permissions=["data.read"])

# Authenticate with API key
token = auth.authenticate({"api_key": api_key})
```

## Testing Patterns

**Strict Zero-Mock Testing**: Always use real `Authenticator`, `TokenManager`, and `PermissionRegistry` objects in tests to ensure that the integrated behavior (signing, verification, inheritance) is correctly validated.

```python
# Verify token roundtrip
from codomyrmex.auth import Authenticator
auth = Authenticator()
token = auth.token_manager.create_token(user_id="test")
assert auth.token_manager.validate_token(token.jwt)
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/auth.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/auth.cursorrules)
