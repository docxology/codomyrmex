# Resource Configuration Guide

This document describes the structure of `resources.json`, resource types, allocation policies, and provides example configurations.

## Overview

The ResourceManager manages system resources (CPU, memory, disk, network, external APIs, etc.) and their allocation to tasks and workflows. Resource configuration is stored in `resources.json` and loaded automatically when ResourceManager is initialized.

## Resources.json Structure

### Root Object

```json
{
  "resources": {
    "resource_id": {
      "id": "string",
      "name": "string",
      "type": "string",
      "description": "string",
      "status": "string",
      "capacity": {},
      "allocated": {},
      "limits": {},
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  },
  "updated_at": "ISO 8601 datetime"
}
```

### Resource Object Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique resource identifier |
| `name` | string | Yes | Human-readable resource name |
| `type` | string | Yes | Resource type (see ResourceType enum) |
| `description` | string | No | Resource description |
| `status` | string | No | Resource status (see ResourceStatus enum) |
| `capacity` | object | Yes | Resource capacity (e.g., {"cores": 8, "gb": 16}) |
| `allocated` | object | No | Currently allocated amounts |
| `limits` | object | No | Usage limits and quotas |
| `total_allocations` | integer | No | Total number of allocations |
| `total_usage_time` | float | No | Total usage time in seconds |
| `current_users` | array | No | List of current user IDs |
| `metadata` | object | No | Additional metadata |
| `tags` | array | No | Resource tags |
| `created_at` | string | No | Creation timestamp |
| `updated_at` | string | No | Last update timestamp |

## Resource Types

### CPU

CPU resources represent processor cores:

```json
{
  "id": "system_cpu",
  "name": "System CPU",
  "type": "cpu",
  "description": "System CPU cores",
  "status": "available",
  "capacity": {
    "cores": 8
  },
  "limits": {
    "max_cpu_cores": 8,
    "max_concurrent_users": null
  }
}
```

### Memory

Memory resources represent RAM:

```json
{
  "id": "system_memory",
  "name": "System Memory",
  "type": "memory",
  "description": "System RAM",
  "status": "available",
  "capacity": {
    "gb": 16.0
  },
  "limits": {
    "max_memory_gb": 12.8,
    "max_concurrent_users": null
  }
}
```

### Disk

Disk resources represent storage space:

```json
{
  "id": "system_disk",
  "name": "System Disk",
  "type": "disk",
  "description": "System disk space",
  "status": "available",
  "capacity": {
    "gb": 500.0
  },
  "limits": {
    "max_disk_gb": 450.0
  }
}
```

### Network

Network resources represent bandwidth:

```json
{
  "id": "system_network",
  "name": "System Network",
  "type": "network",
  "description": "Network bandwidth",
  "status": "available",
  "capacity": {
    "mbps": 1000
  },
  "limits": {
    "max_network_mbps": 1000
  }
}
```

### External API

External API resources represent API quotas:

```json
{
  "id": "openai_api",
  "name": "OpenAI API",
  "type": "external_api",
  "description": "OpenAI API quota",
  "status": "available",
  "capacity": {
    "requests_per_minute": 60,
    "tokens_per_minute": 10000
  },
  "limits": {
    "max_requests_per_minute": 60,
    "timeout_seconds": 30
  }
}
```

### GPU

GPU resources represent GPU units:

```json
{
  "id": "gpu_1",
  "name": "GPU Resource",
  "type": "gpu",
  "description": "NVIDIA GPU",
  "status": "available",
  "capacity": {
    "units": 1
  },
  "limits": {
    "max_concurrent_users": 1
  }
}
```

### Database

Database resources represent database connections:

```json
{
  "id": "postgres_db",
  "name": "PostgreSQL Database",
  "type": "database",
  "description": "PostgreSQL connection pool",
  "status": "available",
  "capacity": {
    "connections": 20
  },
  "limits": {
    "max_concurrent_users": 20,
    "timeout_seconds": 30
  }
}
```

## Resource Limits

The `limits` object defines usage constraints:

```json
{
  "limits": {
    "max_cpu_cores": null,
    "max_memory_gb": null,
    "max_disk_gb": null,
    "max_network_mbps": null,
    "max_concurrent_users": null,
    "max_requests_per_minute": null,
    "timeout_seconds": null
  }
}
```

### Limit Types

- `max_cpu_cores`: Maximum CPU cores per allocation
- `max_memory_gb`: Maximum memory per allocation
- `max_disk_gb`: Maximum disk space per allocation
- `max_network_mbps`: Maximum network bandwidth per allocation
- `max_concurrent_users`: Maximum number of concurrent users
- `max_requests_per_minute`: Maximum API requests per minute
- `timeout_seconds`: Default timeout for resource allocations

## Allocation Policies

### Resource Selection

When allocating resources, the ResourceManager:
1. Finds all resources of the requested type
2. Filters resources that can satisfy the requirement
3. Selects the resource with lowest utilization (best-fit)
4. Allocates the requested amount

### Allocation Failure Handling

If allocation fails:
- All partial allocations are rolled back
- Returns `None` to indicate failure
- Logs warning message with details

### Concurrent Access

- **Read mode**: Multiple tasks can read simultaneously
- **Write mode**: Exclusive access required
- **Exclusive mode**: Only one task can use the resource

## Complete Example Configuration

```json
{
  "resources": {
    "system_cpu": {
      "id": "system_cpu",
      "name": "System CPU",
      "type": "cpu",
      "description": "System CPU cores",
      "status": "available",
      "capacity": {
        "cores": 14
      },
      "allocated": {},
      "limits": {
        "max_cpu_cores": null,
        "max_memory_gb": null,
        "max_disk_gb": null,
        "max_network_mbps": null,
        "max_concurrent_users": null,
        "max_requests_per_minute": null,
        "timeout_seconds": null
      },
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "2025-10-22T23:46:35.441078+00:00",
      "updated_at": "2025-10-22T23:46:35.441080+00:00"
    },
    "system_memory": {
      "id": "system_memory",
      "name": "System Memory",
      "type": "memory",
      "description": "System RAM",
      "status": "available",
      "capacity": {
        "gb": 24.0
      },
      "allocated": {},
      "limits": {
        "max_memory_gb": 20.0
      },
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "2025-10-22T23:46:35.441140+00:00",
      "updated_at": "2025-10-22T23:46:35.441140+00:00"
    },
    "system_disk": {
      "id": "system_disk",
      "name": "System Disk",
      "type": "disk",
      "description": "System disk space",
      "status": "available",
      "capacity": {
        "gb": 121.3
      },
      "allocated": {},
      "limits": {
        "max_disk_gb": 100.0
      },
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "2025-10-22T23:46:35.441169+00:00",
      "updated_at": "2025-10-22T23:46:35.441169+00:00"
    },
    "system_network": {
      "id": "system_network",
      "name": "System Network",
      "type": "network",
      "description": "Network bandwidth",
      "status": "available",
      "capacity": {
        "mbps": 1000
      },
      "allocated": {},
      "limits": {
        "max_network_mbps": 1000
      },
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "2025-10-22T23:46:35.441193+00:00",
      "updated_at": "2025-10-22T23:46:35.441193+00:00"
    },
    "openai_api": {
      "id": "openai_api",
      "name": "OpenAI API",
      "type": "external_api",
      "description": "OpenAI API quota",
      "status": "available",
      "capacity": {
        "requests_per_minute": 60,
        "tokens_per_minute": 10000
      },
      "allocated": {},
      "limits": {
        "max_requests_per_minute": 60,
        "timeout_seconds": 30
      },
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "2025-10-22T23:46:35.441213+00:00",
      "updated_at": "2025-10-22T23:46:35.441213+00:00"
    }
  },
  "updated_at": "2025-10-24T02:20:25.444114+00:00"
}
```

## Default Resources

If `resources.json` doesn't exist or is empty, ResourceManager creates default resources:

- **system_cpu**: CPU cores (detected from system)
- **system_memory**: System RAM (detected from system or defaults to 8GB)
- **system_disk**: Disk space (detected from system or defaults to 100GB)
- **system_network**: Network bandwidth (defaults to 1Gbps)
- **openai_api**: OpenAI API quota (defaults to 60 req/min, 10000 tokens/min)

## Resource Allocation

### Allocating Resources

```python
from codomyrmex.project_orchestration import get_resource_manager

rm = get_resource_manager()

# Allocate resources for a task
allocation = rm.allocate_resources(
    user_id="task_123",
    requirements={
        "cpu": {"cores": 2},
        "memory": {"gb": 4},
        "external_api": {"requests_per_minute": 10}
    },
    timeout=300  # 5 minute timeout
)

if allocation:
    print(f"Allocated: {allocation}")
    # allocation = {"cpu": "system_cpu", "memory": "system_memory", "external_api": "openai_api"}
else:
    print("Allocation failed")
```

### Deallocating Resources

```python
# Deallocate all resources for a user
rm.deallocate_resources("task_123")

# Deallocate specific allocations
rm.deallocate_resources("task_123", allocation_ids=["alloc_1", "alloc_2"])
```

## Resource Usage Monitoring

### Get Resource Usage

```python
# System-wide usage
usage = rm.get_resource_usage()
print(f"Total resources: {usage['total_resources']}")
print(f"Utilization: {usage['utilization_summary']}")

# Specific resource usage
cpu_usage = rm.get_resource_usage("system_cpu")
print(f"CPU utilization: {cpu_usage['utilization']}")
print(f"Current users: {cpu_usage['current_users']}")
```

### Get User Allocations

```python
allocations = rm.get_user_allocations("task_123")
for alloc in allocations:
    print(f"Resource: {alloc['resource_name']}")
    print(f"Allocated: {alloc['allocated']}")
```

## Resource Health Checks

```python
health = rm.health_check()
print(f"Overall status: {health['overall_status']}")

for resource_id, resource_health in health['resources'].items():
    if not resource_health['healthy']:
        print(f"Issue with {resource_id}: {resource_health}")
```

## Custom Resources

### Adding Custom Resources

```python
from codomyrmex.project_orchestration import Resource, ResourceType, ResourceLimits

custom_resource = Resource(
    id="custom_api",
    name="Custom API",
    type=ResourceType.EXTERNAL_API,
    description="Custom external API",
    capacity={"requests_per_minute": 100, "tokens_per_minute": 50000},
    limits=ResourceLimits(
        max_requests_per_minute=100,
        timeout_seconds=60
    )
)

rm.add_resource(custom_resource)
```

### Removing Resources

```python
# Remove resource (only if not in use)
rm.remove_resource("custom_api")
```

## Best Practices

1. **Capacity Planning**: Set realistic capacity values based on actual system resources
2. **Limits**: Configure limits to prevent resource exhaustion
3. **Monitoring**: Regularly check resource utilization and health
4. **Cleanup**: Ensure resources are deallocated when tasks complete
5. **Timeouts**: Set appropriate timeouts for resource allocations
6. **Resource Types**: Use appropriate resource types for different resource kinds

## Related Documentation

- [Task Orchestration Guide](./task-orchestration-guide.md)
- [Dispatch and Coordination](./dispatch-coordination.md)
- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../../README.md)
