# Deployment - API Specification

## Introduction

The Deployment module provides tools for managing application deployments, including various deployment strategies (canary, blue-green) and GitOps synchronization capabilities.

## Endpoints / Functions / Interfaces

### Class: `DeploymentManager`

- **Description**: Central manager for deployment operations.
- **Constructor**:
    - `strategy` (DeploymentStrategy, optional): Default deployment strategy.
    - `config` (dict, optional): Deployment configuration.
- **Methods**:

#### `deploy(target: str, version: str, options: dict | None = None) -> DeploymentResult`

- **Description**: Deploy a new version to the target environment.
- **Parameters/Arguments**:
    - `target` (str): Target environment (e.g., "production", "staging").
    - `version` (str): Version to deploy.
    - `options` (dict, optional): Deployment options.
- **Returns**:
    - `DeploymentResult`: Deployment outcome.

#### `rollback(target: str, version: str | None = None) -> DeploymentResult`

- **Description**: Rollback to a previous version.
- **Parameters/Arguments**:
    - `target` (str): Target environment.
    - `version` (str, optional): Version to rollback to. Defaults to previous version.
- **Returns**:
    - `DeploymentResult`: Rollback outcome.

#### `get_status(target: str) -> DeploymentStatus`

- **Description**: Get current deployment status.
- **Parameters/Arguments**:
    - `target` (str): Target environment.
- **Returns**:
    - `DeploymentStatus`: Current deployment status.

### Class: `DeploymentStrategy`

- **Description**: Base class for deployment strategies.
- **Methods**:
    - `execute(deployment: Deployment) -> DeploymentResult`: Execute the deployment.
    - `validate(deployment: Deployment) -> bool`: Validate deployment before execution.

### Class: `CanaryStrategy`

- **Description**: Canary deployment strategy with gradual traffic shifting.
- **Constructor**:
    - `initial_percentage` (float): Initial traffic percentage (0-100). Default: 10.
    - `increment` (float): Traffic increment per step. Default: 10.
    - `interval` (int): Seconds between increments. Default: 300.
    - `health_check_url` (str, optional): Health check endpoint.
- **Methods**: Inherits from `DeploymentStrategy`.

### Class: `BlueGreenStrategy`

- **Description**: Blue-green deployment with instant traffic switch.
- **Constructor**:
    - `switch_delay` (int): Delay before traffic switch in seconds. Default: 0.
    - `health_check_url` (str, optional): Health check endpoint.
- **Methods**: Inherits from `DeploymentStrategy`.

### Class: `GitOpsSynchronizer`

- **Description**: Synchronizes deployments with Git repository state.
- **Constructor**:
    - `repo_url` (str): Git repository URL.
    - `branch` (str): Branch to watch. Default: "main".
    - `path` (str): Path to deployment manifests. Default: "/".
- **Methods**:

#### `sync() -> SyncResult`

- **Description**: Synchronize current state with Git repository.
- **Returns**:
    - `SyncResult`: Synchronization result.

#### `watch(callback: Callable) -> None`

- **Description**: Watch for changes and trigger callbacks.
- **Parameters/Arguments**:
    - `callback` (Callable): Function to call on changes.

#### `get_diff() -> list[Change]`

- **Description**: Get differences between current state and repository.
- **Returns**:
    - `list[Change]`: List of detected changes.

## Data Models

### Model: `DeploymentResult`
- `success` (bool): Whether deployment succeeded.
- `version` (str): Deployed version.
- `target` (str): Target environment.
- `strategy` (str): Strategy used.
- `duration` (float): Deployment duration in seconds.
- `errors` (list[str] | None): Any errors encountered.

### Model: `DeploymentStatus`
- `target` (str): Target environment.
- `current_version` (str): Currently deployed version.
- `status` (str): Status (running, deployed, failed, rolling_back).
- `health` (str): Health status (healthy, degraded, unhealthy).
- `instances` (int): Number of running instances.

### Model: `Deployment`
- `id` (str): Unique deployment identifier.
- `target` (str): Target environment.
- `version` (str): Version being deployed.
- `strategy` (DeploymentStrategy): Deployment strategy.
- `created_at` (datetime): Creation timestamp.
- `metadata` (dict): Additional metadata.

## Authentication & Authorization

Deployment operations require appropriate credentials for target environments. Configure authentication via environment variables or configuration files.

## Rate Limiting

N/A - Deployment operations are not rate-limited but may have environment-specific constraints.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
