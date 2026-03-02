# Agent Guidelines - Auth

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Authentication and authorization with OAuth, JWT, and API keys.

## Key Components

| Component | Description |
|-----------|-------------|
| `Authenticator` | Main entry point for auth and authorization logic |
| `PermissionRegistry` | Role-based Access Control (RBAC) manager |
| `TokenManager` | Lifecycle management for authentication tokens |
| `APIKeyManager` | Secure generation and validation of API keys |

## Usage for Agents

### Authentication

```python
from codomyrmex.auth import Authenticator

auth = Authenticator()
# Authenticate with credentials
token = auth.authenticate({"username": "agent_alpha", "password": "secure_password"})

if token:
    # Check authorization for a specific permission
    is_allowed = auth.authorize(token, resource="secure_data", permission="read")
```

### RBAC Management

```python
from codomyrmex.auth.rbac import PermissionRegistry

rbac = PermissionRegistry()
rbac.register_role("editor", ["read", "write"])
rbac.add_inheritance("admin", "editor")
rbac.register_role("admin", ["delete"])

# Admin inherits read and write
has_perm = rbac.has_permission("admin", "write") # True
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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Authentication providers, token management, credential handling | TRUSTED |
| **Architect** | Read + Design | Auth strategy review, security model design, token lifecycle analysis | OBSERVED |
| **QATester** | Validation | Auth flow validation, token expiry testing, credential security verification | OBSERVED |

### Engineer Agent
**Use Cases**: Configuring authentication during BUILD, managing credentials during EXECUTE.

### Architect Agent
**Use Cases**: Reviewing authentication strategies, designing security models, planning OAuth/JWT flows.

### QATester Agent
**Use Cases**: Validating authentication flows during VERIFY, testing token handling and expiry.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
