# Wallet Module - Agent Guide

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Secure Cognitive Agent module enabling autonomous value/key management. Critical for "Self-Custody" capability - agents can hold keys without exposing them to external systems.

## Key Components

| Component | Description |
|-----------|-------------|
| `WalletManager` | Core key management and signing |
| `NaturalRitualRecovery` | Social/memory-based key recovery |
| `KeyRotation` | Automated key rotation |
| `BackupManager` | Secure backup handling |

## Usage for Agents

### Basic Operations

```python
from codomyrmex.wallet import WalletManager

wallet = WalletManager()
address = wallet.create_wallet("user_1")
signature = wallet.sign_message("user_1", b"Authorize Action")
```

### Recovery

```python
from codomyrmex.wallet import NaturalRitualRecovery, RitualStep

recovery = NaturalRitualRecovery()
# User proves knowledge of secret memory
success = recovery.initiate_recovery("user_1", ["SecretAnswer1", "SecretAnswer2"])
```

## Agent Guidelines

1. **Never Export Keys**: Keys never leave secure storage
2. **Rotation**: Rotate keys periodically via `rotate_key()`
3. **Backup**: Maintain encrypted backups via `BackupManager`

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent**: [codomyrmex/](../README.md)
- **🏠 Root**: [../../../README.md](../../../README.md)
- **🔗 Related**: [identity/](../identity/) | [defense/](../defense/) | [privacy/](../privacy/)
