# Deployment Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `deployment` module provides deployment strategies, managers, and utilities for orchestrating service deployments. It supports rolling, blue-green, and canary deployment strategies, a high-level `DeploymentManager` for simplified deployment orchestration with rollback capability, and a `GitOpsSynchronizer` for synchronizing deployment configurations from Git repositories. The module is organized into submodules for strategies, health checks, rollback, manager, and gitops functionality.

## Key Features

- **Multiple deployment strategies**: Rolling, blue-green, and canary deployment patterns via dedicated strategy classes
- **Strategy factory**: `create_strategy()` function for instantiating strategies by name
- **High-level deployment manager**: `DeploymentManager` provides a simplified interface for deploying services with automatic target provisioning
- **Deployment history tracking**: Records all deployments with service name, version, strategy, success status, and targets updated
- **Built-in rollback**: `rollback()` method redeploys a previous version using the same strategy interface
- **GitOps synchronization**: `GitOpsSynchronizer` syncs deployment configurations from a Git repository branch
- **Health check integration**: Dedicated `health_checks` submodule for verifying deployment health
- **Deployment state management**: `DeploymentState` enum for tracking deployment lifecycle
- **Target-based deployment model**: `DeploymentTarget` dataclass with id, name, address, and version tracking
- **Strategy result reporting**: `DeploymentResult` dataclass capturing success status and target update counts
- **Convenience aliases**: `CanaryStrategy`, `BlueGreenStrategy`, `RollingStrategy` aliases for different naming preferences

## Key Components

| Component | Description |
|-----------|-------------|
| `DeploymentState` | Enum for deployment lifecycle states |
| `DeploymentTarget` | Dataclass representing a deployment target with id, name, address, and current version |
| `DeploymentResult` | Dataclass capturing deployment outcome: success status and number of targets updated |
| `DeploymentStrategy` | Abstract base class defining the strategy interface with a `deploy()` method |
| `RollingDeployment` | Strategy that updates targets incrementally one at a time |
| `BlueGreenDeployment` | Strategy that maintains two identical environments and switches traffic |
| `CanaryDeployment` | Strategy that gradually rolls out to a subset of targets before full deployment |
| `create_strategy` | Factory function to instantiate a deployment strategy by name |
| `DeploymentManager` | High-level orchestrator for deploying services with strategy selection, history tracking, and rollback |
| `GitOpsSynchronizer` | Synchronizes deployment configurations from a Git repository with branch and sync state management |
| `health_checks` | Submodule for deployment health verification |
| `strategies` | Submodule containing all deployment strategy implementations |
| `rollback` | Submodule with rollback utilities and procedures |

## Quick Start

```python
from codomyrmex.deployment import (
    DeploymentManager,
    GitOpsSynchronizer,
    RollingDeployment,
    BlueGreenDeployment,
    CanaryDeployment,
    create_strategy,
    DeploymentTarget,
)

# Simple deployment with default rolling strategy
manager = DeploymentManager()
success = manager.deploy("auth-service", "v2.1.0")
print(f"Deployment successful: {success}")

# Deploy with a specific strategy
canary = CanaryDeployment()
success = manager.deploy("api-gateway", "v3.0.0", strategy=canary)

# Use the strategy factory
strategy = create_strategy("blue_green")
success = manager.deploy("web-frontend", "v1.5.0", strategy=strategy)

# View deployment history
history = manager.get_deployment_history()
for entry in history:
    print(f"{entry['service']} -> {entry['version']} ({entry['strategy']}): {'OK' if entry['success'] else 'FAILED'}")

# Rollback to a previous version
manager.rollback("auth-service", "v2.0.0")

# GitOps synchronization
gitops = GitOpsSynchronizer(
    repo_url="https://github.com/org/deploy-configs",
    local_path="/tmp/deploy-configs",
    branch="main",
)
gitops.sync()
print(f"Synced version: {gitops.get_version()}")
print(f"Is synced: {gitops.is_synced()}")
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k deployment -v
```

## Related Modules

- [containerization](../containerization/) - Docker/Kubernetes management that provides deployment targets
- [ci_cd_automation](../ci_cd_automation/) - CI/CD pipeline management that triggers deployments
- [health_checks](../health_checks/) - Health verification integrated into deployment workflows
- [git_operations](../git_operations/) - Git workflow automation used by GitOps synchronization

## Navigation

- **Source**: [src/codomyrmex/deployment/](../../../src/codomyrmex/deployment/)
- **Parent**: [docs/modules/](../README.md)
