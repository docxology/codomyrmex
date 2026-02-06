# Market Module

**Version**: v0.1.0 | **Status**: Active

Reverse auction and demand aggregation for AI service procurement.

## Quick Start

```python
from codomyrmex.market import ReverseAuction, Bid, AuctionRequest, DemandAggregator

# Create an auction request
request = AuctionRequest(
    resource="llm-inference",
    quantity=1000,
    max_price=0.01,
    deadline="2024-12-31"
)

# Start reverse auction (sellers compete to offer lowest price)
auction = ReverseAuction(request)
auction.add_bid(Bid(provider="openai", price=0.008, capacity=5000))
auction.add_bid(Bid(provider="anthropic", price=0.007, capacity=3000))
auction.add_bid(Bid(provider="local", price=0.005, capacity=500))

winner = auction.resolve()
print(f"Winner: {winner.provider} at ${winner.price}/request")

# Aggregate demand across users
aggregator = DemandAggregator()
aggregator.add(user="team-a", resource="gpu-hours", quantity=100)
aggregator.add(user="team-b", resource="gpu-hours", quantity=50)

bulk_order = aggregator.consolidate("gpu-hours")
print(f"Total demand: {bulk_order.quantity}")
```

## Exports

| Class | Description |
|-------|-------------|
| `ReverseAuction` | Sellers compete to win buyer's request |
| `Bid` | Provider bid with price and capacity |
| `AuctionRequest` | Buyer's resource request |
| `DemandAggregator` | Consolidate demand for bulk pricing |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
