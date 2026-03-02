# api/authentication — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The authentication submodule provides a strategy pattern for API request authentication. Six authentication types are supported through concrete implementations of the `Authenticator` ABC.

## Architecture

All types and implementations reside in `__init__.py` (~427 lines). The module is self-contained with no external dependencies.

```
authentication/
├── __init__.py    # All enums, dataclasses, authenticators, and factory
```

## Key Classes

### AuthType (Enum)

| Member | Value | Description |
|--------|-------|-------------|
| `API_KEY` | `"api_key"` | Static API key validation |
| `BEARER_TOKEN` | `"bearer_token"` | Token-based auth with custom verifier |
| `BASIC_AUTH` | `"basic_auth"` | Username/password pairs |
| `OAUTH2` | `"oauth2"` | OAuth 2.0 token validation |
| `HMAC` | `"hmac"` | HMAC signature verification |
| `JWT` | `"jwt"` | JSON Web Token validation |

### AuthCredentials (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `auth_type` | `AuthType` | Which authentication strategy to use |
| `value` | `str` | The credential value (key, token, signature, etc.) |
| `metadata` | `dict[str, Any]` | Optional extra data (e.g., username for basic auth) |

### AuthResult (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `authenticated` | `bool` | Whether authentication succeeded |
| `user_id` | `str \| None` | Identified user on success |
| `roles` | `list[str]` | Roles/permissions associated with the user |
| `error` | `str \| None` | Error message on failure |

### Authenticator (ABC)

| Method | Signature | Description |
|--------|-----------|-------------|
| `authenticate` | `(credentials: AuthCredentials) -> AuthResult` | Validate credentials and return result |

### Concrete Authenticators

| Class | Constructor Args | Behaviour |
|-------|-----------------|-----------|
| `APIKeyAuthenticator` | `keys: dict[str, str]` | Looks up `credentials.value` in `keys` dict |
| `BearerTokenAuthenticator` | `verify: Callable[[str], dict \| None]` | Calls `verify(token)` callable; returns user info dict or None |
| `BasicAuthenticator` | `users: dict[str, str]` | Matches username (from metadata) + password against `users` dict |
| `HMACAuthenticator` | `secret: str` | Verifies HMAC signature in `credentials.value` against expected |

### Factory Function

```python
def create_authenticator(auth_type: AuthType, **kwargs) -> Authenticator
```

Returns the matching `Authenticator` implementation based on `auth_type`. Raises `ValueError` for unsupported types.

## Error Handling

- Invalid `auth_type` in factory: raises `ValueError`.
- Authentication failure: returns `AuthResult(authenticated=False, error="...")`.
- Authenticators never raise on bad credentials; they return a failed `AuthResult`.

## Dependencies

- Python standard library only (no third-party packages).

## Navigation

- **Parent**: [api/SPEC.md](../SPEC.md)
- **Sibling**: [AGENTS.md](AGENTS.md) | [README.md](README.md)
