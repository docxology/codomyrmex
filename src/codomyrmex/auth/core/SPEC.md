# Auth Core -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Central authentication and authorization module providing credential validation, token management, and role-based access control through a unified `Authenticator` facade.

## Architecture

Facade pattern: `Authenticator` composes three collaborators -- `TokenManager` (token lifecycle), `APIKeyManager` (API key validation), and `PermissionRegistry` (RBAC). Authentication strategies are selected based on credential dict keys.

## Key Classes

### `AuthenticationError`

Extends `CodomyrmexError`. Raised when authentication encounters an unexpected error (not for simple invalid credentials, which return `None`).

### `Authenticator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `authenticate` | `credentials: dict` | `Token or None` | Authenticate via API key or username/password; returns `None` on invalid credentials |
| `authorize` | `token: Token, resource: str, permission: str` | `bool` | Check token validity and permission for a resource |
| `refresh_token` | `token: Token` | `Token or None` | Refresh an expired or expiring token |
| `revoke_token` | `token: Token` | `bool` | Revoke a token |

**Authentication strategies** (selected by credential dict keys):

| Key in `credentials` | Strategy |
|----------------------|----------|
| `"api_key"` | Validated via `APIKeyManager.validate_api_key()` |
| `"username"` + `"password"` | Validated against internal user store |

**Authorization flow** (checked in order):

1. Token validity via `TokenManager.validate_token()`
2. Role-based check via `PermissionRegistry.has_permission()`
3. Direct token permissions (including `"admin"` override)

## Dependencies

- **Internal**: `auth.providers.api_key_manager`, `auth.rbac.permissions`, `auth.tokens.token`, `exceptions.CodomyrmexError`, `logging_monitoring`
- **External**: None

## Constraints

- User store (`_users` dict) is in-memory only; a real implementation would connect to a database.
- Password comparison is plaintext (development only); production deployments must use hashed passwords.
- Zero-mock: real validation only, `AuthenticationError` for unexpected failures.

## Error Handling

- `AuthenticationError`: raised and logged at error level for unexpected authentication failures.
- Invalid credentials: logged at warning level, `None` returned (no exception).
- All errors logged before propagation.
