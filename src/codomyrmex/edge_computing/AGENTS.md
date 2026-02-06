# Agent Guidelines - Edge Computing

## Module Overview

Edge node management, function deployment, and synchronization.

## Key Classes

- **EdgeNode** — Edge node representation
- **EdgeFunction** — Deployable edge function
- **EdgeRuntime** — Function execution runtime
- **EdgeCluster** — Cluster management
- **EdgeSynchronizer** — State synchronization

## Agent Instructions

1. **Design for offline** — Handle disconnected states
2. **Sync efficiently** — Delta sync, not full state
3. **Resource aware** — Consider edge constraints
4. **Local caching** — Cache at edge when possible
5. **Graceful degradation** — Work with reduced capability

## Common Patterns

```python
from codomyrmex.edge_computing import (
    EdgeNode, EdgeCluster, EdgeFunction, EdgeSynchronizer
)

# Define edge function
@EdgeFunction(resources={"memory": "256MB"})
def process_sensor_data(data):
    return analyze(data)

# Create cluster
cluster = EdgeCluster()
cluster.add_node(EdgeNode("edge-1", location="factory-a"))
cluster.add_node(EdgeNode("edge-2", location="factory-b"))

# Deploy function
cluster.deploy(process_sensor_data, to_nodes=["edge-1"])

# Synchronize state
sync = EdgeSynchronizer()
sync.sync_bidirectional(cloud_state, edge_state)
```

## Testing Patterns

```python
# Verify edge function
@EdgeFunction()
def test_func(x):
    return x * 2
assert test_func(5) == 10

# Verify cluster management
cluster = EdgeCluster()
cluster.add_node(EdgeNode("n1"))
assert len(cluster.nodes) == 1
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
