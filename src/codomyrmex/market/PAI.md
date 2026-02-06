# Personal AI Infrastructure — Market Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Market module provides PAI integration for market data and trading.

## PAI Capabilities

### Market Data

Fetch market data:

```python
from codomyrmex.market import MarketData

data = MarketData()
price = data.get_price("BTC/USD")
history = data.get_history("ETH/USD", period="1d")
```

### Trading Operations

Execute trades:

```python
from codomyrmex.market import TradingClient

client = TradingClient()
order = client.place_order(
    symbol="BTC/USD", side="buy", amount=0.1
)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `MarketData` | Fetch prices |
| `TradingClient` | Execute trades |
| `Portfolio` | Track positions |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
