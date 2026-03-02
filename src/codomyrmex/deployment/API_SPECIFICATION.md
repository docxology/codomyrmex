# Deployment - API Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Introduction

The Deployment module provides tools for managing application deployments, including various deployment strategies (canary, blue-green, rolling), a high-level manager, and GitOps synchronization capabilities.

## Endpoints / Functions / Interfaces

### Class: `DeploymentManager`

- **Description**: Central manager for deployment operations.
- **Constructor**:
    - `config` (dict, optional): Deployment configuration.
- **Methods**:

#### `deploy(service_name: str, version: str, strategy: DeploymentStrategy | None = None, targets: list[DeploymentTarget] | None = None) -> DeploymentResult`

- **Description**: Deploy a new version of a service.
- **Parameters**:
    - `service_name` (str): Name of the service to deploy.
    - `version` (str): Version to deploy.
    - `strategy` (DeploymentStrategy, optional): Strategy to use. Defaults to `RollingDeployment`.
    - `targets` (list[DeploymentTarget], optional): List of targets. Defaults to auto-generated mocks if None.
- **Returns**:
    - `DeploymentResult`: Outcome of the deployment.

#### `rollback(service_name: str, previous_version: str, strategy: DeploymentStrategy | None = None, targets: list[DeploymentTarget] | None = None) -> DeploymentResult`

- **Description**: Rollback to a previous version.
- **Parameters**:
    - `service_name` (str): Service name.
    - `previous_version` (str): Version to rollback to.
    - `strategy` (DeploymentStrategy, optional): Strategy to use.
    - `targets` (list[DeploymentTarget], optional): List of targets.
- **Returns**:
    - `DeploymentResult`: Outcome of the rollback.

#### `get_active_version(service_name: str) -> str | None`

- **Description**: Get the currently active version for a service.
- **Returns**:
    - `str | None`: Active version or None.

### Class: `DeploymentStrategy` (Abstract)

- **Methods**:
    - `deploy(targets: list[DeploymentTarget], version: str, deploy_fn: Callable) -> DeploymentResult`: Execute deployment.
    - `rollback(targets: list[DeploymentTarget], previous_version: str, deploy_fn: Callable) -> DeploymentResult`: Execute rollback.

### Class: `RollingDeployment`

- **Constructor**:
    - `batch_size` (int): Number of targets per batch. Default: 1.
    - `delay_seconds` (float): Delay between batches. Default: 0.0.
    - `health_check` (Callable, optional): Health check function.

### Class: `BlueGreenDeployment`

- **Constructor**:
    - `switch_fn` (Callable, optional): Function to switch traffic.
    - `health_check` (Callable, optional): Health check function.

### Class: `CanaryDeployment`

- **Constructor**:
    - `stages` (list[float], optional): Traffic percentages per stage. Default: [10, 25, 50, 100].
    - `stage_duration_seconds` (float): Delay between stages. Default: 0.0.
    - `health_check` (Callable, optional): Health check function.
    - `success_threshold` (float): Success rate required to proceed. Default: 0.95.

### Class: `GitOpsSynchronizer`

- **Constructor**:
    - `repo_url` (str): Git repository URL.
    - `local_path` (str): Local path for the repository.
- **Methods**:
    - `sync(branch: str = "main") -> bool`: Synchronize with the remote repository.
    - `get_version() -> str | None`: Get the current commit SHA.
    - `checkout(revision: str) -> bool`: Checkout a specific revision.
    - `is_dirty() -> bool`: Check for uncommitted local changes.

## Data Models

### Model: `DeploymentTarget`
- `id` (str): Unique target identifier.
- `name` (str): Human-readable name.
- `address` (str): Network address.
- `healthy` (bool): Current health status.
- `version` (str | None): Currently deployed version.
- `metadata` (dict): Additional metadata.

### Model: `DeploymentResult`
- `success` (bool): Whether the operation succeeded.
- `targets_updated` (int): Number of targets successfully updated.
- `targets_failed` (int): Number of targets that failed update.
- `duration_ms` (float): Duration of the operation in milliseconds.
- `state` (DeploymentState): Final state (COMPLETED, FAILED, ROLLED_BACK).
- `errors` (list[str]): List of error messages.
- `metadata` (dict): Additional operation metadata.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS.md](AGENTS.md)
