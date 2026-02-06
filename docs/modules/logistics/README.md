# Logistics Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Supply chain, inventory, and delivery optimization utilities.

## Key Features

- **Inventory** — Track stock levels
- **Shipments** — Shipment tracking
- **Routes** — Route optimization
- **Alerts** — Low stock alerts

## Quick Start

```python
from codomyrmex.logistics import InventoryManager, RouteOptimizer

inventory = InventoryManager()
inventory.add_item("SKU-001", quantity=100)

optimizer = RouteOptimizer()
route = optimizer.optimize(deliveries, start_location)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/logistics/](../../../src/codomyrmex/logistics/)
- **Parent**: [Modules](../README.md)
