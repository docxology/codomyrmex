# Edge Computing Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Edge deployment, IoT gateways, and latency-sensitive patterns.

## Key Features

- **EdgeNodeStatus** — Status of an edge node.
- **EdgeNode** — An edge computing node.
- **EdgeFunction** — A function deployable to edge.
- **SyncState** — State synchronization data.
- **EdgeSynchronizer** — Synchronize state between edge and cloud.
- **EdgeRuntime** — Runtime for edge function execution.
- `from_data()` — from data
- `get_local_state()` — get local state
- `update_local()` — Update local state.
- `apply_remote()` — Apply remote state if newer.

## Quick Start

```python
from codomyrmex.edge_computing import EdgeNodeStatus, EdgeNode, EdgeFunction

# Initialize
instance = EdgeNodeStatus()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `EdgeNodeStatus` | Status of an edge node. |
| `EdgeNode` | An edge computing node. |
| `EdgeFunction` | A function deployable to edge. |
| `SyncState` | State synchronization data. |
| `EdgeSynchronizer` | Synchronize state between edge and cloud. |
| `EdgeRuntime` | Runtime for edge function execution. |
| `EdgeExecutionError` | Error during edge function execution. |
| `EdgeCluster` | Manage a cluster of edge nodes. |

### Functions

| Function | Description |
|----------|-------------|
| `from_data()` | from data |
| `get_local_state()` | get local state |
| `update_local()` | Update local state. |
| `apply_remote()` | Apply remote state if newer. |
| `get_pending_changes()` | Get changes to sync to remote. |
| `confirm_sync()` | Confirm changes synced. |
| `deploy()` | Deploy a function to edge. |
| `undeploy()` | Undeploy a function. |
| `invoke()` | Invoke an edge function. |
| `list_functions()` | list functions |
| `register_node()` | Register an edge node. |
| `deregister_node()` | Deregister a node. |
| `get_node()` | get node |
| `get_runtime()` | get runtime |
| `list_nodes()` | list nodes |
| `deploy_to_all()` | Deploy function to all nodes. |
| `heartbeat()` | Update node heartbeat. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k edge_computing -v
```

## Navigation

- **Source**: [src/codomyrmex/edge_computing/](../../../src/codomyrmex/edge_computing/)
- **Parent**: [Modules](../README.md)
