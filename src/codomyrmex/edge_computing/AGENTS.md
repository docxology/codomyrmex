# Agent Guidelines - Edge Computing

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Edge node management, function deployment, and synchronization.

## Key Classes

- **EdgeNode** — Edge node representation
- **EdgeFunction** — Deployable edge function
- **EdgeRuntime** — Function execution runtime
- **EdgeCluster** — Cluster management
- **EdgeSynchronizer** — State synchronization
- **EdgeMetrics** — Invocation metrics tracking
- **InvocationRecord** — Single invocation record

## Agent Instructions

1. **Design for offline** — Handle disconnected states
2. **Sync efficiently** — Delta sync, not full state
3. **Resource aware** — Consider edge constraints
4. **Local caching** — Cache at edge when possible
5. **Graceful degradation** — Work with reduced capability

## Common Patterns

```python
from codomyrmex.edge_computing import (
    EdgeNode, EdgeCluster, EdgeFunction, EdgeRuntime,
    EdgeSynchronizer, EdgeMetrics, InvocationRecord, SyncState
)

# Create cluster and register nodes
cluster = EdgeCluster()
node = EdgeNode(id="edge-1", name="factory-sensor", location="factory-a")
cluster.register_node(node)

# Deploy function to all nodes
func = EdgeFunction(id="fn-1", name="process-data", handler=my_handler)
count = cluster.deploy_to_all(func)

# Invoke function via runtime
runtime = cluster.get_runtime("edge-1")
result = runtime.invoke("fn-1", sensor_data)

# Synchronize state
sync = EdgeSynchronizer()
state = sync.update_local({"readings": [1, 2, 3]})
remote = SyncState.from_data({"readings": [4, 5]}, version=5)
sync.apply_remote(remote)

# Track metrics
metrics = EdgeMetrics()
metrics.record(InvocationRecord(
    function_id="fn-1", node_id="edge-1",
    duration_ms=15.2, success=True
))
print(metrics.summary())
```

## Testing Patterns

```python
# Verify cluster management
cluster = EdgeCluster()
node = EdgeNode(id="n1", name="test-node")
cluster.register_node(node)
assert len(cluster.list_nodes()) == 1

# Verify runtime
runtime = EdgeRuntime(node)
func = EdgeFunction(id="fn-1", name="echo", handler=lambda x: x)
runtime.deploy(func)
assert runtime.invoke("fn-1", 42) == 42
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Deploy edge workloads, configure EdgeRuntime and EdgeCluster, manage node registration during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Edge topology design, synchronization strategy review, cluster architecture analysis

### QATester Agent
**Use Cases**: Unit and integration test execution, edge function invocation validation, sync state verification

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
