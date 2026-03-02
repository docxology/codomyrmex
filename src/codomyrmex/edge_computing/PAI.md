# Personal AI Infrastructure — Edge Computing Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Edge Computing module provides PAI integration for edge node management, enabling AI agents to deploy and manage distributed edge infrastructure.

## PAI Capabilities

### Edge Deployment

Deploy functions to edge nodes via cluster:

```python
from codomyrmex.edge_computing import (
    EdgeCluster, EdgeFunction, EdgeNode, EdgeMetrics, InvocationRecord
)

# Create cluster and register nodes
cluster = EdgeCluster()
node = EdgeNode(id="edge-1", name="factory-sensor", location="factory-a")
cluster.register_node(node)

# Deploy function to all nodes
func = EdgeFunction(id="fn-1", name="process-data", handler=my_handler)
count = cluster.deploy_to_all(func)  # -> int (nodes deployed to)

# Invoke via runtime
runtime = cluster.get_runtime("edge-1")
result = runtime.invoke("fn-1", sensor_data)

# Track metrics
metrics = EdgeMetrics()
metrics.record(InvocationRecord(
    function_id="fn-1", node_id="edge-1",
    duration_ms=15.2, success=True
))
```

### State Synchronization

Keep edge and cloud in sync:

```python
from codomyrmex.edge_computing import EdgeSynchronizer, SyncState

sync = EdgeSynchronizer()

# Update local state
state = sync.update_local({"readings": [1, 2, 3]})

# Apply remote state (accepts if version is newer)
remote = SyncState.from_data({"readings": [4, 5]}, version=5)
applied = sync.apply_remote(remote)  # -> bool

# Get pending changes
changes = sync.get_pending_changes()
sync.confirm_sync(up_to_version=3)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `EdgeCluster` | Manage distributed edge nodes |
| `EdgeRuntime` | Deploy and invoke functions |
| `EdgeSynchronizer` | State consistency |
| `EdgeMetrics` | Invocation tracking |

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.edge_computing import ...`
- CLI: `codomyrmex edge_computing <command>`

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
