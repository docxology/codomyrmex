# Agent Guidelines - CI/CD Automation

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Continuous integration and deployment pipeline automation for the Codomyrmex platform. Provides
programmatic pipeline construction (`PipelineBuilder`), workflow file generation for GitHub Actions
and GitLab CI (`WorkflowGenerator`), local and remote pipeline execution (`PipelineManager`),
deployment orchestration across environments (`DeploymentOrchestrator`), and rollback management
(`RollbackManager`). No MCP tools — accessed exclusively via direct Python import.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports all classes and functions listed below |
| `pipeline/` | `PipelineBuilder`, `PipelineManager`, `PipelineJob`, `PipelineStage`, `WorkflowGenerator`, `ArtifactManager` |
| `deployment_orchestrator.py` | `DeploymentOrchestrator`, `manage_deployments()`, `Deployment`, `Environment` |
| `pipeline/pipeline_monitor.py` | `PipelineMonitor`, `PipelineReport`, `monitor_pipeline_health()`, `generate_pipeline_reports()` |
| `rollback_manager.py` | `RollbackManager`, `RollbackStrategy`, `handle_rollback()` |
| `performance_optimizer.py` | `PipelineOptimizer`, `optimize_pipeline_performance()` |
| `exceptions.py` | `PipelineError`, `BuildError`, `DeploymentError`, `ArtifactError`, `StageError`, `RollbackError` |

## Key Classes

- **PipelineBuilder** — Programmatically build CI/CD pipelines with stages
- **WorkflowGenerator** — Generate GitHub Actions/GitLab CI configuration files
- **PipelineManager** — Run pipeline stages locally or trigger external workflows
- **PipelineMonitor** — Real-time pipeline monitoring and health checks
- **DeploymentOrchestrator** — Manage deployments across multiple environments
- **ArtifactManager** — Manage build artifacts with versioning
- **RollbackManager** — Automated and manual rollback of failed deployments
- **PipelineOptimizer** — Performance analysis and optimization suggestions

## Agent Instructions

1. **Fail fast** — Run quick lint/type-check stages before slow tests
2. **Cache dependencies** — Speed up builds with dependency caching
3. **Parallelize** — Run independent stages in parallel via `PipelineManager`
4. **Version artifacts** — Tag artifacts with version using `ArtifactManager`
5. **Notify on failure** — Alert on failed builds via event bus integration
6. **Monitor health** — Use `PipelineMonitor` for real-time status in long-running pipelines

## Operating Contracts

- `PipelineBuilder.build()` returns a `Pipeline` — pass it to `PipelineManager.run_pipeline()`
- `DeploymentOrchestrator` stages are ordered: `create_deployment()` → `deploy()` → optionally `handle_rollback()`
- `ArtifactManager.upload()` requires artifacts to exist at the glob path before upload
- `RollbackManager` requires a prior deployment record to roll back to
- **DO NOT** run deployment stages without health checks; always include a monitor step

## Common Patterns

### Pipeline Build and Execution

```python
from codomyrmex.ci_cd_automation import (
    PipelineBuilder, WorkflowGenerator, ArtifactManager,
    PipelineManager
)

# Build pipeline
builder = PipelineBuilder("main")
builder.add_stage("lint", ["ruff check ."])
builder.add_stage("test", ["pytest"])
builder.add_stage("build", ["python -m build"])
builder.add_stage("deploy", ["./deploy.sh"], on_branch="main")
pipeline = builder.build()

# Generate GitHub Actions workflow
generator = WorkflowGenerator("github")
workflow = generator.from_pipeline(pipeline)
workflow.save(".github/workflows/ci.yml")

# Run locally
mgr = PipelineManager()
mgr.pipelines["main"] = pipeline
results = mgr.run_pipeline("main")
print(f"Status: {results.status}")
```

### Deployment Orchestration

```python
from codomyrmex.ci_cd_automation import manage_deployments

orchestrator = manage_deployments("deploy_config.yaml")
orchestrator.create_deployment("webapp", "1.0.0", "staging", ["app.zip"])
orchestrator.deploy("webapp")
```

## Testing Patterns

```python
# Verify pipeline structure
builder = PipelineBuilder("test")
builder.add_stage("build", ["echo build"])
pipeline = builder.build()
assert "build" in [s.name for s in pipeline.stages]

# Verify workflow generation
generator = WorkflowGenerator("github")
workflow = generator.from_pipeline(pipeline)
assert "jobs" in workflow.to_dict()
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | None — Python import only | TRUSTED |
| **Architect** | Read + Design | None — pipeline design review via Python API | OBSERVED |
| **QATester** | Validation | None — pipeline status validation via Python API | OBSERVED |
| **Researcher** | Read-only | None — inspect pipeline configurations | SAFE |

### Engineer Agent
**Use Cases**: Pipeline management during BUILD/EXECUTE, workflow triggering, CI/CD configuration, deployment orchestration.

### Architect Agent
**Use Cases**: Pipeline design review, workflow dependency analysis, CI/CD architecture planning.

### QATester Agent
**Use Cases**: Pipeline status validation during VERIFY, workflow output verification, CI health checks.

### Researcher Agent
**Use Cases**: Inspecting pipeline configurations and deployment histories for analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/ci_cd_automation.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/ci_cd_automation.cursorrules)
