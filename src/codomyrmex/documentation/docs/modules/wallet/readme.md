# Wallet Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `wallet` module provides secure self-custody key management and "Natural Ritual" recovery mechanisms for cognitive agents. It extends standard key management with behavioral and knowledge-based recovery flows, eliminating reliance on centralized custodians.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **EXECUTE** | Manage cryptocurrency wallet operations (create, sign, rotate) | Direct Python import |
| **OBSERVE** | Check balances, list wallets, and inspect transactions | Direct Python import |
| **VERIFY** | Validate transaction signatures and backup integrity | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge to manage self-custody keys, sign messages, and perform recovery operations.

## Key Capabilities

- **Self-Custody**: Secure local storage of private keys via `encryption.KeyManager`. Keys never leave secure storage.
- **Message Signing & Verification**: HMAC-SHA256 signing with constant-time verification (`WalletManager`).
- **Natural Ritual Recovery**: Recover keys via a sequence of secret knowledge challenges (`NaturalRitualRecovery`).
- **Backup Management**: Encrypted backup creation, listing, verification, and deletion (`BackupManager`).
- **Key Rotation**: Policy-driven rotation with audit trail and hooks (`KeyRotation`).
- **Unified Facade**: Simplified `Wallet` class combining key management and recovery.

## Core Components

| Component | Module | Description |
|-----------|--------|-------------|
| `WalletManager` | `core.py` | Wallet creation, signing, verification, rotation, backup, deletion |
| `NaturalRitualRecovery` | `recovery.py` | Multi-step knowledge-based recovery with lockout protection |
| `BackupManager` | `backup.py` | Encrypted backup lifecycle management |
| `KeyRotation` | `key_rotation.py` | Policy-based rotation tracking and audit trail |
| `Wallet` | `wallet.py` | Unified facade combining WalletManager + recovery |
| `RitualStep` | `recovery.py` | Dataclass for recovery ritual steps |
| `RotationRecord` | `key_rotation.py` | Dataclass for rotation audit records |
| `RotationPolicy` | `key_rotation.py` | Dataclass for rotation policy configuration |

## Exception Hierarchy

| Exception | Description |
|-----------|-------------|
| `WalletError` | Base exception for wallet operations |
| `WalletNotFoundError` | Wallet or key not found |
| `WalletKeyError` | Key storage or retrieval failure |
| `RitualError` | Recovery ritual operation failure |

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Quick Start

```python
from codomyrmex.wallet import WalletManager, NaturalRitualRecovery, RitualStep, hash_response

# Create and use a wallet
wallet = WalletManager()
address = wallet.create_wallet("user_1")
signature = wallet.sign_message("user_1", b"Authorize Action")
assert wallet.verify_signature("user_1", b"Authorize Action", signature)

# Set up recovery
recovery = NaturalRitualRecovery()
recovery.register_ritual("user_1", [
    RitualStep("Secret color?", hash_response("Blue")),
    RitualStep("Lucky number?", hash_response("7")),
])
assert recovery.initiate_recovery("user_1", ["Blue", "7"])
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports, version, convenience functions |
| `core.py` | WalletManager implementation |
| `recovery.py` | NaturalRitualRecovery, RitualStep, hash_response |
| `backup.py` | BackupManager implementation |
| `key_rotation.py` | KeyRotation, RotationPolicy, RotationRecord |
| `wallet.py` | Wallet facade class |
| `exceptions.py` | Custom exception hierarchy |
| `py.typed` | PEP 561 type hint marker |

## Related Modules

- [encryption](../encryption/) - Key storage backend
- [identity](../identity/) - Persona management
- [defense](../defense/) - Active defense
- [privacy](../privacy/) - Data minimization

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k wallet -v
```

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`contracts/`** | Web3 smart contract interfaces and blockchain operations |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/wallet/](../../../docs/modules/wallet/)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Security Policy**: [SECURITY.md](SECURITY.md)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Parent Directory**: [codomyrmex](../README.md)
