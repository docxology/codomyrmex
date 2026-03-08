# Auth -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Authentication
- `authenticate(credentials)` shall verify credentials and return a Token or None.
- Multiple credential types shall be supported (API key, OAuth, basic).

### FR-2: Authorization
- `authorize(token, resource, permission)` shall check RBAC permissions.
- The PermissionRegistry shall support hierarchical permission definitions.

### FR-3: Token Management
- Tokens shall have configurable expiration.
- TokenValidator shall verify token signatures and expiration.

### FR-4: API Key Management
- APIKeyManager shall support key generation, validation, rotation, and revocation.

## Interface Contracts

```python
def authenticate(credentials: dict[str, Any]) -> Token | None
def authorize(token: Token | str, resource: str, permission: str) -> bool
def get_authenticator() -> Authenticator
```

## Navigation

- **Source**: [src/codomyrmex/auth/](../../../../src/codomyrmex/auth/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
