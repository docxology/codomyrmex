# deployment

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The deployment module provides deployment strategy implementations and orchestration for service rollouts. It supports rolling, blue-green, and canary deployment patterns with configurable health checks, batch sizing, traffic switching, and staged percentage-based rollouts. Includes a high-level deployment manager for simplified orchestration and a GitOps synchronizer for Git-based configuration management.


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Strategy Classes

- **`DeploymentState`** -- Enum representing deployment lifecycle states: PENDING, IN_PROGRESS, COMPLETED, FAILED, ROLLED_BACK, PAUSED.
- **`DeploymentTarget`** -- Dataclass representing a deployment target (server, pod) with id, name, address, health status, version, and metadata.
- **`DeploymentResult`** -- Dataclass capturing deployment outcomes: success flag, targets updated/failed counts, duration, errors, and state.
- **`DeploymentStrategy`** -- Abstract base class defining the `deploy()` and `rollback()` contract for all strategies.
- **`RollingDeployment`** -- Updates targets incrementally in configurable batch sizes with inter-batch delays and optional health checks.
- **`BlueGreenDeployment`** -- Deploys to all targets in a green environment, then atomically switches traffic. Supports instant rollback via traffic switch reversal.
- **`CanaryDeployment`** -- Gradual rollout through percentage-based stages (default: 10%, 25%, 50%, 100%) with configurable stage duration and success threshold (default 95%).
- **`create_strategy()`** -- Factory function that instantiates deployment strategies by name string ("rolling", "blue_green", "canary").

### Convenience Aliases

- **`CanaryStrategy`** -- Alias for `CanaryDeployment`
- **`BlueGreenStrategy`** -- Alias for `BlueGreenDeployment`
- **`RollingStrategy`** -- Alias for `RollingDeployment`

### Manager Classes

- **`DeploymentManager`** -- High-level orchestrator providing a simple `deploy()` / `rollback()` interface with deployment history tracking. Defaults to rolling strategy.
- **`GitOpsSynchronizer`** -- Synchronizes deployment configurations from a Git repository. Supports `sync()`, `get_version()` via git rev-parse, and `is_synced()` status checks.

### Submodules

- **`health_checks`** -- Health check utilities for deployment targets
- **`strategies`** -- All deployment strategy implementations
- **`rollback`** -- Rollback orchestration utilities

## Directory Contents

- `__init__.py` - Module entry point with `DeploymentManager`, `GitOpsSynchronizer`, and all exports
- `strategies/` - Strategy implementations (rolling, blue-green, canary) and factory function
- `health_checks/` - Health check utilities for verifying deployment target readiness
- `rollback/` - Rollback orchestration and automation
- `manager/` - Extended deployment management utilities
- `gitops/` - GitOps synchronization and Git-based configuration management
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Quick Start

```python
from codomyrmex.deployment import DeploymentManager, GitOpsSynchronizer

# Initialize DeploymentManager
instance = DeploymentManager()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k deployment -v
```

## Navigation

- **Full Documentation**: [docs/modules/deployment/](../../../docs/modules/deployment/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
