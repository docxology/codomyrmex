# Personal AI Infrastructure — Smart Contracts Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Smart Contracts module provides PAI integration for blockchain interactions, enabling AI agents to interact with decentralized applications.

## PAI Capabilities

### Contract Interactions

AI agents can interact with smart contracts:

```python
from codomyrmex.smart_contracts import (
    Contract, TransactionBuilder, Network
)

# Connect to contract
contract = Contract(
    address="0x1234...",
    abi=contract_abi,
    network=Network.ETHEREUM_MAINNET
)

# Read contract state
balance = contract.call("balanceOf", wallet_address)

# Build transaction
tx = TransactionBuilder()
tx.to(contract.address)
tx.data(contract.encode("transfer", recipient, amount))
tx.gas_limit(100000)
```

### Multi-Chain Support

Work across multiple blockchains:

```python
from codomyrmex.smart_contracts import Network, MultiChainManager

# Manage multiple networks
manager = MultiChainManager()
manager.add_network(Network.ETHEREUM_MAINNET)
manager.add_network(Network.POLYGON)

# Execute across chains
results = manager.execute_multi(
    contracts={"eth": eth_contract, "poly": poly_contract},
    method="getPrice"
)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Contract` | Interact with contracts |
| `TransactionBuilder` | Build transactions |
| `MultiChainManager` | Multi-chain operations |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
