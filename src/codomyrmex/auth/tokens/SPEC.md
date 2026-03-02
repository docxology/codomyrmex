# Tokens — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Token authentication with two layers: `TokenManager` for token lifecycle (create, validate, revoke, refresh) and `TokenValidator` for cryptographic signing and verification via HMAC-SHA256.

## Architecture

Two-class design: `TokenManager` manages the token lifecycle using an in-memory store and revocation set, while `TokenValidator` handles cryptographic signing and verification of base64-encoded token payloads.

## Key Classes

### `TokenManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_token` | `user_id: str, permissions: list[str], ttl: int` | `Token` | Create a UUID token with permissions and TTL |
| `validate_token` | `token: Token` | `bool` | Check revocation, expiry, and store membership |
| `revoke_token` | `token: Token` | `bool` | Add to revocation set and remove from store |
| `refresh_token` | `token: Token, ttl: int` | `Token \| None` | Create new token with same permissions, revoke old |

Constructor: `secret: str | None = None`

### `Token` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `token_id` | `str` | UUID identifier |
| `user_id` | `str` | Token owner |
| `permissions` | `list[str]` | Granted permissions |
| `expires_at` | `float \| None` | Expiry timestamp |
| `secret` | `str \| None` | Optional signing secret |

Methods: `is_expired() -> bool`, `to_dict() -> dict`, `from_dict(data) -> Token`

### `TokenValidator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `sign_token_data` | `token_data: dict` | `str` | Sign data with HMAC-SHA256 and return base64-encoded token |
| `validate_signed_token` | `token_str: str` | `dict \| None` | Decode, verify signature and expiry; returns data or `None` |

Constructor: `secret: str` (encoded to bytes internally)

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: Standard library (`uuid`, `time`, `hmac`, `hashlib`, `json`, `base64`)

## Constraints

- Tokens are stored in-memory; no persistence.
- Signature verification uses `hmac.compare_digest` for constant-time comparison.
- `refresh_token` returns `None` if the old token fails validation.
- Default secret is `"default_secret_change_in_production"` -- must be overridden.
- Zero-mock: real HMAC signatures only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `validate_signed_token` catches all exceptions and returns `None` (logs errors).
- Signature mismatches logged at WARNING level.
- Token expiry logged at WARNING level.
