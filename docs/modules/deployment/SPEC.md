# Deployment — Functional Specification

**Module**: `codomyrmex.deployment`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Deployment module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `DeploymentManager` | Class | High-level deployment manager for orchestrating deployments. |
| `GitOpsSynchronizer` | Class | GitOps synchronization manager. |
| `deploy()` | Function | Deploy a service version using the specified strategy. |
| `get_deployment_history()` | Function | Get history of deployments. |
| `rollback()` | Function | Rollback a service to a previous version. |
| `sync()` | Function | Synchronize from Git repository. |
| `get_version()` | Function | Get the current synced version via git rev-parse. |

### Submodule Structure

- `gitops/` — GitOps integration submodule.
- `health_checks/` — Deployment health check implementations.
- `manager/` — Deployment manager submodule.
- `rollback/` — Rollback management submodule.
- `strategies/` — Deployment strategies.

## 3. Dependencies

See `src/codomyrmex/deployment/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.deployment import DeploymentManager, GitOpsSynchronizer
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k deployment -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/deployment/)
