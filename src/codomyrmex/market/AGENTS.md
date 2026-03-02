# Market Module - Agent Guide

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Secure Cognitive Agent module enabling anonymous marketplace transactions. Supports reverse auctions and collective bargaining through demand aggregation.

## Key Components

| Component | Description |
|-----------|-------------|
| `ReverseAuction` | Buyer-initiated auction system |
| `DemandAggregator` | Collective bargaining engine |
| `BidManager` | Bid lifecycle management |
| `ProviderRegistry` | Service provider tracking |

## Usage for Agents

### Auction Lifecycle

```python
from codomyrmex.market import ReverseAuction

market = ReverseAuction()
# 1. Create Request
auction_id = market.create_request(persona_id="anon_1", description="GPU Compute", max_price=0.50)

# 2. Receive Bids (from providers)
market.place_bid(auction_id, "provider_A", 0.45, "High speed")

# 3. Select Winner
best_bid = market.get_best_bid(auction_id)
```

### Demand Aggregation

```python
from codomyrmex.market import DemandAggregator

aggregator = DemandAggregator()
# Join collective demand for better pricing
aggregator.join_demand(item="storage_1TB", persona_id="anon_1")
```

## Agent Guidelines

1. **Anonymity**: Always use personas, never real identities
2. **Verification**: Verify provider authenticity before transacting
3. **Cancellation**: Use `cancel_auction()` for cleanup

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Implements market data analysis, reverse auction lifecycle, demand aggregation, and bid management via ReverseAuction, DemandAggregator, and BidManager.

### Architect Agent
**Use Cases**: Designs market data pipelines, evaluates auction system scalability, and reviews provider registry integration patterns.

### QATester Agent
**Use Cases**: Validates market data processing accuracy, auction lifecycle correctness, bid ranking logic, and demand aggregation consistency.

## Navigation Links

- **📁 Parent**: [codomyrmex/](../README.md)
- **🏠 Root**: [../../../README.md](../../../README.md)
- **🔗 Related**: [identity/](../identity/) | [wallet/](../wallet/) | [privacy/](../privacy/)
