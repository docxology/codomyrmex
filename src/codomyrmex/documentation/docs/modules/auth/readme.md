# Auth Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

Authentication with API keys, signed tokens, OAuth, and Role-Based Access Control (RBAC).

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Check authentication state and token validity | Direct Python import |
| **EXECUTE** | Authenticate users, register users, and issue tokens | Direct Python import |
| **VERIFY** | Validate tokens, sessions, and API key permissions | Direct Python import |

## Key Features

- **Singleton Authenticator**: Maintains shared state across the application.
- **User Registration**: Support for local user management with integrated RBAC.
- **Signed Tokens**: JWT-like signed tokens for secure, verifiable authentication.
- **Granular RBAC**: Role hierarchy, wildcard permissions, and audit logging.
- **API Key Management**: Secure generation, validation, and rotation of API keys.

## Quick Start

```python
from codomyrmex.auth import Authenticator

auth = Authenticator()

# 1. Setup Permissions
auth.permissions.register_role("editor", ["documents.read", "documents.write"])
auth.permissions.add_inheritance("admin", "editor")
auth.permissions.register_role("admin", ["*"])

# 2. Register and Authenticate
auth.register_user("alice", "secret_password", roles=["editor"])
token = auth.authenticate({"username": "alice", "password": "secret_password"})

# 3. Authorize
if auth.authorize(token, resource="doc123", permission="documents.read"):
    print("Authorized!")

# 4. API Keys
api_key = auth.api_key_manager.generate(user_id="alice", permissions=["documents.read"])
token_from_key = auth.authenticate({"api_key": api_key})
```

## Exports

| Class | Description |
|-------|-------------|
| `Authenticator` | Main singleton entry point |
| `PermissionRegistry` | RBAC manager |
| `TokenManager` | Lifecycle and signing of tokens |
| `APIKeyManager` | API key lifecycle management |

## Testing

```bash
pytest src/codomyrmex/tests/unit/auth/
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
