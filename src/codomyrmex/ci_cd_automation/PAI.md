# Personal AI Infrastructure -- CI/CD Automation Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The CI/CD Automation module provides end-to-end pipeline orchestration for building, testing, and deploying code artifacts across multiple languages and platforms. It exposes `PipelineManager` for multi-stage pipeline creation and execution, `DeploymentOrchestrator` for staged rollout with health checks and automated rollback, `PipelineOptimizer` for bottleneck identification and performance tuning, and `RollbackManager` for configurable rollback strategies (immediate, rolling, blue-green, canary). PAI agents invoke these capabilities during the BUILD, EXECUTE, and VERIFY phases to automate the full software delivery lifecycle.

## PAI Capabilities

### Multi-Language Build Orchestration

The `PipelineManager` creates and executes multi-stage pipelines from YAML configuration. It supports parallel and sequential job execution, dependency resolution, artifact management, and retry logic. The `build/` submodule provides `orchestrate_build_pipeline` for language-specific builds (Python, JavaScript, Go, Rust).

```python
from codomyrmex.ci_cd_automation import PipelineManager

manager = PipelineManager(workspace_dir="/tmp/pipelines")

# Create pipeline from YAML config
pipeline = manager.create_pipeline("pipeline.yaml")

# Pipeline YAML defines stages, jobs, and dependencies:
# stages:
#   - name: build
#     jobs:
#       - name: build-python
#         commands: ["uv sync", "uv run pytest"]
#       - name: build-js
#         commands: ["bun install", "bun run build"]
#   - name: test
#     depends_on: [build]
#     jobs:
#       - name: integration-tests
#         commands: ["uv run pytest -m integration"]

# Execute the pipeline with full stage orchestration
result = manager.run_pipeline(pipeline.name)

# Multi-language build via build submodule
from codomyrmex.ci_cd_automation.build import orchestrate_build_pipeline

build_result = orchestrate_build_pipeline(
    project_path="/path/to/project",
    language="python",
    output_dir="/tmp/artifacts"
)
```

### Pipeline Optimization

The `PipelineOptimizer` records execution metrics, analyzes performance trends, identifies bottlenecks, and generates optimization suggestions ranked by estimated impact and implementation effort.

```python
from codomyrmex.ci_cd_automation import PipelineOptimizer

optimizer = PipelineOptimizer(workspace_dir="/tmp/optimization")

# Record metrics from pipeline runs
optimizer.record_metric("duration", 245.3, "seconds", tags={"pipeline": "main-build"})
optimizer.record_metric("memory_mb", 1024.0, "MB", tags={"pipeline": "main-build"})
optimizer.record_metric("cpu_percent", 78.5, "%", tags={"pipeline": "main-build"})

# Analyze performance over the last 7 days
analysis = optimizer.analyze_performance("main-build", time_range=7)
# Returns: duration_stats, memory_stats, cpu_stats, trends, bottlenecks, suggestions

# Generate a targeted optimization plan
plan = optimizer.optimize_pipeline_performance(
    pipeline_name="main-build",
    target_improvement=0.2  # 20% faster target
)
# plan["current_performance"]["average_duration"] -> 245.3
# plan["current_performance"]["target_duration"]  -> 196.2
# plan["suggestions"] -> ranked list of OptimizationSuggestion objects
```

### Rollback Management

The `RollbackManager` creates and executes rollback plans using configurable strategies. Each strategy generates appropriate steps (stop services, restore backup, restart, verify health) with per-step timeouts and retry counts.

```python
from codomyrmex.ci_cd_automation import RollbackManager, RollbackStrategy

rollback_mgr = RollbackManager(workspace_dir="/tmp/rollbacks")

# Create a rollback plan for a failed deployment
plan = rollback_mgr.create_rollback_plan(
    deployment_id="deploy-v2.1.0-prod",
    strategy=RollbackStrategy.BLUE_GREEN,
    reason="Health check failures detected after deploy"
)
# plan.estimated_duration -> calculated from step timeouts
# plan.steps -> [stop_services, restore_backup, restart_services, verify_health]

# Execute the rollback asynchronously
import asyncio

execution = asyncio.run(rollback_mgr.execute_rollback("deploy-v2.1.0-prod"))
# execution.status -> "completed" or "failed"
# execution.completed_steps -> 4
# execution.errors -> [] (empty on success)

# Available strategies:
# RollbackStrategy.IMMEDIATE   - Stop and restore immediately
# RollbackStrategy.ROLLING     - Gradual rollback across instances
# RollbackStrategy.BLUE_GREEN  - Switch traffic to previous environment
# RollbackStrategy.CANARY      - Revert canary percentage first
# RollbackStrategy.MANUAL      - Generate plan for manual execution
```

### Deployment Orchestration

The `DeploymentOrchestrator` manages the full deployment lifecycle: environment registration, deployment creation with strategy selection, execution with health checks, and automated rollback on failure. Supports Docker, Kubernetes, and traditional deployment targets.

```python
from codomyrmex.ci_cd_automation import (
    DeploymentOrchestrator,
    Environment,
    EnvironmentType,
)

orchestrator = DeploymentOrchestrator(config_path="deployment_config.yaml")

# Register target environments
staging_env = Environment(
    name="staging",
    type=EnvironmentType.STAGING,
    host="staging.example.com",
    port=22,
    user="deploy",
    docker_registry="registry.example.com",
    health_checks=[
        {"url": "http://staging.example.com/health", "timeout": 30}
    ],
    pre_deploy_hooks=["./scripts/pre-deploy.sh"],
    post_deploy_hooks=["./scripts/smoke-test.sh"],
)

# Create a deployment
deployment = orchestrator.create_deployment(
    name="api-v2.1.0",
    version="2.1.0",
    environment_name="staging",
    artifacts=["dist/api-2.1.0.tar.gz"],
    strategy="rolling",
    rollback_on_failure=True,
)

# Execute the deployment
result = orchestrator.deploy("api-v2.1.0")
# result.status -> DeploymentStatus.SUCCESS or DeploymentStatus.FAILURE
# result.duration -> 42.7 (seconds)
# result.logs -> ["Deploying api-v2.1.0...", "Health check passed", ...]
```

## MCP Tools

No direct MCP tools via `@mcp_tool` decorator. Access CI/CD Automation capabilities through the `call_module_function` universal proxy tool exposed by the PAI MCP bridge.

```python
# Example: invoke ci_cd_automation via the proxy tool
from codomyrmex.agents.pai.mcp_bridge import call_tool

# Run a pipeline
result = call_tool(
    "call_module_function",
    module="ci_cd_automation",
    function="run_pipeline",
    args={"config_path": "pipeline.yaml"}
)

# Create a deployment
result = call_tool(
    "call_module_function",
    module="ci_cd_automation",
    function="manage_deployments",
    args={"config_path": "deployment_config.yaml"}
)

# Handle rollback
result = call_tool(
    "call_module_function",
    module="ci_cd_automation",
    function="handle_rollback",
    args={
        "deployment_id": "deploy-v2.1.0-prod",
        "strategy": "blue_green",
        "reason": "Post-deploy health check failures"
    }
)
```

Note: `call_module_function` is gated by the Trust Gateway. The trust level must be TRUSTED (set via `/codomyrmexTrust`) before executing destructive operations like `run_pipeline` or `deploy`.

## PAI Algorithm Phase Mapping

| Phase | CI/CD Automation Contribution |
|-------|-------------------------------|
| **OBSERVE** | `PipelineMonitor.monitor_pipeline_health()` reads current pipeline state; `generate_pipeline_reports()` surfaces execution history and failure trends for the Algorithm's context window |
| **THINK** | `PipelineOptimizer.analyze_performance()` provides bottleneck data and optimization suggestions that inform ISC criteria for build/deploy decisions |
| **PLAN** | `PipelineManager.create_pipeline()` defines the execution DAG; `RollbackManager.create_rollback_plan()` pre-computes the rollback strategy before any deployment begins |
| **BUILD** | `orchestrate_build_pipeline()` compiles, bundles, and packages artifacts for the target language; `validate_build_config()` and `validate_build_dependencies()` gate the build |
| **EXECUTE** | `PipelineManager.run_pipeline()` executes the full pipeline; `DeploymentOrchestrator.deploy()` rolls out artifacts to target environments with health checks |
| **VERIFY** | `PipelineMonitor.generate_pipeline_reports()` validates build status and test coverage; `DeploymentOrchestrator` runs post-deploy health checks; `RollbackManager` triggers automatic rollback if verification fails |
| **LEARN** | `PipelineOptimizer.record_metric()` captures execution telemetry; `PipelineReport` stores duration, success rates, and trends for future optimization passes |

## PAI Configuration

### Environment Variables

```bash
# CI provider integration
export CI_PROVIDER="github_actions"       # github_actions | gitlab_ci | jenkins | circleci

# Artifact storage
export ARTIFACT_REGISTRY="registry.example.com"
export ARTIFACT_STORAGE_PATH="/tmp/artifacts"

# Deployment targets
export DEPLOY_TARGET="staging"            # default environment for deployments
export DEPLOY_STRATEGY="rolling"          # rolling | blue_green | canary

# Pipeline configuration
export PIPELINE_CONFIG_PATH="pipeline.yaml"
export PIPELINE_WORKSPACE="/tmp/pipelines"
export PIPELINE_MAX_WORKERS=10            # ThreadPoolExecutor concurrency

# Rollback settings
export ROLLBACK_AUTO_TRIGGER="true"       # auto-rollback on health check failure
export ROLLBACK_DEFAULT_STRATEGY="immediate"
```

### Pipeline YAML Structure

```yaml
# pipeline.yaml
name: main-build
trigger:
  branches: [main, develop]
  events: [push, pull_request]

stages:
  - name: build
    jobs:
      - name: build-python
        language: python
        commands:
          - uv sync --all-extras
          - uv run black --check src/
          - uv run ruff check src/

  - name: test
    depends_on: [build]
    jobs:
      - name: unit-tests
        commands: ["uv run pytest -m unit"]
      - name: integration-tests
        commands: ["uv run pytest -m integration"]

  - name: deploy
    depends_on: [test]
    environment: staging
    strategy: rolling
    rollback_on_failure: true
```

## PAI Best Practices

### 1. Trigger Pipelines via call_module_function in EXECUTE Phase

PAI agents should invoke pipeline execution through the proxy tool during the EXECUTE phase, after the PLAN phase has defined the pipeline configuration and the THINK phase has validated ISC criteria.

```python
# In PAI EXECUTE phase: run the pipeline
result = call_tool(
    "call_module_function",
    module="ci_cd_automation",
    function="run_pipeline",
    args={"config_path": "pipeline.yaml"}
)

# Check result before proceeding to VERIFY
if result["status"] != "success":
    # Trigger rollback via the same proxy
    call_tool(
        "call_module_function",
        module="ci_cd_automation",
        function="handle_rollback",
        args={"deployment_id": result["deployment_id"], "strategy": "immediate"}
    )
```

### 2. Pre-Compute Rollback Plans as ISC Anti-Criteria

Before any deployment, the PLAN phase should define a rollback plan as an ISC anti-criterion. This ensures the Algorithm has an explicit exit strategy if verification fails.

```python
# In PAI PLAN phase: define rollback before deploying
rollback_mgr = RollbackManager()
plan = rollback_mgr.create_rollback_plan(
    deployment_id="deploy-v2.1.0-prod",
    strategy=RollbackStrategy.BLUE_GREEN,
    reason="Pre-computed rollback for v2.1.0 production deploy"
)
# ISC anti-criterion: "If post-deploy health checks fail within 5 minutes,
# execute blue-green rollback plan deploy-v2.1.0-prod"
```

### 3. Generate GitHub Actions Workflows from PAI BUILD Phase

PAI agents can generate CI workflow YAML during the BUILD phase by combining pipeline configuration with GitHub Actions syntax.

```python
# Generate GitHub Actions workflow from pipeline config
from codomyrmex.ci_cd_automation import PipelineManager

manager = PipelineManager()
pipeline = manager.create_pipeline("pipeline.yaml")

# The pipeline stages map to GitHub Actions jobs:
# stages[0] "build"  -> jobs.build (runs-on: ubuntu-latest)
# stages[1] "test"   -> jobs.test  (needs: [build])
# stages[2] "deploy" -> jobs.deploy (needs: [test], environment: staging)
```

### 4. Use PipelineOptimizer in LEARN Phase for Continuous Improvement

After each pipeline execution, record metrics so the optimizer can identify trends and suggest improvements in future THINK phases.

```python
# In PAI LEARN phase: capture execution telemetry
optimizer = PipelineOptimizer()
optimizer.record_metric("duration", result["duration"], "seconds",
                       tags={"pipeline": "main-build", "commit": "abc123"})
optimizer.record_metric("test_coverage", result["coverage"], "percent",
                       tags={"pipeline": "main-build"})
```

## Architecture Role

**Service Layer** -- The CI/CD Automation module sits in the Service Layer of the codomyrmex architecture, orchestrating higher-level workflows that compose Foundation and Core layer capabilities.

### Dependencies (consumed)

| Module | Relationship |
|--------|-------------|
| `containerization/` | Docker image builds, container scanning, runtime management |
| `testing/` | Test runner execution, coverage reporting |
| `git_operations/` | VCS hooks, commit metadata, branch management |
| `logging_monitoring/` | Structured logging via `get_logger()` for all pipeline operations |
| `environment_setup/` | Environment validation and dependency checking |
| `security/` | Security scanning integrated into pipeline stages |

### Consumers (consumed by)

| Module | Relationship |
|--------|-------------|
| `deployment/` | Production release orchestration using `DeploymentOrchestrator` |
| `orchestrator/` | Workflow engine triggers pipelines as workflow steps |

### Key Exports

| Export | Type | PAI Use |
|--------|------|---------|
| `PipelineManager` | Class | Create and execute multi-stage pipelines |
| `DeploymentOrchestrator` | Class | Manage staged deployments with health checks |
| `PipelineOptimizer` | Class | Analyze and optimize pipeline performance |
| `RollbackManager` | Class | Create and execute rollback plans |
| `PipelineMonitor` | Class | Track pipeline health and generate reports |
| `run_pipeline()` | Function | Convenience function for pipeline execution |
| `manage_deployments()` | Function | Convenience function returning configured orchestrator |
| `handle_rollback()` | Function | Convenience function for rollback execution |
| `optimize_pipeline_performance()` | Function | Convenience function for optimization analysis |

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
