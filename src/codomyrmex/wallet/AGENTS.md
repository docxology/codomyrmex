# Wallet Module - Agent Guide

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Secure Cognitive Agent module enabling autonomous value/key management. Critical for "Self-Custody" capability - agents can hold keys without exposing them to external systems.

## Key Components

| Component | Module | Description |
|-----------|--------|-------------|
| `WalletManager` | `core.py` | Wallet creation, HMAC-SHA256 signing, verification, rotation, backup, deletion |
| `NaturalRitualRecovery` | `recovery.py` | Multi-step knowledge-based recovery with lockout protection |
| `BackupManager` | `backup.py` | Encrypted backup creation, listing, verification |
| `KeyRotation` | `key_rotation.py` | Policy-based rotation tracking with audit trail |
| `Wallet` | `wallet.py` | Unified facade combining key management and recovery |

## Exceptions

| Exception | When Raised |
|-----------|------------|
| `WalletError` | Duplicate wallet creation, general wallet errors |
| `WalletNotFoundError` | Wallet/key lookup fails |
| `WalletKeyError` | Key storage/retrieval fails |
| `RitualError` | Empty ritual steps, locked out user, no ritual registered |

## Usage for Agents

### Basic Operations

```python
from codomyrmex.wallet import WalletManager

wallet = WalletManager()
address = wallet.create_wallet("agent_001")
signature = wallet.sign_message("agent_001", b"Authorize Action")
is_valid = wallet.verify_signature("agent_001", b"Authorize Action", signature)
```

### Recovery

```python
from codomyrmex.wallet import NaturalRitualRecovery, RitualStep, hash_response

recovery = NaturalRitualRecovery()
recovery.register_ritual("agent_001", [
    RitualStep("Secret?", hash_response("MySecret")),
])
success = recovery.initiate_recovery("agent_001", ["MySecret"])
```

### Key Rotation with Policy

```python
from codomyrmex.wallet import KeyRotation, RotationPolicy

rotation = KeyRotation(policy=RotationPolicy(max_signatures=1000))
rotation.register_wallet("agent_001", address)
rotation.record_signature("agent_001")
if rotation.needs_rotation("agent_001"):
    new_address = wallet.rotate_keys("agent_001")
    rotation.record_rotation("agent_001", address, new_address)
```

### Backup Management

```python
from codomyrmex.wallet import BackupManager

backup_mgr = BackupManager(key_manager=wallet.key_manager)
record = backup_mgr.create_backup("agent_001", address)
is_valid = backup_mgr.verify_backup("agent_001", record["backup_id"])
```

## Agent Guidelines

1. **Never Export Keys**: Keys never leave secure storage. Use `sign_message()` instead.
2. **Rotation**: Rotate keys periodically via `rotate_keys()` or use `KeyRotation` for policy-driven rotation.
3. **Backup**: Create backups after key creation and rotation via `BackupManager`.
4. **Recovery**: Register recovery rituals with strong, unique secret knowledge.
5. **Error Handling**: Catch `WalletError` subclasses for granular error handling.
6. **Verification**: Always verify signatures with `verify_signature()` (constant-time).

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Keys are never logged, exported, or included in backup plaintext.

## Navigation Links

- **Source**: [src/codomyrmex/wallet/](.)
- **Documentation**: [docs/modules/wallet/](../../../docs/modules/wallet/)
- **Related**: [encryption/](../encryption/) | [identity/](../identity/) | [defense/](../defense/) | [privacy/](../privacy/)
