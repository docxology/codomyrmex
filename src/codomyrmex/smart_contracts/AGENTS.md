# Agent Guidelines - Smart Contracts

## Module Overview

Blockchain smart contract interactions: Ethereum, Solana, and multi-chain.

## Key Classes

- **Contract** — Smart contract interface (ABI parsing, function lookup)
- **ContractCall** — Fluent contract call builder
- **Transaction** — Transaction dataclass
- **TransactionBuilder** — Fluent transaction builder
- **Network** — Network enum (ETHEREUM, POLYGON, ARBITRUM, OPTIMISM, BASE, SOLANA)
- **ContractRegistry** — Named contract registry
- **ContractEvent** / **EventFilter** / **EventLog** — Event system

## Agent Instructions

1. **Validate addresses** — Use `Address.is_valid` property
2. **Use ContractCall** — Fluent builder for function calls
3. **Use nonce** — Track nonce for sequencing
4. **Test on testnet** — Never test on mainnet
5. **Verify contracts** — Check contract source

## Common Patterns

```python
from codomyrmex.smart_contracts import (
    Address, Contract, ContractCall, ContractRegistry,
    TransactionBuilder, Network, wei_to_ether,
    ContractEvent, EventFilter, EventLog
)

# Create contract with ABI
addr = Address(value="0x" + "a" * 40, network=Network.ETHEREUM)
contract = Contract(address=addr, abi=contract_abi, name="MyToken")

# Look up function from ABI
func = contract.get_function("transfer")
print(func.name, func.inputs)

# Build and encode a contract call
call = (
    ContractCall(contract, "transfer")
    .with_args("0xrecipient", 1000)
    .with_value(0)
    .with_gas_limit(60000)
)
tx = call.to_transaction(from_address=addr, nonce=5)

# Build raw transaction
tx = (
    TransactionBuilder(addr)
    .to(addr)
    .value(ether_to_wei(1.0))
    .gas_limit(21000)
    .build()
)

# Registry
registry = ContractRegistry()
registry.register("token", contract)
registry.get("token")      # -> Contract
registry.remove("token")   # -> True
registry.list()             # -> []

# Events
log = EventLog()
log.add(ContractEvent(name="Transfer", block_number=100))
log.add(ContractEvent(name="Approval", block_number=101))
results = log.query(EventFilter().event("Transfer"))
```

## Testing Patterns

```python
# Verify address validation
addr = Address(value="0x" + "a" * 40)
assert addr.is_valid is True

# Verify unit conversion
assert wei_to_ether(10**18) == 1.0
assert ether_to_wei(1.0) == 10**18
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
