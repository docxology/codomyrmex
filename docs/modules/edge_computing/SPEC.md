# Edge Computing — Functional Specification

**Module**: `codomyrmex.edge_computing`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Edge deployment, IoT gateways, and latency-sensitive patterns.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `EdgeNodeStatus` | Class | Status of an edge node. |
| `EdgeNode` | Class | An edge computing node. |
| `EdgeFunction` | Class | A function deployable to edge. |
| `SyncState` | Class | State synchronization data. |
| `EdgeSynchronizer` | Class | Synchronize state between edge and cloud. |
| `EdgeRuntime` | Class | Runtime for edge function execution. |
| `EdgeExecutionError` | Class | Error during edge function execution. |
| `EdgeCluster` | Class | Manage a cluster of edge nodes. |
| `from_data()` | Function | from data |
| `get_local_state()` | Function | get local state |
| `update_local()` | Function | Update local state. |
| `apply_remote()` | Function | Apply remote state if newer. |
| `get_pending_changes()` | Function | Get changes to sync to remote. |

## 3. Dependencies

See `src/codomyrmex/edge_computing/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.edge_computing import EdgeNodeStatus, EdgeNode, EdgeFunction, SyncState, EdgeSynchronizer
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k edge_computing -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/edge_computing/)
