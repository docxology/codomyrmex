# market

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The market module facilitates anonymous economic coordination through reverse auctions and demand aggregation. Agents post demands without revealing identity and providers submit competitive bids, while the demand aggregator pools identical needs from multiple entities to achieve bulk purchasing power with an expected 10% discount threshold.

## Key Exports

- **`ReverseAuction`** -- Manages the full auction lifecycle (OPEN, CLOSED, CANCELLED). Supports `create_request()`, `place_bid()` with automatic price-sorted ranking, `get_best_bid()`, `close_auction()`, `cancel_auction()`, and `get_history()` per persona.
- **`Bid`** -- Dataclass representing a provider's offer with `provider_id`, `amount`, `details`, and auto-generated `timestamp`.
- **`AuctionRequest`** -- Dataclass representing a demand posting with `id`, anonymous `requester_persona_id`, `item_description`, `max_price`, a sorted list of `bids`, and lifecycle `status`.
- **`DemandAggregator`** -- Aggregates similar demands by category from multiple personas. When a configurable threshold of interested parties is reached (default 5), triggers a bulk auction through `ReverseAuction` at 90% of the average max price.

## Directory Contents

- `__init__.py` - Module entry point; exports all market classes
- `auction.py` - `ReverseAuction` manager, `Bid` and `AuctionRequest` dataclasses
- `aggregator.py` - `DemandAggregator` for pooling demand and triggering bulk auctions
- `market.py` - Additional market utilities
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `SECURITY.md` - Security considerations
- `CHANGELOG.md` - Version history
- `USAGE_EXAMPLES.md` - Usage examples and patterns
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/market/](../../../docs/modules/market/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
