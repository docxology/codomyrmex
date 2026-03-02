# Edge Deployment -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides deployment strategy management for edge functions across a cluster. Supports rolling, blue-green, and canary deployment patterns with automatic rollback on failure.

## Architecture

Uses a strategy pattern where `DeploymentManager` delegates execution to private methods based on the `DeploymentStrategy` enum. All strategies operate through the `EdgeCluster` API for actual function deployment, ensuring consistent node-level operations regardless of strategy.

## Key Classes

### `DeploymentStrategy` (Enum)

| Value | Description |
|-------|-------------|
| `ROLLING` | Deploy one node at a time, stop on failure |
| `BLUE_GREEN` | Deploy to all targets simultaneously |
| `CANARY` | Deploy to a percentage-based subset first, then the remainder |

### `DeploymentState` (Enum)

| Value | Description |
|-------|-------------|
| `PENDING` | Plan created but not yet executed |
| `IN_PROGRESS` | Deployment currently running |
| `COMPLETED` | All target nodes deployed successfully |
| `ROLLED_BACK` | Deployment reversed due to failure |
| `FAILED` | One or more nodes failed without full rollback |

### `DeploymentPlan` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `function` | `EdgeFunction` | The function being deployed |
| `strategy` | `DeploymentStrategy` | Chosen deployment strategy |
| `target_nodes` | `list[str]` | Node IDs to deploy to |
| `canary_percent` | `int` | Percentage of nodes for canary phase (default 10) |
| `rollback_on_error` | `bool` | Whether to rollback on first failure (default True) |
| `state` | `DeploymentState` | Current deployment lifecycle state |
| `deployed_nodes` | `list[str]` | Nodes where deployment succeeded |
| `failed_nodes` | `list[str]` | Nodes where deployment failed |

### `DeploymentManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_plan` | `function, strategy?, target_nodes?, canary_percent?` | `DeploymentPlan` | Create a deployment plan targeting ONLINE nodes by default |
| `execute` | `plan` | `DeploymentPlan` | Execute the plan using the configured strategy |
| `rollback` | `plan` | `int` | Undeploy function from all deployed nodes, return count |
| `list_deployments` | -- | `list[DeploymentPlan]` | Return all tracked deployment plans |

## Dependencies

- **Internal**: `edge_computing.core.cluster.EdgeCluster`, `edge_computing.core.models.EdgeFunction`, `edge_computing.core.models.EdgeNodeStatus`
- **External**: None (Python stdlib only)

## Constraints

- Rolling deploy stops at first failure when `rollback_on_error` is True; remaining nodes are skipped.
- Blue-green deploy attempts all nodes before deciding whether to rollback.
- Canary deploy uses `max(1, total * canary_percent // 100)` to ensure at least one canary node.
- Zero-mock: real cluster operations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Runtime errors during `deploy()` are caught per-node and tracked in `failed_nodes`.
- `rollback` iterates `deployed_nodes` and undeploys via the cluster runtime.
- All errors logged before propagation.
