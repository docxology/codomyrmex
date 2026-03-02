# Agent Guidelines - Deployment

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Container deployment, infrastructure automation, and environment management. Provides pluggable
deployment strategies (rolling, blue-green, canary) with health checking, canary analysis, and
snapshot-based rollback. Use `DeploymentManager` for all deployment orchestration; `RollbackManager`
for capturing and restoring snapshots; `HealthChecker` for multi-mode liveness and readiness probes.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `DeploymentManager`, `RollingDeployment`, `BlueGreenDeployment`, `CanaryDeployment`, `CanaryAnalyzer`, `HealthChecker`, `RollbackManager`, `DeploymentTarget` |
| `deployment_manager.py` | Orchestrate deployments; `deploy()` and `rollback()` entrypoints |
| `strategies/rolling.py` | Rolling (batch-by-batch) strategy |
| `strategies/blue_green.py` | Atomic swap blue-green strategy |
| `strategies/canary.py` | Percentage-based canary strategy |
| `canary_analyzer.py` | Metric-based canary promote/abort decision engine |
| `health_checker.py` | Multi-mode health verification (HTTP, process, custom) |
| `rollback_manager.py` | Snapshot creation and restoration |
| `gitops_synchronizer.py` | Sync infrastructure from Git state |
| `mcp_tools.py` | MCP tools: `deployment_execute`, `deployment_list_strategies`, `deployment_get_history` |

## Key Classes

- **DeploymentManager** — Orchestrate deployments using various strategies (`deploy()`, `rollback()`)
- **GitOpsSynchronizer** — Sync infrastructure and code from Git
- **RollingDeployment** — Gradual update strategy (batch-by-batch)
- **BlueGreenDeployment** — Atomic swap update strategy
- **CanaryDeployment** — Percentage-based update strategy
- **CanaryAnalyzer** — Metric-based canary decision maker (promote / abort)
- **HealthChecker** — Multi-mode health verification
- **RollbackManager** — Snapshot and restoration manager

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `deployment_execute` | Execute a named deployment strategy against one or more targets | TRUSTED |
| `deployment_list_strategies` | List all available deployment strategy names and their parameters | SAFE |
| `deployment_get_history` | Retrieve deployment history records for a given service | SAFE |

## Agent Instructions

1. **Validate targets** — Ensure deployment targets are reachable before beginning
2. **Use staging first** — Never deploy directly to production
3. **Rollback ready** — Always have a rollback plan and test it
4. **Health checks** — Always include health checks in strategy execution
5. **Log everything** — Use the centralized logging system to capture deployment outcomes
6. **Prefer GitOps** — Use `GitOpsSynchronizer` for managing infrastructure as code

## Operating Contracts

- `deploy()` is the only public entrypoint — never instantiate strategies directly outside of tests
- `rollback()` requires a prior snapshot created by `RollbackManager.snapshot()`
- `HealthChecker` must be passed as argument; do not bypass health checks in production
- `CanaryAnalyzer` decisions are final — no manual override after `analyze()` returns `ABORT`
- **DO NOT** call `manager.promote()` — it does not exist; use `deploy()` with the new version

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

result = manager.deploy(
    service_name="frontend",
    version="v2.0",
    strategy=RollingDeployment(batch_size=1, delay_seconds=10),
    targets=targets
)

if not result.success:
    manager.rollback("frontend", "v1.9", RollingDeployment(), targets)
```

### Canary Analysis

```python
from codomyrmex.deployment import CanaryAnalyzer, CanaryDecision

analyzer = CanaryAnalyzer(promote_threshold=0.9)
report = analyzer.analyze(
    baseline={"error_rate": 0.01, "p99_latency": 150},
    canary={"error_rate": 0.012, "p99_latency": 155}
)

if report.decision == CanaryDecision.PROMOTE:
    # Proceed to full rollout via deploy()
    pass
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `deployment_execute`, `deployment_list_strategies`, `deployment_get_history` | TRUSTED |
| **Architect** | Read + Design | `deployment_list_strategies`, `deployment_get_history` — strategy review and pipeline design | OBSERVED |
| **QATester** | Validation | `deployment_list_strategies`, `deployment_get_history` — health verification, rollback testing | OBSERVED |
| **Researcher** | Read-only | `deployment_list_strategies`, `deployment_get_history` — inspect strategy catalog and history | SAFE |

### Engineer Agent
**Use Cases**: Executing deployments during EXECUTE phase, managing release automation, provisioning environments.

### Architect Agent
**Use Cases**: Designing deployment strategies (blue/green, canary), reviewing release pipelines, planning rollback architectures.

### QATester Agent
**Use Cases**: Verifying deployment success during VERIFY, confirming environment health, testing rollback procedures.

### Researcher Agent
**Use Cases**: Inspecting available deployment strategies and historical deployment records for analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
