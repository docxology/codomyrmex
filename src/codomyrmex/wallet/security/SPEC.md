# Wallet Security -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Security layer for wallet key management providing symmetric encryption, policy-based rotation, encrypted backups, and multi-factor recovery ceremonies. Uses HMAC-SHA256 for key derivation and integrity verification.

## Architecture

```
EncryptedStore(master_key: bytes)
  +-- put(key, plaintext) / get(key) -> plaintext
  +-- delete(key) / has(key) / list_keys()
  +-- rotate_master_key(new_key)

KeyRotation()
  +-- register_wallet(id, policy)
  +-- record_signature(id)
  +-- needs_rotation(id) -> bool
  +-- record_rotation(id, new_key_hash)
  +-- pre_rotate_hooks / post_rotate_hooks

NaturalRitualRecovery()
  +-- register_ritual(user_id, steps)
  +-- initiate_recovery(user_id, responses) -> bool
  +-- get_remaining_attempts(user_id) -> int

BackupManager(key_manager, backup_dir)
  +-- create_backup(store) -> backup_id
  +-- verify_backup(path) -> bool
  +-- list_backups() -> list[dict]
  +-- delete_backup(backup_id)
```

## Key Classes

### EncryptedStore Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `put(key, plaintext)` | `None` | Encrypt and store with HMAC tag |
| `get(key)` | `bytes` | Decrypt after HMAC verification; raises on tamper |
| `delete(key)` | `None` | Remove entry |
| `rotate_master_key(new_key)` | `None` | Re-encrypt all entries with new master key |

### KeyRotation

| Field / Method | Description |
|----------------|-------------|
| `RotationPolicy.max_age_days` | Default 90 days |
| `RotationPolicy.max_signatures` | Default 10,000 signatures |
| `needs_rotation(wallet_id)` | True if age or sig count exceeded |
| `record_rotation(wallet_id, key_hash)` | Logs rotation with audit trail |

### NaturalRitualRecovery

| Method | Description |
|--------|-------------|
| `register_ritual(user_id, steps)` | Store SHA-256 hashed expected responses |
| `initiate_recovery(user_id, responses)` | All-or-nothing hash comparison |
| `max_attempts` | Default 5; lockout when exceeded |

### BackupManager

| Method | Returns | Description |
|--------|---------|-------------|
| `create_backup(store)` | `str` | Backup ID (SHA-256 of content) |
| `verify_backup(path)` | `bool` | Compare key hashes against current store |
| `list_backups()` | `list[dict]` | Sorted newest-first with metadata |

## Dependencies

- `hashlib`, `hmac`, `os`, `json`, `pathlib` (stdlib)
- `codomyrmex.encryption` for `KeyManager`

## Constraints

- Encryption uses XOR-based symmetric cipher -- not production-grade for high-security contexts.
- Master key is held in memory; no HSM or secure enclave integration.
- Backup files written with `0o600` permissions; directory permissions are caller's responsibility.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [wallet](../README.md)
