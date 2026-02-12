# Smart Contracts Module

**Version**: v0.1.0 | **Status**: Active

Web3 and blockchain smart contract interfaces.


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`Network`** — Blockchain networks.
- **`TransactionStatus`** — Transaction status.
- **`Address`** — Blockchain address.
- **`Transaction`** — A blockchain transaction.
- **`ContractFunction`** — A smart contract function.
- **`Contract`** — A smart contract.
- **`ContractCall`** — Build and execute contract calls.
- **`TransactionBuilder`** — Build transactions with fluent API.

### Functions
- **`wei_to_ether()`** — wei_to_ether
- **`ether_to_wei()`** — ether_to_wei
- **`gwei_to_wei()`** — gwei_to_wei

## Directory Structure

- `models.py` — Data models (Network, TransactionStatus, Address, Transaction, ContractFunction)
- `contract.py` — Smart contract logic (Contract, ContractCall)
- `builders.py` — Transaction builder with fluent API (TransactionBuilder)
- `registry.py` — Contract registry (ContractRegistry)
- `events.py` — Contract events, filtering, and event log (ContractEvent, EventFilter, EventLog)
- `utils.py` — Unit conversion utilities (wei_to_ether, ether_to_wei, gwei_to_wei)
- `__init__.py` — Public API re-exports

## Quick Start

```python
from codomyrmex.smart_contracts import (
    Address, Contract, TransactionBuilder, Network,
    wei_to_ether, ether_to_wei
)

# Build a transaction
tx = (TransactionBuilder(Address("0x742d...1234"))
    .to(Address("0x8ba1...5678"))
    .value(ether_to_wei(0.1))
    .gas_limit(21000)
    .nonce(5)
    .build())

print(f"Tx Hash: {tx.hash}")
print(f"Value: {wei_to_ether(tx.value)} ETH")

# Load a contract
contract = Contract(
    address=Address("0xContractAddress"),
    abi=[{"type": "function", "name": "transfer", "inputs": [...]}]
)

print(contract.list_functions())  # ['transfer', ...]
```

## Exports

| Class/Function | Description |
|----------------|-------------|
| `Address` | Blockchain address with network validation |
| `Transaction` | Transaction with hash, value, gas, data |
| `TransactionStatus` | Enum: pending, confirmed, failed |
| `TransactionBuilder` | Fluent API for building transactions |
| `Contract` | Smart contract with ABI parsing |
| `ContractFunction` | Single contract function with inputs/outputs |
| `ContractCall` | Build contract method calls |
| `ContractRegistry` | Registry of named contracts |
| `Network` | Enum: ethereum, polygon, arbitrum, optimism, base, solana |
| `wei_to_ether(wei)` | Convert wei to ether |
| `ether_to_wei(eth)` | Convert ether to wei |
| `gwei_to_wei(gwei)` | Convert gwei to wei |

## Supported Networks

- Ethereum
- Polygon
- Arbitrum
- Optimism
- Base
- Solana


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k smart_contracts -v
```


## Documentation

- [Module Documentation](../../../docs/modules/smart_contracts/README.md)
- [Agent Guide](../../../docs/modules/smart_contracts/AGENTS.md)
- [Specification](../../../docs/modules/smart_contracts/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
