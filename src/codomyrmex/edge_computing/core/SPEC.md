# edge_computing/core — Technical Specification

## Overview

Three modules providing the foundational layer for edge computing: `models.py` (data types and enums), `cluster.py` (multi-node orchestration), and `runtime.py` (per-node function execution with metrics).

## Architecture

`models.py` defines pure data types. `EdgeRuntime` wraps a single `EdgeNode` and manages function deploy/invoke. `EdgeCluster` manages multiple nodes, each backed by an `EdgeRuntime` instance.

## Key Classes

### EdgeNodeStatus (Enum)

Values: `ONLINE`, `OFFLINE`, `DEGRADED`, `SYNCING`, `MAINTENANCE`.

### ResourceUsage

| Property | Type | Description |
|----------|------|-------------|
| `cpu_percent` | `float` | CPU utilization 0-100 |
| `memory_mb` / `memory_max_mb` | `float` | Current and max memory |
| `memory_percent` | `float` (property) | Derived percentage |
| `is_overloaded` | `bool` (property) | True if CPU > 90% or memory > 90% |

### EdgeNode

| Field | Type | Default |
|-------|------|---------|
| `id` / `name` | `str` | required |
| `location` | `str` | `""` |
| `status` | `EdgeNodeStatus` | `ONLINE` |
| `capabilities` | `list[str]` | `[]` |
| `resources` | `ResourceUsage` | default |
| `max_functions` | `int` | `10` |

Methods: `heartbeat()`, `is_healthy` (property), `has_capability(cap)`, `to_dict()`.

### EdgeFunction

Fields: `id`, `name`, `handler` (Callable), `memory_mb` (128), `timeout_seconds` (30), `environment` (dict), `required_capabilities` (list). Method: `can_run_on(node) -> bool`.

### EdgeCluster (cluster.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `register_node` | `(node: EdgeNode)` | None |
| `deregister_node` | `(node_id: str)` | `bool` |
| `heartbeat` | `(node_id: str)` | None |
| `deploy_to_all` | `(function: EdgeFunction)` | `int` (count) |
| `deploy_least_loaded` | `(function: EdgeFunction)` | `str \| None` (node_id) |
| `drain_node` | `(node_id: str)` | `bool` |
| `health` | `()` | `dict` (cluster summary) |
| `detect_stale_nodes` | `(timeout_seconds: float)` | `list[str]` |

### EdgeRuntime (runtime.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `deploy` | `(function: EdgeFunction)` | None |
| `undeploy` | `(function_id: str)` | `bool` |
| `invoke` | `(function_id: str, *args, **kwargs)` | `Any` |
| `warm_up` | `(function_id: str)` | `bool` |
| `get_function_stats` | `(function_id: str)` | `dict` |
| `summary` | `()` | `dict` |

Properties: `function_count`, `total_invocations`, `cold_start_count`.

### SyncState

Created via `SyncState.from_data(data, version)` which computes MD5 checksum. `verify()` recomputes and compares.

## Error Handling

- `EdgeExecutionError` raised when function invocation fails.
- `ValueError` raised when invoking a non-existent function.
- `TimeoutError` raised post-execution if elapsed time exceeds `timeout_seconds`.
