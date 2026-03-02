# Codomyrmex Agents -- src/codomyrmex/config_management/secrets

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides secure secret storage and retrieval using Fernet symmetric encryption. Supports CRUD operations on encrypted secrets, key rotation with automatic re-encryption, and configuration-level field encryption.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `secret_manager.py` | `SecretManager` | Core secret manager using Fernet encryption for storing and retrieving secrets |
| `secret_manager.py` | `SecretManager.store_secret` | Encrypts and stores a secret value, returning a hex secret ID |
| `secret_manager.py` | `SecretManager.get_secret` | Retrieves and decrypts a secret by ID |
| `secret_manager.py` | `SecretManager.get_secret_by_name` | Retrieves and decrypts a secret by its name |
| `secret_manager.py` | `SecretManager.list_secrets` | Lists all stored secrets metadata (without values) |
| `secret_manager.py` | `SecretManager.delete_secret` | Removes a secret by ID |
| `secret_manager.py` | `SecretManager.rotate_key` | Generates a new encryption key and re-encrypts all existing secrets |
| `secret_manager.py` | `manage_secrets` | Convenience function dispatching operations by name |
| `secret_manager.py` | `encrypt_configuration` | Encrypts sensitive fields in a config dict, replacing values with `encrypted:{id}` references |

## Operating Contracts

- Encryption key is stored at `~/.codomyrmex/secrets.key` by default; auto-generated if absent.
- Secret IDs are generated using `secrets.token_hex(16)` (32 hex characters).
- Key rotation re-encrypts all in-memory secrets; secrets not yet loaded from persistent storage are not rotated.
- The `list_secrets` method never exposes decrypted values.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `cryptography.fernet.Fernet`, `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: Config deployment (environment secrets), trust gateway, authentication modules

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
