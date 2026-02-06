# Personal AI Infrastructure — Wallet Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Wallet module provides PAI integration for cryptocurrency wallet management.

## PAI Capabilities

### Wallet Operations

Manage crypto wallets:

```python
from codomyrmex.wallet import WalletManager

wallet = WalletManager()
address = wallet.create_address()
balance = wallet.get_balance(address)
```

### Transaction Support

Send transactions:

```python
from codomyrmex.wallet import WalletManager

wallet = WalletManager()
tx = wallet.send(to="0x...", amount=0.1)
print(f"TX: {tx.hash}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `WalletManager` | Manage wallets |
| `send` | Send transactions |
| `get_balance` | Check balances |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
