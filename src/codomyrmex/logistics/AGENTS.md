# Agent Guidelines - Logistics

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
