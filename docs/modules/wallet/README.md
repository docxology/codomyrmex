# Wallet Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Secure Cognitive Agent module for self-custody key management. Enables autonomous value/key holding without exposing keys to external systems. Provides message signing, signature verification, encrypted backups, policy-driven key rotation, and knowledge-based recovery.

## Key Features

- **Self-Custody**: Keys never leave secure local storage (via `encryption.KeyManager`)
- **Message Signing & Verification**: HMAC-SHA256 with constant-time verification
- **Natural Ritual Recovery**: Multi-step knowledge-based key recovery with lockout protection
- **Key Rotation**: Policy-driven rotation with configurable thresholds and audit trail
- **Secure Backup**: Encrypted backup management with integrity verification
- **Unified Facade**: Simplified `Wallet` class for streamlined usage

## Architecture

```
wallet/
  __init__.py          # Public exports, __version__, convenience functions
  core.py              # WalletManager - wallet lifecycle & signing
  recovery.py          # NaturalRitualRecovery, RitualStep, hash_response
  backup.py            # BackupManager - backup lifecycle
  key_rotation.py      # KeyRotation, RotationPolicy, RotationRecord
  wallet.py            # Wallet facade (unified API)
  exceptions.py        # WalletError, WalletNotFoundError, WalletKeyError, RitualError
  py.typed             # PEP 561 type hint marker
```

## Key Classes

| Class | Module | Description |
|-------|--------|-------------|
| `WalletManager` | `core.py` | Core wallet creation, signing, verification, rotation, backup, deletion |
| `NaturalRitualRecovery` | `recovery.py` | Multi-step knowledge-based recovery with lockout |
| `BackupManager` | `backup.py` | Encrypted backup creation, listing, verification, deletion |
| `KeyRotation` | `key_rotation.py` | Policy-based rotation tracking and audit trail |
| `Wallet` | `wallet.py` | Unified facade combining WalletManager + recovery |

## Data Models

| Model | Description |
|-------|-------------|
| `RitualStep` | Dataclass: prompt + expected_response_hash |
| `RotationRecord` | Dataclass: user_id, old/new wallet_id, timestamp, reason |
| `RotationPolicy` | Dataclass: max_age_days, max_signatures, auto_rotate |

## Exceptions

| Exception | Base | Description |
|-----------|------|-------------|
| `WalletError` | `CodomyrmexError` | Base wallet exception |
| `WalletNotFoundError` | `WalletError` | Wallet/key not found |
| `WalletKeyError` | `WalletError` | Key storage/retrieval failure |
| `RitualError` | `WalletError` | Recovery ritual failure |

## Quick Start

```python
from codomyrmex.wallet import WalletManager, NaturalRitualRecovery, RitualStep, hash_response

# Create and sign
wallet = WalletManager()
address = wallet.create_wallet("user_1")
signature = wallet.sign_message("user_1", b"Authorize Action")
assert wallet.verify_signature("user_1", b"Authorize Action", signature)

# Key rotation
new_address = wallet.rotate_keys("user_1", reason="periodic")

# Recovery setup
recovery = NaturalRitualRecovery()
recovery.register_ritual("user_1", [
    RitualStep("Secret color?", hash_response("Blue")),
    RitualStep("Lucky number?", hash_response("7")),
])
assert recovery.initiate_recovery("user_1", ["Blue", "7"])
```

## Convenience Functions

```python
from codomyrmex.wallet import create_wallet, get_wallet_manager, hash_response

# Quick wallet creation
address = create_wallet("user_1")

# Get a configured manager
mgr = get_wallet_manager()

# Hash a ritual response
h = hash_response("MySecret")  # SHA-256 hex digest
```

## Dependencies

- **Internal**: `codomyrmex.encryption.key_manager.KeyManager`, `codomyrmex.logging_monitoring`
- **Standard Library**: `hashlib`, `hmac`, `uuid`, `json`, `datetime`, `pathlib`, `dataclasses`


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k wallet -v
```

## Related Modules

- [encryption](../encryption/) - Key storage backend
- [identity](../identity/) - Persona management
- [defense](../defense/) - Active defense
- [privacy](../privacy/) - Data minimization

## Navigation

- **Source**: [src/codomyrmex/wallet/](../../../src/codomyrmex/wallet/)
- **API Specification**: [src/codomyrmex/wallet/API_SPECIFICATION.md](../../../src/codomyrmex/wallet/API_SPECIFICATION.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Security Policy**: [src/codomyrmex/wallet/SECURITY.md](../../../src/codomyrmex/wallet/SECURITY.md)
- **Usage Examples**: [src/codomyrmex/wallet/USAGE_EXAMPLES.md](../../../src/codomyrmex/wallet/USAGE_EXAMPLES.md)
- **MCP Tools**: [src/codomyrmex/wallet/MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/wallet/MCP_TOOL_SPECIFICATION.md)
- **Changelog**: [src/codomyrmex/wallet/CHANGELOG.md](../../../src/codomyrmex/wallet/CHANGELOG.md)
- **Parent**: [docs/modules/](../README.md)
