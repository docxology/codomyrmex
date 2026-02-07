# Edge Computing Module — Agent Coordination

## Purpose

Edge deployment, IoT gateways, and latency-sensitive patterns.

## Key Capabilities

- **EdgeNodeStatus**: Status of an edge node.
- **EdgeNode**: An edge computing node.
- **EdgeFunction**: A function deployable to edge.
- **SyncState**: State synchronization data.
- **EdgeSynchronizer**: Synchronize state between edge and cloud.
- `from_data()`: from data
- `get_local_state()`: get local state
- `update_local()`: Update local state.

## Agent Usage Patterns

```python
from codomyrmex.edge_computing import EdgeNodeStatus

# Agent initializes edge computing
instance = EdgeNodeStatus()
```

## Integration Points

- **Source**: [src/codomyrmex/edge_computing/](../../../src/codomyrmex/edge_computing/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
