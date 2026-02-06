# Smart Contracts Module

Web3 and blockchain smart contract interfaces.

```python
from codomyrmex.smart_contracts import (
    Contract, Address, TransactionBuilder, Network,
    ether_to_wei,
)

# Build transaction
tx = (TransactionBuilder(Address("0x...", Network.ETHEREUM))
    .to(Address("0x..."))
    .value(ether_to_wei(0.1))
    .build())
```
