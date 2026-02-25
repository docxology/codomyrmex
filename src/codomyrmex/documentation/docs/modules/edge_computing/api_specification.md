# Edge Computing API Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## 1. Overview

The `edge_computing` module provides edge deployment, function execution, state synchronization, and cluster management for latency-sensitive workloads. It models edge nodes, deployable functions, and cloud-edge synchronization with conflict resolution.

## 2. Core Components

### 2.1 Enums

- **`EdgeNodeStatus`**: Node health states -- `ONLINE`, `OFFLINE`, `DEGRADED`, `SYNCING`.

### 2.2 Data Classes

**`EdgeNode`**: Represents a physical or virtual edge node.
- `id: str`, `name: str`, `location: str = ""`, `status: EdgeNodeStatus = ONLINE`.
- `capabilities: list[str]` -- Node capabilities (e.g., `["gpu", "camera"]`).
- `metadata: dict[str, Any]`, `last_heartbeat: datetime`.

**`EdgeFunction`**: A function deployable to edge nodes.
- `id: str`, `name: str`, `handler: Callable[..., Any]`.
- `memory_mb: int = 128`, `timeout_seconds: int = 30`.
- `environment: dict[str, str]` -- Environment variables.

**`SyncState`**: State synchronization snapshot.
- `version: int`, `data: dict[str, Any]`, `checksum: str`, `updated_at: datetime`.
- Class method: `SyncState.from_data(data, version)` -- Creates state with MD5 checksum.

### 2.3 Edge Synchronizer

```python
from codomyrmex.edge_computing import EdgeSynchronizer, SyncState

sync = EdgeSynchronizer()

# Update local state
state = sync.update_local({"sensor_data": [1, 2, 3]})

# Apply remote state (accepts if version is newer)
remote = SyncState.from_data({"sensor_data": [4, 5, 6]}, version=5)
applied = sync.apply_remote(remote)  # -> bool

# Sync workflow
changes = sync.get_pending_changes()   # -> list[dict]
sync.confirm_sync(up_to_version=3)     # Remove confirmed changes

current = sync.get_local_state()       # -> SyncState | None
```

### 2.4 Edge Runtime

```python
from codomyrmex.edge_computing import EdgeRuntime, EdgeNode, EdgeFunction

node = EdgeNode(id="edge-01", name="warehouse-sensor")
runtime = EdgeRuntime(node)

func = EdgeFunction(id="fn-1", name="process-image", handler=my_handler)
runtime.deploy(func)
result = runtime.invoke("fn-1", image_data)
runtime.undeploy("fn-1")  # -> bool
runtime.list_functions()   # -> list[EdgeFunction]
```

### 2.5 Edge Cluster

```python
from codomyrmex.edge_computing import EdgeCluster, EdgeNodeStatus

cluster = EdgeCluster()

# Node management
cluster.register_node(node)
cluster.deregister_node("edge-01")  # -> bool
cluster.heartbeat("edge-01")        # Updates timestamp + sets ONLINE

# Queries
cluster.get_node("edge-01")         # -> EdgeNode | None
cluster.get_runtime("edge-01")      # -> EdgeRuntime | None
cluster.list_nodes()                 # -> list[EdgeNode]
cluster.list_nodes(status=EdgeNodeStatus.ONLINE)  # Filter by status

# Deploy to all nodes
count = cluster.deploy_to_all(func)  # -> int (number of nodes deployed to)
```

### 2.6 Invocation Metrics

**`InvocationRecord`**: Record of a single function invocation.
- `function_id: str`, `node_id: str`, `duration_ms: float`, `success: bool`.
- `timestamp: datetime` (defaults to `now()`), `error: str` (defaults to `""`).

**`EdgeMetrics`**: Track and query invocation metrics.

```python
from codomyrmex.edge_computing import EdgeMetrics, InvocationRecord

metrics = EdgeMetrics()

# Record invocations
metrics.record(InvocationRecord(
    function_id="fn-1", node_id="edge-01",
    duration_ms=42.5, success=True
))

# Query metrics
metrics.total_invocations()                    # -> int
metrics.total_invocations(function_id="fn-1")  # -> int (filtered)
metrics.success_rate()                         # -> float (0-100)
metrics.avg_latency_ms()                       # -> float
metrics.error_count()                          # -> int
metrics.summary()                              # -> dict with all above
```

## 3. Error Handling

| Exception | Raised When |
|:----------|:------------|
| `EdgeExecutionError` | Function invocation fails (wraps original exception) |
| `ValueError` | Function ID not found in runtime |
| `TimeoutError` | Function exceeds its `timeout_seconds` |

`EdgeExecutionError` chains the original exception via `from e` for full traceback access.

## 4. Thread Safety

`EdgeSynchronizer` is thread-safe via `threading.Lock`. `EdgeRuntime` and `EdgeCluster` are not inherently thread-safe; external synchronization is needed for concurrent access.

## 5. Integration Points

- **service_mesh**: Route edge function calls through service proxy for resilience.
- **streaming**: Stream edge sensor data via topic-based streams.
- **chaos_engineering**: Test edge node failure and network partition scenarios.
- **metrics**: Track function invocation latency and node health.

## 6. Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
