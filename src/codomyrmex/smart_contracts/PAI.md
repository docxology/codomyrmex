# Personal AI Infrastructure — Smart Contracts Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Smart Contracts module provides PAI integration for blockchain interactions, enabling AI agents to interact with decentralized applications.

## PAI Capabilities

### Contract Interactions

AI agents can interact with smart contracts using the fluent API:

```python
from codomyrmex.smart_contracts import (
    Address, Contract, ContractCall, TransactionBuilder, Network
)

# Create contract with ABI
addr = Address(value="0x" + "a" * 40, network=Network.ETHEREUM)
contract = Contract(address=addr, abi=contract_abi, name="MyToken")

# Look up function from ABI
func = contract.get_function("transfer")

# Build a contract call (fluent API)
call = (
    ContractCall(contract, "transfer")
    .with_args("0xrecipient", 1000)
    .with_gas_limit(60000)
)
tx = call.to_transaction(from_address=addr, nonce=5)

# Build raw transaction (fluent API)
tx = (
    TransactionBuilder(addr)
    .to(addr)
    .value(1000)
    .gas_limit(21000)
    .build()
)
```

### Contract Registry & Events

Manage contracts and track events:

```python
from codomyrmex.smart_contracts import (
    ContractRegistry, ContractEvent, EventFilter, EventLog
)

# Registry
registry = ContractRegistry()
registry.register("token", contract)
registry.get("token")      # -> Contract
registry.remove("token")   # -> True

# Events
log = EventLog()
log.add(ContractEvent(name="Transfer", block_number=100, args={"to": "0x1"}))
log.add(ContractEvent(name="Approval", block_number=101))

# Query with filter
transfers = log.query(EventFilter().event("Transfer").from_block(50))
latest = log.latest(5)     # 5 most recent by block number
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Contract` | ABI parsing and function lookup |
| `ContractCall` | Fluent contract call builder |
| `TransactionBuilder` | Fluent transaction builder |
| `ContractRegistry` | Named contract management |
| `EventLog` | Event tracking and querying |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
