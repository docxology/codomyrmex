# Market Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Reverse auction and demand aggregation for AI service procurement.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Fetch market data and auction state | Direct Python import |
| **THINK** | Analyze market signals and bid patterns | Direct Python import |
| **PLAN** | Make market-driven procurement decisions | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Architect agent imports `ReverseAuction` and `DemandAggregator` to evaluate AI service procurement options during planning phases.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`DemandAggregator`** — Aggregates similar demands into a bulk auction.
- **`Bid`** — Bid
- **`AuctionRequest`** — AuctionRequest
- **`ReverseAuction`** — Manages anonymous reverse auctions.
- **`Market`** — Main class for market functionality.

### Functions
- **`create_market()`** — Create a new Market instance.

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

## MCP Tools

The module exposes Model Context Protocol (MCP) tools in `mcp_tools.py` for interacting with the marketplace:
- `market_create_auction`: Create a new reverse auction request.
- `market_place_bid`: Place a bid on an active auction.
- `market_get_best_bid`: Get the current best bid for an auction.
- `market_register_demand`: Register demand for a category to participate in collective bargaining.
- `market_trigger_bulk_auction`: Trigger a bulk auction if demand meets the threshold.
- `market_get_stats`: Get marketplace statistics including agents and tasks.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k market -v
```

## Documentation

- [Module Documentation](../../../docs/modules/market/README.md)
- [Agent Guide](../../../docs/modules/market/AGENTS.md)
- [Specification](../../../docs/modules/market/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
