# Codomyrmex Agents — src/codomyrmex/auth/tokens

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Token-based authentication with UUID token generation, HMAC-SHA256 signature verification, TTL-based expiry, revocation tracking, and token refresh (rotate).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `token.py` | `Token` | Dataclass representing an authentication token (token_id, user_id, permissions, expiry) |
| `token.py` | `TokenManager` | Creates, validates, revokes, and refreshes tokens using an internal store and revocation set |
| `validator.py` | `TokenValidator` | Signs token data with HMAC-SHA256 and verifies base64-encoded signed tokens |

## Operating Contracts

- `TokenManager.create_token` generates UUID-based tokens with configurable TTL (default 3600s).
- `TokenManager.validate_token` checks revocation set, expiry, and internal store.
- `TokenManager.refresh_token` creates a new token with the same permissions and revokes the old one.
- `TokenValidator.sign_token_data` produces base64-encoded JSON with HMAC-SHA256 signature.
- `TokenValidator.validate_signed_token` verifies signature using `hmac.compare_digest` (constant-time) and checks expiry.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config` (structured logging)
- **Used by**: `auth` parent module, API authentication, session management

## Navigation

- **Parent**: [auth](../README.md)
- **Root**: [Root](../../../../README.md)
