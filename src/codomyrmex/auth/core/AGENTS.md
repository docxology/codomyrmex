# Codomyrmex Agents -- src/codomyrmex/auth/core

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides the central `Authenticator` class for user authentication and authorization. Supports API key authentication (via `APIKeyManager`), username/password authentication, role-based access control (via `PermissionRegistry`), and token lifecycle management (create, validate, refresh, revoke).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `authenticator.py` | `Authenticator` | Main authentication and authorization facade; delegates to `TokenManager`, `APIKeyManager`, and `PermissionRegistry` |
| `authenticator.py` | `AuthenticationError` | Exception raised when authentication fails (extends `CodomyrmexError`) |

## Operating Contracts

- `Authenticator.authenticate()` accepts a `credentials` dict with either `"api_key"` or `"username"` + `"password"` keys.
- Returns a `Token` on success, `None` on invalid credentials, raises `AuthenticationError` on unexpected errors.
- `Authenticator.authorize()` checks token validity first, then role-based permissions, then direct token permissions.
- `Authenticator.refresh_token()` returns a new `Token` or `None` if refresh fails.
- `Authenticator.revoke_token()` returns `True` on successful revocation.
- All authentication failures are logged as warnings; errors are logged at error level.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `auth.providers.api_key_manager.APIKeyManager`, `auth.rbac.permissions.PermissionRegistry`, `auth.tokens.token.Token` / `TokenManager`, `exceptions.CodomyrmexError`, `logging_monitoring.core.logger_config`
- **Used by**: API authentication middleware, any module requiring user identity verification

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../README.md](../../../README.md)
