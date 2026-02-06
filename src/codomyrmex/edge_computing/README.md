# Edge Computing Module

**Version**: v0.1.0 | **Status**: Active

Edge deployment, IoT gateways, and latency-sensitive function execution.

## Quick Start

```python
from codomyrmex.edge_computing import (
    EdgeNode, EdgeFunction, EdgeCluster, EdgeSynchronizer, EdgeNodeStatus
)

# Create an edge cluster
cluster = EdgeCluster()

# Register edge nodes
node = EdgeNode(
    id="edge-01",
    name="Factory Floor Gateway",
    location="Building A",
    capabilities=["gpu", "camera"]
)
cluster.register_node(node)

# Deploy functions to edge
def process_sensor(data: dict) -> dict:
    return {"processed": True, "value": data["temp"] * 1.8 + 32}

func = EdgeFunction(
    id="sensor-proc",
    name="Process Sensor Data",
    handler=process_sensor,
    memory_mb=256,
    timeout_seconds=5
)
cluster.deploy_to_all(func)

# Invoke on edge
runtime = cluster.get_runtime("edge-01")
result = runtime.invoke("sensor-proc", {"temp": 25})
```

## Exports

| Class | Description |
|-------|-------------|
| `EdgeNode` | Edge node with id, location, status, capabilities |
| `EdgeNodeStatus` | Enum: online, offline, degraded, syncing |
| `EdgeFunction` | Deployable function with handler, memory, timeout |
| `EdgeRuntime` | Execute functions on an edge node |
| `EdgeCluster` | Manage multiple edge nodes |
| `EdgeSynchronizer` | Sync state between edge and cloud |
| `SyncState` | Versioned state with checksum |
| `EdgeExecutionError` | Error during edge execution |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
