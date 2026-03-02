# Codomyrmex Agents -- src/codomyrmex/wallet/security

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides wallet security primitives including encrypted credential storage with HMAC-based key derivation, key rotation lifecycle management with configurable policies, encrypted backup/restore operations, and a "Natural Ritual" multi-factor recovery system.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `encrypted_storage.py` | `EncryptedStore` | In-memory encrypted credential vault using HMAC-SHA256 key derivation and XOR-based symmetric encryption with integrity verification |
| `encrypted_storage.py` | `EncryptedEntry` | Dataclass for an encrypted credential entry with ciphertext, nonce, auth tag, and timestamps |
| `key_rotation.py` | `KeyRotation` | Key rotation lifecycle manager with configurable policies (max age, max signatures), audit trail, and pre/post-rotation hooks |
| `key_rotation.py` | `RotationPolicy`, `RotationRecord` | Policy dataclass (max_age_days, max_signatures, auto_rotate) and rotation event record |
| `recovery.py` | `NaturalRitualRecovery` | Multi-factor recovery via ordered secret-experience challenges; all-or-nothing verification with lockout after max attempts |
| `recovery.py` | `RitualStep`, `hash_response` | Step dataclass with prompt and expected SHA-256 hash, and helper to hash plaintext responses |
| `backup.py` | `BackupManager` | Encrypted wallet backup/restore with JSON persistence, integrity verification via key hash comparison, and file-level permissions |

## Operating Contracts

- `EncryptedStore` uses `os.urandom(32)` for master key generation and `os.urandom(16)` for per-entry nonces; integrity is verified via HMAC-SHA256 tag comparison using `hmac.compare_digest`.
- `EncryptedStore.rotate_master_key` decrypts all entries with the old key, then re-encrypts with the new key atomically -- partial rotation is not possible.
- `KeyRotation.needs_rotation` returns `True` if signature count exceeds `max_signatures` OR key age exceeds `max_age_days`.
- `NaturalRitualRecovery.initiate_recovery` is all-or-nothing: every step must match for success; failed attempts increment a counter and lockout occurs after `max_attempts` (default 5).
- `BackupManager` stores backup files with `0o600` permissions; plaintext keys are never persisted.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging), `codomyrmex.encryption.keys.key_manager` (KeyManager for backup operations), `wallet.exceptions` (WalletNotFoundError, RitualError)
- **Used by**: Wallet CLI commands, wallet management workflows

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
