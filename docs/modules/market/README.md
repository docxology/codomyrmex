# Market Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Reverse auction and demand aggregation capabilities for resource allocation and pricing.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **DemandAggregator** — Aggregates similar demands into a bulk auction.
- **Bid** — Bid
- **AuctionRequest** — AuctionRequest
- **ReverseAuction** — Manages anonymous reverse auctions.
- **Market** — Main class for market functionality.
- `create_market()` — Create a new Market instance.

## Quick Start

```python
from codomyrmex.market import DemandAggregator, Bid, AuctionRequest

instance = DemandAggregator()
```

## Source Files

- `aggregator.py`
- `auction.py`
- `market.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k market -v
```

## Navigation

- **Source**: [src/codomyrmex/market/](../../../src/codomyrmex/market/)
- **Parent**: [Modules](../README.md)
