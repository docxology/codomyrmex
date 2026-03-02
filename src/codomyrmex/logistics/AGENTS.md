# Agent Guidelines - Logistics

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Supply chain management, inventory tracking, and delivery optimization.

## Key Classes

- **InventoryManager** — Track inventory levels
- **ShipmentTracker** — Track shipments
- **RouteOptimizer** — Optimize delivery routes
- **WarehouseManager** — Warehouse operations

## Agent Instructions

1. **Track everything** — Full audit trail
2. **Optimize routes** — Use RouteOptimizer for efficiency
3. **Handle exceptions** — Plan for delays/shortages
4. **Batch updates** — Reduce API calls
5. **Alert on low stock** — Proactive notifications

## Common Patterns

```python
from codomyrmex.logistics import (
    InventoryManager, ShipmentTracker, RouteOptimizer
)

# Manage inventory
inventory = InventoryManager()
inventory.add_item("SKU-001", quantity=100, location="warehouse-a")
inventory.decrement("SKU-001", 5)  # Sold 5 units

# Check stock levels
low_stock = inventory.get_low_stock(threshold=10)
for item in low_stock:
    notify_reorder(item)

# Track shipments
tracker = ShipmentTracker()
tracker.create_shipment("order-123", items=["SKU-001"])
status = tracker.get_status("order-123")

# Optimize delivery routes
optimizer = RouteOptimizer()
route = optimizer.optimize(deliveries, start_location)
```

## Testing Patterns

```python
# Verify inventory tracking
inventory = InventoryManager()
inventory.add_item("A", quantity=10)
inventory.decrement("A", 3)
assert inventory.get_quantity("A") == 7

# Verify route optimization
optimizer = RouteOptimizer()
route = optimizer.optimize([loc1, loc2, loc3])
assert len(route.stops) == 3
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Task logistics, workflow coordination, notification dispatching, scheduling | TRUSTED |
| **Architect** | Read + Design | Logistics pipeline design, workflow dependency review, scheduling architecture | OBSERVED |
| **QATester** | Validation | Workflow completion verification, notification delivery testing, scheduling correctness | OBSERVED |

### Engineer Agent
**Use Cases**: Coordinating workflow logistics during EXECUTE, dispatching notifications, scheduling tasks.

### Architect Agent
**Use Cases**: Designing logistics pipelines, reviewing workflow dependencies, planning notification strategies.

### QATester Agent
**Use Cases**: Verifying workflow completion during VERIFY, confirming notification delivery.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
