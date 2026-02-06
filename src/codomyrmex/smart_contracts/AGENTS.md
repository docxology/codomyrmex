# Agent Guidelines - Smart Contracts

## Module Overview

Blockchain smart contract interactions: Ethereum, Solana, and multi-chain.

## Key Classes

- **Contract** — Smart contract interface
- **Transaction** — Transaction building
- **TransactionBuilder** — Compose transactions
- **Network** — Network configuration

## Agent Instructions

1. **Validate addresses** — Check address format
2. **Estimate gas** — Always estimate before send
3. **Use nonce** — Track nonce for sequencing
4. **Test on testnet** — Never test on mainnet
5. **Verify contracts** — Check contract source

## Common Patterns

```python
from codomyrmex.smart_contracts import (
    Contract, TransactionBuilder, Network, wei_to_ether
)

# Connect to contract
contract = Contract(
    address="0x...",
    abi=contract_abi,
    network=Network.ETHEREUM_MAINNET
)

# Read contract state
balance = contract.call("balanceOf", user_address)
print(f"Balance: {wei_to_ether(balance)} ETH")

# Build transaction
tx = TransactionBuilder()
tx.to(contract.address)
tx.data(contract.encode("transfer", recipient, amount))
tx.gas_limit(100000)

# Sign and send
signed = tx.sign(private_key)
tx_hash = contract.send(signed)
```

## Testing Patterns

```python
# Verify address validation
from codomyrmex.smart_contracts import is_valid_address
assert is_valid_address("0x" + "a" * 40)
assert not is_valid_address("invalid")

# Verify unit conversion
assert wei_to_ether(10**18) == 1.0
assert ether_to_wei(1.0) == 10**18
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
