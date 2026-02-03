# Wallet Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Secure Cognitive Agent module for self-custody key management. Enables autonomous value/key holding without exposing keys to external systems.

## Key Features

- **Self-Custody**: Keys never leave secure local storage
- **Natural Ritual Recovery**: Social/memory-based key recovery
- **Key Rotation**: Automated periodic key rotation
- **Secure Backup**: Encrypted backup management

## Key Classes

| Class | Description |
|-------|-------------|
| `WalletManager` | Core key management |
| `NaturalRitualRecovery` | Recovery system |
| `KeyRotation` | Automated rotation |
| `BackupManager` | Backup handling |

## Quick Start

```python
from codomyrmex.wallet import WalletManager

wallet = WalletManager()
address = wallet.create_wallet("user_1")
signature = wallet.sign_message("user_1", b"Authorize Action")
```

## Related Modules

- [identity](../identity/) - Persona management
- [defense](../defense/) - Active defense
- [privacy](../privacy/) - Data minimization

## Navigation

- **Source**: [src/codomyrmex/wallet/](../../../src/codomyrmex/wallet/)
- **Parent**: [docs/modules/](../README.md)
