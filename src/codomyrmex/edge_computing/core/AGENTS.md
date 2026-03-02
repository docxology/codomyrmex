# edge_computing/core — Agent Coordination

## Purpose

Defines the data models and orchestration layer for edge computing: node management, function deployment, cluster lifecycle, and state synchronization with checksum integrity.

## Key Components

| Component | Role |
|-----------|------|
| `EdgeNodeStatus` | Enum: `ONLINE`, `OFFLINE`, `DEGRADED`, `SYNCING`, `MAINTENANCE` |
| `ResourceUsage` | Tracks CPU%, memory (MB/max), disk, active function count; exposes `is_overloaded` |
| `EdgeNode` | Node with ID, location, capabilities, heartbeat tracking, health check, `to_dict()` |
| `EdgeFunction` | Deployable function with handler, memory/timeout constraints, required capabilities |
| `EdgeDeployment` | Assignment record linking function to node with invocation counter |
| `SyncState` | Versioned state dict with MD5 checksum; `from_data()` factory and `verify()` integrity check |
| `EdgeCluster` | Multi-node orchestrator: register/deregister, heartbeat, deploy (all/specific/least-loaded), drain, health |
| `EdgeRuntime` | Per-node function executor: deploy/undeploy/invoke with latency tracking, cold-start detection, warm-up |
| `InvocationMetrics` | Per-invocation record: duration, success, cold-start flag |

## Operating Contracts

- `EdgeNode.is_healthy` requires `ONLINE` status and heartbeat within 60 seconds.
- `EdgeFunction.can_run_on(node)` checks all `required_capabilities` against node capabilities.
- `EdgeCluster.deploy_least_loaded(fn)` selects the non-draining node with fewest deployed functions.
- `EdgeCluster.drain_node(id)` prevents new deployments but existing functions keep running.
- `EdgeRuntime.invoke(fn_id, *args)` tracks latency, cold-start status, and records `InvocationMetrics`. Raises `EdgeExecutionError` on failure.
- `SyncState.verify()` recomputes MD5 over `json.dumps(data, sort_keys=True)` and compares to stored checksum.

## Integration Points

- **Infrastructure**: `HealthMonitor`, `EdgeCache`, `EdgeMetrics`, `EdgeSynchronizer` consume core models.
- **Scheduling**: `EdgeScheduler` references function IDs managed by `EdgeRuntime`.

## Navigation

- **Parent**: [edge_computing README](../../edge_computing/README.md)
- **Siblings**: [infrastructure](../infrastructure/AGENTS.md) | [scheduling](../scheduling/AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
