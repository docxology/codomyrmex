# Edge Computing Module

**Version**: v0.1.0 | **Status**: Active

Edge deployment, IoT gateways, and latency-sensitive function execution.


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`EdgeNodeStatus`** — Status of an edge node.
- **`EdgeNode`** — An edge computing node.
- **`EdgeFunction`** — A function deployable to edge.
- **`SyncState`** — State synchronization data.
- **`EdgeSynchronizer`** — Synchronize state between edge and cloud.
- **`EdgeRuntime`** — Runtime for edge function execution.
- **`EdgeExecutionError`** — Error during edge function execution.
- **`EdgeCluster`** — Manage a cluster of edge nodes.

## Directory Structure

- `models.py` — Data models (EdgeNodeStatus, EdgeNode, EdgeFunction, SyncState, EdgeExecutionError)
- `runtime.py` — Edge function execution runtime (EdgeRuntime)
- `cluster.py` — Multi-node cluster management (EdgeCluster)
- `sync.py` — State synchronization between edge and cloud (EdgeSynchronizer)
- `metrics.py` — Invocation metrics and tracking (EdgeMetrics, InvocationRecord)
- `__init__.py` — Public API re-exports

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


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k edge_computing -v
```


## Documentation

- [Module Documentation](../../../docs/modules/edge_computing/README.md)
- [Agent Guide](../../../docs/modules/edge_computing/AGENTS.md)
- [Specification](../../../docs/modules/edge_computing/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
