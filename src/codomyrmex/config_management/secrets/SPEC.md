# Secrets Management -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides secure secret storage, retrieval, and lifecycle management using Fernet symmetric encryption from the `cryptography` library. Supports CRUD operations, key rotation with automatic re-encryption, and configuration-level field encryption.

## Architecture

Single-class design with `SecretManager` as the primary interface. Encryption keys are stored on disk at a configurable path. Secrets are held in an in-memory dictionary with encrypted values. Convenience functions provide operation-based dispatch and bulk configuration encryption.

## Key Classes

### `SecretManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `key_file: str \| None` | `None` | Loads or generates Fernet key at `~/.codomyrmex/secrets.key` |
| `store_secret` | `name: str, value: str, metadata: dict \| None` | `str` | Encrypts and stores a secret; returns hex ID |
| `get_secret` | `secret_id: str` | `str \| None` | Decrypts and returns secret value by ID |
| `get_secret_by_name` | `name: str` | `str \| None` | Decrypts and returns secret value by name |
| `list_secrets` | | `list[dict]` | Returns metadata for all secrets (no values exposed) |
| `delete_secret` | `secret_id: str` | `bool` | Removes a secret from the store |
| `rotate_key` | | `str` | Generates new key, re-encrypts all secrets, returns new key ID |

### Module-Level Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `manage_secrets` | `operation: str, **kwargs` | `Any` | Dispatches to SecretManager methods by operation name |
| `encrypt_configuration` | `config: dict, secret_keys: list[str]` | `dict` | Encrypts specified config fields, replacing values with `encrypted:{id}` |

## Dependencies

- **Internal**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `cryptography.fernet.Fernet`

## Constraints

- Key file default path: `~/.codomyrmex/secrets.key`; parent directory is auto-created.
- Secret IDs use `secrets.token_hex(16)` (32-character hex strings).
- Key rotation re-encrypts in-memory secrets only; externally persisted secrets require separate handling.
- The `list_secrets` endpoint never includes decrypted values.
- Zero-mock: real encryption only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Key rotation logs per-secret re-encryption failures without aborting the full rotation.
- Unknown operations in `manage_secrets` raise `CodomyrmexError`.
- All errors are logged before propagation.
