# Resource Configuration Guide

This document describes how resources are defined, allocated, and monitored by the `ResourceManager` in `codomyrmex.logistics.orchestration.project` (formerly `codomyrmex.project_orchestration`).

## Overview

The ResourceManager tracks resources (compute, memory, API quota, storage, etc.) as numeric capacities and records allocations against them. It is configured in code: there is no `resources.json` that is loaded automatically. A new `ResourceManager()` starts with three default resources, and you add more with `add_resource()`. To keep resource definitions in a file, load them yourself with `Resource.from_dict()` (see [Custom Resources](#custom-resources)).

## Resource Object

`Resource` is a dataclass; `Resource.to_dict()` and `Resource.from_dict()` use this shape:

```json
{
  "id": "custom_api",
  "name": "Custom API",
  "type": "api_quota",
  "description": "Custom external API quota",
  "capacity": 200.0,
  "status": "available",
  "limits": {
    "min_value": 0,
    "max_value": 200.0,
    "default_allocation": 1.0,
    "burst_limit": null,
    "unit": "RPM"
  },
  "metadata": {}
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | Yes | Unique resource identifier (a UUID is generated when empty) |
| `name` | string | Yes | Human-readable resource name |
| `type` | string | Yes | A `ResourceType` value (see below) |
| `description` | string | No | Resource description |
| `capacity` | number | No | Total allocatable amount (default `1.0`) |
| `status` | string | No | A `ResourceStatus` value (default `available`) |
| `limits` | object | No | `ResourceLimits` fields: `min_value`, `max_value`, `default_allocation`, `burst_limit`, `unit` |
| `metadata` | object | No | Additional metadata |

`to_dict()` also emits the runtime fields `allocated` and `allocations`.

## Resource Types

`ResourceType` values: `compute`, `memory`, `storage`, `network`, `api_quota`, `database`, `custom`, `file_handle`, `thread`, `process`, `lock`.

`ResourceStatus` values: `available`, `allocated`, `busy`, `maintenance`, `offline`, `depleted`, `unknown`. Allocation is only attempted when a resource is `available` or `allocated`.

## Default Resources

Every new ResourceManager registers:

- **sys-compute** (`compute`): capacity 100.0, unit `vCPU`
- **sys-memory** (`memory`): capacity 1024.0, unit `MB`
- **api-global** (`api_quota`): capacity 1000.0, unit `RPM`

## Resource Allocation

### Allocating Resources

```python
from codomyrmex.logistics.orchestration.project import get_resource_manager

rm = get_resource_manager()

# Allocate one resource (returns a ResourceAllocation, or None if capacity is insufficient)
allocation = rm.allocate("sys-compute", requester_id="task_123", amount=2.0)

# Allocate several at once; "cpu" and "memory" map to sys-compute and sys-memory,
# any other key is used as a resource ID. All-or-nothing: partial allocations are rolled back.
allocations = rm.allocate_resources(
    "task_123",
    {
        "cpu": {"cores": 2},
        "memory": {"gb": 4},
        "api-global": {"amount": 10},
    },
)

if allocations:
    print(f"Allocated: {[a.resource_id for a in allocations]}")
else:
    print("Allocation failed")
```

### Releasing Resources

```python
# Release one allocation
rm.release(allocation.allocation_id)

# Release everything held by a requester
rm.deallocate_resources("task_123")
```

## Resource Usage Monitoring

```python
from codomyrmex.logistics.orchestration.project import ResourceType

usage = rm.get_usage("sys-compute")  # ResourceUsage or None
print(f"Utilization: {usage.utilization_percentage:.1f}%")
print(f"Available: {usage.available_amount} of {usage.total_capacity}")
print(f"Active allocations: {usage.allocation_count}")

for resource in rm.list_resources(type_filter=ResourceType.MEMORY):
    print(resource.name, resource.status.value, resource.allocated)
```

## Custom Resources

### Adding Custom Resources

```python
import json

from codomyrmex.logistics.orchestration.project import Resource, ResourceType
from codomyrmex.logistics.orchestration.project.resource_manager import ResourceLimits

custom_resource = Resource(
    id="custom_api",
    name="Custom API",
    type=ResourceType.API_QUOTA,
    description="Custom external API",
    capacity=100.0,
    limits=ResourceLimits(max_value=100.0, unit="RPM"),
)

rm.add_resource(custom_resource)

# Or load definitions you keep in your own JSON file
with open("resources.json") as f:
    for data in json.load(f)["resources"]:
        rm.add_resource(Resource.from_dict(data))
```

There is no `remove_resource()`; to take a resource out of service, set its `status` to `ResourceStatus.MAINTENANCE` or `ResourceStatus.OFFLINE`.

## Best Practices

1. **Capacity Planning**: Set realistic capacity values based on actual system resources
2. **Units**: Record the unit in `ResourceLimits.unit` so allocations are logged meaningfully
3. **Monitoring**: Regularly check utilization with `get_usage()`
4. **Cleanup**: Release allocations (or call `deallocate_resources()`) when tasks complete
5. **Resource Types**: Use appropriate resource types for different resource kinds

## Related Documentation

- [Task Orchestration Guide](./task-orchestration-guide.md)
- [Dispatch and Coordination](./dispatch-coordination.md)
- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
