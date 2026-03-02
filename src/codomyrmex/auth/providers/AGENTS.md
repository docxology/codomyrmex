# Codomyrmex Agents — src/codomyrmex/auth/providers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides API key management with generation, validation, expiry-based invalidation, per-key rate limits, key rotation, and lifecycle operations (revoke, list, cleanup).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `api_key_manager.py` | `APIKeyManager` | Core manager for API key generation, validation, rotation, revocation, and listing |
| `api_key_manager.py` | `APIKey` | Dataclass holding key metadata: user_id, permissions, expiry, rate_limit, request_count |

## Operating Contracts

- Keys are generated using `secrets.token_urlsafe(32)` with a configurable prefix (default: `codomyrmex`).
- `validate()` returns `None` for unknown, expired, or revoked keys; increments `request_count` on valid keys.
- `rotate()` revokes the old key and issues a new one with the same permissions and rate limit.
- `cleanup_expired()` permanently removes expired and revoked keys from memory.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config` (structured logging)
- **Used by**: `auth` parent module, API authentication middleware

## Navigation

- **Parent**: [auth](../README.md)
- **Root**: [Root](../../../../README.md)
