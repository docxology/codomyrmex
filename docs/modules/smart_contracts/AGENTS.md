# Smart Contracts Module — Agent Coordination

## Purpose

Web3 and blockchain smart contract interfaces.

## Key Capabilities

- **Network**: Blockchain networks.
- **TransactionStatus**: Transaction status.
- **Address**: Blockchain address.
- **Transaction**: A blockchain transaction.
- **ContractFunction**: A smart contract function.
- `wei_to_ether()`: wei to ether
- `ether_to_wei()`: ether to wei
- `gwei_to_wei()`: gwei to wei

## Agent Usage Patterns

```python
from codomyrmex.smart_contracts import Network

# Agent initializes smart contracts
instance = Network()
```

## Integration Points

- **Source**: [src/codomyrmex/smart_contracts/](../../../src/codomyrmex/smart_contracts/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
