# Codomyrmex Agents -- src/codomyrmex/edge_computing/deployment

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Manages the deployment lifecycle of edge functions across a cluster using configurable strategies (rolling, blue-green, canary). Provides plan creation, execution with automatic rollback on failure, and deployment state tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `deployment.py` | `DeploymentStrategy` | Enum of available strategies: ROLLING, BLUE_GREEN, CANARY |
| `deployment.py` | `DeploymentState` | Enum of deployment lifecycle states: PENDING, IN_PROGRESS, COMPLETED, ROLLED_BACK, FAILED |
| `deployment.py` | `DeploymentPlan` | Dataclass capturing function, strategy, target nodes, canary percentage, and deployment progress |
| `deployment.py` | `DeploymentManager` | Orchestrates plan creation, strategy-based execution, and rollback across an `EdgeCluster` |

## Operating Contracts

- `DeploymentManager` requires an `EdgeCluster` instance at construction time; it delegates all runtime operations to the cluster.
- `create_plan` defaults to targeting all ONLINE nodes if no explicit `target_nodes` list is provided.
- Rolling deployment stops and rolls back on the first node failure when `rollback_on_error` is True.
- Blue-green deployment deploys to all targets simultaneously and only rolls back after all attempts complete.
- Canary deployment splits targets into a canary subset (controlled by `canary_percent`) and remaining nodes, deploying canary first.
- `rollback` undeploys the function from all successfully deployed nodes and sets state to ROLLED_BACK.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `edge_computing.core.cluster.EdgeCluster`, `edge_computing.core.models.EdgeFunction`, `edge_computing.core.models.EdgeNodeStatus`
- **Used by**: Higher-level deployment orchestration and CI/CD pipelines

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Siblings**: [core](../core/AGENTS.md) | [infrastructure](../infrastructure/AGENTS.md) | [scheduling](../scheduling/AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
