# Market Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Secure Cognitive Agent module for anonymous marketplace transactions. Supports reverse auctions and collective bargaining through demand aggregation.

## Key Features

- **Reverse Auctions**: Buyer-initiated competitive bidding
- **Demand Aggregation**: Collective bargaining for better pricing
- **Anonymous Bidding**: Persona-based marketplace identity

## Key Classes

| Class | Description |
|-------|-------------|
| `ReverseAuction` | Auction management |
| `DemandAggregator` | Collective bargaining |
| `BidManager` | Bid lifecycle |
| `ProviderRegistry` | Provider tracking |

## Quick Start

```python
from codomyrmex.market import ReverseAuction

market = ReverseAuction()
auction_id = market.create_request(
    persona_id="anon_1", 
    description="GPU Compute", 
    max_price=0.50
)
best_bid = market.get_best_bid(auction_id)
```

## Related Modules

- [identity](../identity/) - Anonymous personas
- [wallet](../wallet/) - Payment handling
- [privacy](../privacy/) - Transaction privacy

## Navigation

- **Source**: [src/codomyrmex/market/](../../../src/codomyrmex/market/)
- **Parent**: [docs/modules/](../README.md)
