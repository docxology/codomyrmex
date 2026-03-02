# Agent Guidelines - Deployment

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Container deployment, infrastructure automation, and environment management.

## Key Classes

- **DeploymentManager** — Orchestrate deployments using various strategies.
- **GitOpsSynchronizer** — Sync infrastructure and code from Git.
- **RollingDeployment** — Gradual update strategy.
- **BlueGreenDeployment** — Atomic swap update strategy.
- **CanaryDeployment** — Percentage-based update strategy.
- **CanaryAnalyzer** — Metric-based canary decision maker.
- **HealthChecker** — Multi-mode health verification.
- **RollbackManager** — Snapshot and restoration manager.

## Agent Instructions

1. **Validate targets** — Ensure deployment targets are reachable before beginning.
2. **Use staging first** — Never deploy directly to production.
3. **Rollback ready** — Always have a rollback plan and test it.
4. **Health checks** — Always include health checks in strategy execution.
5. **Log everything** — Use the centralized logging system to capture deployment outcomes.
6. **Prefer GitOps** — Use `GitOpsSynchronizer` for managing infrastructure as code.

## Common Patterns

### Performing a Rolling Deployment

```python
from codomyrmex.deployment import (
    DeploymentManager, RollingDeployment, DeploymentTarget
)

manager = DeploymentManager()
targets = [
    DeploymentTarget(id="node-1", name="app-1", address="10.0.0.1"),
    DeploymentTarget(id="node-2", name="app-2", address="10.0.0.2"),
]

# Simple rolling deployment
result = manager.deploy(
    service_name="frontend",
    version="v2.0",
    strategy=RollingDeployment(batch_size=1, delay_seconds=10),
    targets=targets
)

if not result.success:
    manager.rollback("frontend", "v1.9", RollingDeployment(), targets)
```

### Canary Analysis and Promotion

```python
from codomyrmex.deployment import CanaryAnalyzer, CanaryDecision

analyzer = CanaryAnalyzer(promote_threshold=0.9)
report = analyzer.analyze(
    baseline={"error_rate": 0.01, "p99_latency": 150},
    canary={"error_rate": 0.012, "p99_latency": 155}
)

if report.decision == CanaryDecision.PROMOTE:
    # Proceed to full rollout
    pass
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Deployment automation, release management, environment provisioning | TRUSTED |
| **Architect** | Read + Design | Deployment strategy review, environment architecture, release pipeline design | OBSERVED |
| **QATester** | Validation | Deployment health checks, rollback verification, environment correctness | OBSERVED |

### Engineer Agent
**Use Cases**: Executing deployments during EXECUTE phase, managing release automation, provisioning environments.

### Architect Agent
**Use Cases**: Designing deployment strategies (blue/green, canary), reviewing release pipelines.

### QATester Agent
**Use Cases**: Verifying deployment success during VERIFY, confirming environment health, testing rollback procedures.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
