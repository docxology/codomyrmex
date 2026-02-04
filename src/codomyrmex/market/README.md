# Market Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `market` module facilitates anonymous economic coordination. It implements "Reverse Auctions" where agents post demands without revealing identity, and "Demand Aggregation" to pool purchasing power.

## Key Capabilities

- **Reverse Auctions**: Users post what they want, providers bid. Identity is hidden (`ReverseAuction`).
- **Demand Aggregation**: Multiple users' identical demands are bundled for bulk negotiation (`DemandAggregator`).
- **Transaction History**: Track participation anonymously.

## Core Components

- `ReverseAuction`: Manages the auction lifecycle (Open -> Bid -> Close/Cancel).
- `DemandAggregator`: Grouping logic for bulk requests.
- `Bid`: Data structure for provider offers.

## Navigation

- **Full Documentation**: [docs/modules/market/](../../../docs/modules/market/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
