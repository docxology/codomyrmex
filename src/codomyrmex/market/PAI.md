# Personal AI Infrastructure — Market Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Market module provides reverse auction and demand aggregation mechanisms for AI agent resource allocation. It enables agents to bid on tasks, aggregate demand for compute/services, and negotiate resource allocation through market-based mechanisms. Part of the Secure Cognitive Agent suite.

## PAI Capabilities

### Reverse Auctions

```python
from codomyrmex.market import ReverseAuction, AuctionRequest, Bid

# Create a reverse auction for a task
auction = ReverseAuction()
request = AuctionRequest(task="code_review", requirements={"language": "python"})

# Agents bid on the task
bid = Bid(agent="claude", cost=0.5, estimated_time=60)
auction.submit_bid(request, bid)
```

### Demand Aggregation

```python
from codomyrmex.market import DemandAggregator

aggregator = DemandAggregator()
# Aggregate demand for compute resources across multiple agents
# Optimize resource allocation based on task priorities
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ReverseAuction` | Class | Task auction engine where providers bid |
| `AuctionRequest` | Class | Task specification for auction |
| `Bid` | Class | Provider bid on an auction request |
| `DemandAggregator` | Class | Multi-agent demand collection and optimization |

## PAI Algorithm Phase Mapping

| Phase | Market Contribution |
|-------|---------------------|
| **PLAN** | Select optimal agent/model for task via auction mechanism |
| **EXECUTE** | Allocate compute resources based on aggregated demand |
| **LEARN** | Track bid outcomes to improve future resource allocation |

## Architecture Role

**Specialized Layer** — Part of the Secure Cognitive Agent suite (`identity`, `wallet`, `defense`, `market`, `privacy`). Provides agent selection logic consumed by `orchestrator/` and `agents/`.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.market import ...`
- CLI: `codomyrmex market <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
