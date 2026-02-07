# Market Module — Agent Coordination

## Purpose

Market Module.

## Key Capabilities

- Market operations and management

## Agent Usage Patterns

```python
from codomyrmex.market import *

# Agent uses market capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/market/](../../../src/codomyrmex/market/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`DemandAggregator`** — Aggregates similar demands into a bulk auction.
- **`Bid`** — Bid
- **`AuctionRequest`** — AuctionRequest
- **`ReverseAuction`** — Manages anonymous reverse auctions.
- **`Market`** — Main class for market functionality.
- **`create_market()`** — Create a new Market instance.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k market -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
