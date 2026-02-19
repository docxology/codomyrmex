# deployment/strategies

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Deployment strategy implementations. Provides pluggable deployment strategies including rolling updates, blue-green switching, and canary rollouts with configurable health checks, batch sizing, and automatic rollback support.

## Key Exports

### Enums

- **`DeploymentState`** -- Deployment lifecycle states: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `ROLLED_BACK`, `PAUSED`

### Data Classes

- **`DeploymentTarget`** -- A deployment target (server, pod, etc.) with ID, name, address, health status, current version, and metadata
- **`DeploymentResult`** -- Result of a deployment operation with success flag, counts of updated/failed targets, duration in milliseconds, final state, and error list

### Abstract Base Class

- **`DeploymentStrategy`** -- ABC defining `deploy()` and `rollback()` interfaces. Both accept a list of targets, a version string, and a deploy function callback

### Strategy Implementations

- **`RollingDeployment`** -- Updates targets in configurable batch sizes with inter-batch delay and optional health checks. Rollback reuses the deploy path with the previous version
- **`BlueGreenDeployment`** -- Deploys to all targets (green environment), then atomically switches traffic via a configurable `switch_fn`. Only switches if all deployments succeed. Rollback is an instant traffic switch back to blue
- **`CanaryDeployment`** -- Gradual percentage-based rollout through configurable stages (default: 10%, 25%, 50%, 100%) with per-stage health validation and a success threshold (default 95%). Automatically halts if success rate drops below threshold. Rollback delegates to a rolling strategy

### Factory Function

- **`create_strategy()`** -- Factory that creates a deployment strategy by type string (`"rolling"`, `"blue_green"`, `"canary"`) with keyword arguments forwarded to the constructor

## Directory Contents

- `__init__.py` - Strategy ABC, three implementations, data classes, and factory function (367 lines)
- `strategies.py` - Extended strategy utilities
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [deployment](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
