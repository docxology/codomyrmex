# Agent Guidelines - Edge Computing

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Edge node management, function deployment, scheduling, and synchronization. Provides a complete edge computing framework with `EdgeCluster` for multi-node orchestration (registration, heartbeat, drain, rebalance, auto-heal), `EdgeRuntime` for function execution with cold-start tracking and latency metrics, `EdgeScheduler` for periodic and one-shot job scheduling, `DeploymentManager` for rolling/canary/blue-green deployment strategies, `EdgeSynchronizer` for bidirectional delta sync, `HealthMonitor` for failure detection, and `EdgeCache` for local caching at the edge.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports all public classes: `EdgeNode`, `EdgeCluster`, `EdgeRuntime`, `EdgeFunction`, `EdgeScheduler`, `DeploymentManager`, `EdgeSynchronizer`, `HealthMonitor`, `EdgeCache`, etc. |
| `core/models.py` | `EdgeNode` (with `ResourceUsage`, `EdgeNodeStatus`), `EdgeFunction`, `SyncState`, `EdgeExecutionError` |
| `core/cluster.py` | `EdgeCluster` -- multi-node orchestration: register, deregister, heartbeat, deploy, drain, rebalance, auto-heal, health summary |
| `core/runtime.py` | `EdgeRuntime` -- function deploy/undeploy/invoke lifecycle with `InvocationMetrics`, cold-start detection, per-function stats |
| `scheduling/scheduler.py` | `EdgeScheduler` -- job lifecycle with `ScheduledJob`, `ScheduleType` (ONCE, INTERVAL, CRON_LIKE), `execute_tick()` |
| `deployment/deployment.py` | `DeploymentManager`, `DeploymentPlan`, `DeploymentState`, `DeploymentStrategy` |
| `infrastructure/sync.py` | `EdgeSynchronizer` -- bidirectional delta sync with `SyncState` |
| `infrastructure/cache.py` | `EdgeCache`, `CacheEntry` -- local caching at edge nodes |
| `infrastructure/health.py` | `HealthMonitor`, `HealthCheck` -- failure detection with recovery logic |

## Key Classes

- **EdgeNode** -- Node with `ResourceUsage` and health status. Tracks `id`, `name`, `location`, `status` (`EdgeNodeStatus`), and `last_heartbeat`.
- **EdgeNodeStatus** -- Enum: ONLINE, OFFLINE, DEGRADED.
- **EdgeFunction** -- Function with `id`, `name`, `handler` callable, capability constraints, and `timeout_seconds`.
- **EdgeRuntime** -- Per-node function execution runtime. Tracks invocation latency, cold-start events, and per-function call counts via `InvocationMetrics`.
- **EdgeCluster** -- Multi-node orchestrator. Provides `register_node()`, `deregister_node()`, `deploy_to_all()`, `deploy_least_loaded()`, `drain_node()`, `rebalance_cluster()`, `auto_heal()`, and `health()`.
- **EdgeSynchronizer** -- Bidirectional delta sync between edge and cloud with `update_local()` and `apply_remote()`.
- **EdgeScheduler** -- Job lifecycle management with `add_job()`, `remove_job()`, `get_due_jobs()`, and `execute_tick()`.
- **ScheduledJob** -- Job dataclass with `schedule_type`, `interval_seconds`, `max_runs`, `enabled`, and `exhausted` property.
- **DeploymentManager** -- Rolling/Canary/Blue-Green deployment strategies for edge functions.
- **HealthMonitor** -- Failure detection with recovery logic and periodic health checks.
- **EdgeCache** / **CacheEntry** -- Local caching with TTL support at edge nodes.
- **EdgeMetrics** / **InvocationRecord** -- Metrics collection and per-invocation recording.

## Agent Instructions

1. **Design for offline** -- Handle disconnected states gracefully.
2. **Sync efficiently** -- Use `is_delta=True` for partial updates.
3. **Resource aware** -- Check `is_overloaded` before large deployments.
4. **Auto-heal** -- Periodically call `cluster.auto_heal()` to prune stale nodes.
5. **Local caching** -- Cache at edge when possible.
6. **Graceful degradation** -- Work with reduced capability.

## Operating Contracts

- `EdgeCluster` must have at least one registered node before deploying functions. `deploy_to_all()` returns 0 if no nodes are registered.
- `EdgeCluster.register_node()` automatically creates an `EdgeRuntime` for the node -- do not create runtimes separately.
- `EdgeCluster.drain_node()` prevents new deployments to the node but existing functions continue to run.
- `EdgeCluster.auto_heal()` marks stale nodes (heartbeat older than 60s) as OFFLINE. Always call it periodically.
- `EdgeRuntime.invoke()` raises `ValueError` if the function is not deployed and `EdgeExecutionError` if execution fails.
- `EdgeRuntime.invoke()` logs a warning if the node `is_overloaded` but does not block execution.
- A function is "cold" until its first successful invocation. `warm_up()` pre-warms a function to avoid cold-start latency.
- `EdgeScheduler.execute_tick()` requires an `EdgeCluster` argument and executes all due jobs on any node that has the function deployed.
- `ScheduledJob.exhausted` is True when `run_count >= max_runs` -- the scheduler skips exhausted jobs automatically.
- `EdgeSynchronizer` sync is eventually consistent -- there is no strong ordering guarantee between local and remote state.
- **DO NOT** deploy to an edge node without first confirming its health via `cluster.health()` or `node.status == EdgeNodeStatus.ONLINE`.
- **DO NOT** bypass `EdgeCluster.deploy_to_node()` by directly calling `runtime.deploy()` in production -- the cluster tracks deployment state.
- **DO NOT** call `execute_tick()` without a valid cluster reference.

## Common Patterns

### Cluster Setup and Deployment

```python
from codomyrmex.edge_computing import (
    EdgeNode, EdgeCluster, EdgeFunction, EdgeRuntime
)

cluster = EdgeCluster()
node = EdgeNode(id="edge-1", name="factory-sensor", location="factory-a")
cluster.register_node(node)

func = EdgeFunction(id="fn-1", name="process-data", handler=my_handler)
count = cluster.deploy_to_all(func)

runtime = cluster.get_runtime("edge-1")
result = runtime.invoke("fn-1", sensor_data)
```

### Scheduled Jobs

```python
from codomyrmex.edge_computing import EdgeScheduler, ScheduleType

scheduler = EdgeScheduler()
job = scheduler.add_job(
    job_id="periodic-check",
    function_id="fn-1",
    schedule_type=ScheduleType.INTERVAL,
    interval_seconds=30.0,
    max_runs=100,
)

# In your main loop:
executed = scheduler.execute_tick(cluster)
```

### Health Monitoring and Auto-Heal

```python
cluster.heartbeat("edge-1")
stale = cluster.detect_stale_nodes(timeout_seconds=60.0)
healed = cluster.auto_heal()
health = cluster.health()
print(f"Online: {health['online']}/{health['total_nodes']}")
```

## Testing Patterns

```python
# Verify cluster management
cluster = EdgeCluster()
node = EdgeNode(id="n1", name="test-node")
cluster.register_node(node)
assert len(cluster.list_nodes()) == 1

# Verify runtime invocation
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
| **Researcher** | Read-only | Cluster health analysis, metrics inspection | SAFE |

### Engineer Agent
**Use Cases**: Deploy edge workloads, configure EdgeRuntime and EdgeCluster, manage node registration during BUILD/EXECUTE phases.

### Architect Agent
**Use Cases**: Edge topology design, synchronization strategy review, cluster architecture analysis.

### QATester Agent
**Use Cases**: Unit and integration test execution, edge function invocation validation, sync state verification.

### Researcher Agent
**Use Cases**: Analyze cluster health metrics, study invocation latency patterns, review scheduling statistics.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
