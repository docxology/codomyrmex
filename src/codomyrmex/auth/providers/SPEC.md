# Auth Providers — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

API key management provider supporting key generation with configurable prefix and entropy, TTL-based expiry, per-key rate limits, key rotation, and bulk cleanup.

## Architecture

In-memory key store with `dict[str, APIKey]` backing. Keys are prefixed tokens generated via `secrets.token_urlsafe(32)`. Validation checks revocation and expiry in constant time.

## Key Classes

### `APIKeyManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate` | `user_id, permissions, ttl_seconds, rate_limit, label` | `str` | Generate a new API key with optional TTL and rate limit |
| `validate` | `key_str: str` | `APIKey \| None` | Validate key; returns metadata if valid, `None` if expired/revoked/unknown |
| `revoke` | `key_str: str` | `bool` | Revoke a key (marks `revoked=True`) |
| `rotate` | `old_key_str, ttl_seconds` | `str \| None` | Revoke old key, issue new with same permissions |
| `list_keys` | `user_id, include_revoked` | `list[APIKey]` | List keys filtered by user and status |
| `cleanup_expired` | none | `int` | Remove expired/revoked keys; returns count removed |

Constructor: `prefix: str = "codomyrmex"`

### `APIKey` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | The API key string |
| `user_id` | `str` | Key owner |
| `permissions` | `list[str]` | Granted permissions |
| `expires_at` | `float \| None` | Expiry timestamp (`None` = no expiry) |
| `rate_limit` | `int` | Max requests per minute (0 = unlimited) |
| `revoked` | `bool` | Whether the key is revoked |
| `is_valid` | `bool` (property) | `not revoked and not is_expired` |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: Standard library (`secrets`, `time`, `dataclasses`)

## Constraints

- Keys are stored in-memory only; no persistence layer.
- `validate()` increments `request_count` as a side effect (for rate-limit tracking).
- Zero-mock: real key generation only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Invalid keys return `None` from `validate()` rather than raising.
- Key generation and revocation are logged at INFO level.
