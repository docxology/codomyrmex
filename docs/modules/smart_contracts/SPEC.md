# Smart Contracts — Functional Specification

**Module**: `codomyrmex.smart_contracts`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Web3 and blockchain smart contract interfaces.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `Network` | Class | Blockchain networks. |
| `TransactionStatus` | Class | Transaction status. |
| `Address` | Class | Blockchain address. |
| `Transaction` | Class | A blockchain transaction. |
| `ContractFunction` | Class | A smart contract function. |
| `Contract` | Class | A smart contract. |
| `ContractCall` | Class | Build and execute contract calls. |
| `TransactionBuilder` | Class | Build transactions with fluent API. |
| `ContractRegistry` | Class | Registry of known contracts. |
| `wei_to_ether()` | Function | wei to ether |
| `ether_to_wei()` | Function | ether to wei |
| `gwei_to_wei()` | Function | gwei to wei |
| `is_valid()` | Function | is valid |
| `encode_call()` | Function | Encode function call data (simplified). |

## 3. Dependencies

See `src/codomyrmex/smart_contracts/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.smart_contracts import Network, TransactionStatus, Address, Transaction, ContractFunction
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k smart_contracts -v
```
