# Smart Contracts Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Web3 and blockchain smart contract interfaces.

## Key Features

- **Network** — Blockchain networks.
- **TransactionStatus** — Transaction status.
- **Address** — Blockchain address.
- **Transaction** — A blockchain transaction.
- **ContractFunction** — A smart contract function.
- **Contract** — A smart contract.
- `wei_to_ether()` — wei to ether
- `ether_to_wei()` — ether to wei
- `gwei_to_wei()` — gwei to wei
- `is_valid()` — is valid

## Quick Start

```python
from codomyrmex.smart_contracts import Network, TransactionStatus, Address

# Initialize
instance = Network()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Network` | Blockchain networks. |
| `TransactionStatus` | Transaction status. |
| `Address` | Blockchain address. |
| `Transaction` | A blockchain transaction. |
| `ContractFunction` | A smart contract function. |
| `Contract` | A smart contract. |
| `ContractCall` | Build and execute contract calls. |
| `TransactionBuilder` | Build transactions with fluent API. |
| `ContractRegistry` | Registry of known contracts. |

### Functions

| Function | Description |
|----------|-------------|
| `wei_to_ether()` | wei to ether |
| `ether_to_wei()` | ether to wei |
| `gwei_to_wei()` | gwei to wei |
| `is_valid()` | is valid |
| `encode_call()` | Encode function call data (simplified). |
| `get_function()` | get function |
| `list_functions()` | list functions |
| `with_args()` | with args |
| `with_value()` | with value |
| `with_gas_limit()` | with gas limit |
| `encode()` | Encode the call data. |
| `to_transaction()` | Build transaction for this call. |
| `to()` | to |
| `value()` | value |
| `data()` | data |
| `gas_limit()` | gas limit |
| `gas_price()` | gas price |
| `nonce()` | nonce |
| `build()` | build |
| `register()` | register |
| `get()` | get |
| `list()` | list |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k smart_contracts -v
```

## Navigation

- **Source**: [src/codomyrmex/smart_contracts/](../../../src/codomyrmex/smart_contracts/)
- **Parent**: [Modules](../README.md)
