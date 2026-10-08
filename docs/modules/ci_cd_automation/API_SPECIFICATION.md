# CI/CD Automation - API Specification

## Introduction

This API specification documents the programmatic interfaces for the CI/CD Automation module of Codomyrmex. The module provides comprehensive continuous integration and deployment capabilities, including pipeline management, automated testing, deployment orchestration, and build automation for the Codomyrmex ecosystem.

## Functions

All functions below are importable from `codomyrmex.ci_cd_automation`.

### Function: `create_pipeline(config: str | os.PathLike[str] | Mapping[str, Any]) -> Pipeline`

- **Description**: Create a pipeline from a configuration file (YAML or JSON) or from the configuration itself as a mapping. A new `PipelineManager` parses the configuration into `Pipeline`, `PipelineStage` and `PipelineJob` objects.
- **Parameters**:
  - `config`: Path to a `.yaml`/`.yml` or JSON pipeline file, or a mapping with `name`, optional `description`, `variables`, `triggers`, `timeout` and a `stages` list (each stage has `name` and `jobs`; each job has `name` and `commands`).
- **Return Value**: The created `Pipeline`.
- **Errors**: Re-raises file, YAML and JSON errors (for example `FileNotFoundError`) after logging them. Use `validate_pipeline_config()` to check a mapping first.

### Function: `validate_pipeline_config(config: Mapping[str, Any]) -> tuple[bool, list[str]]`

- **Description**: Validate a pipeline configuration mapping without creating the pipeline.
- **Parameters**:
  - `config`: Pipeline configuration (`name`, `stages` with `jobs` that each define a non-empty `commands` list, optional `triggers` and `timeout`).
- **Return Value**: `(is_valid, errors)`; `errors` lists one message per problem.

### Function: `run_pipeline(pipeline_name: str, config_path: str | None = None, variables: dict[str, str] | None = None) -> Pipeline`

- **Description**: Run a pipeline synchronously and return it with execution results. Each call uses a fresh `PipelineManager`, so pass `config_path` to load the pipeline definition; use `PipelineManager` directly to run pipelines created earlier.
- **Parameters**:
  - `pipeline_name`: Name of the pipeline to run (the `name` in its configuration).
  - `config_path`: Path to the pipeline configuration file to load before running.
  - `variables`: Runtime variables that override the pipeline's `variables`.
- **Return Value**: The `Pipeline`, with `status`, `started_at`, `finished_at`, `duration` and per-stage/per-job status filled in.
- **Errors**: Raises `ValueError` when no pipeline named `pipeline_name` is loaded.

### Function: `manage_deployments(config_path: str | None = None) -> DeploymentOrchestrator`

- **Description**: Create a `DeploymentOrchestrator` and load environments from a YAML or JSON deployment configuration file when it exists. Use the orchestrator's `create_deployment()`, `deploy()`, `get_deployment_status()`, `list_deployments()` and `cancel_deployment()` methods to manage deployments.
- **Parameters**:
  - `config_path`: Path to the deployment configuration file (default: `deployment_config.yaml` in the current directory).
- **Return Value**: A configured `DeploymentOrchestrator`.

### Function: `monitor_pipeline_health(pipeline_name: str, workspace_dir: str | None = None) -> dict[str, Any]`

- **Description**: Return a health summary for a pipeline via `PipelineMonitor.get_pipeline_health()`.
- **Parameters**:
  - `pipeline_name`: Name of the pipeline to check.
  - `workspace_dir`: Workspace directory for monitor reports (default: current directory).
- **Return Value**:

    ```python
    {
        "pipeline_name": <str>,
        "status": <str>,
        "last_execution": <ISO-8601 timestamp>,
        "success_rate": <float>,
        "average_duration": <float>,
        "active_executions": <int>,
        "recent_failures": [<list>]
    }
    ```

- **Note**: The current implementation returns a fixed snapshot (`status` `"healthy"`); the values are not yet derived from recorded executions.

### Function: `generate_pipeline_reports(execution_id: str, report_types: list[ReportType], workspace_dir: str | None = None) -> dict[str, PipelineReport]`

- **Description**: Generate one `PipelineReport` per requested report type for an execution.
- **Parameters**:
  - `execution_id`: Execution ID to report on.
  - `report_types`: `ReportType` members (`EXECUTION`, `PERFORMANCE`, `QUALITY`, `COMPLIANCE`, `SUMMARY`) from `codomyrmex.ci_cd_automation.pipeline.pipeline_monitor`.
  - `workspace_dir`: Workspace directory for reports (default: current directory).
- **Return Value**: Mapping of `ReportType.value` to the generated `PipelineReport`.
- **Note**: `PipelineMonitor.generate_report()` currently fills reports with sample values rather than stored execution data.

### Function: `handle_rollback(deployment_id: str, strategy: RollbackStrategy = RollbackStrategy.IMMEDIATE, reason: str = "Deployment failure", workspace_dir: str | None = None) -> RollbackExecution`

- **Description**: Create a rollback plan for a deployment and execute it synchronously with a `RollbackManager`.
- **Parameters**:
  - `deployment_id`: ID of the deployment to roll back.
  - `strategy`: `RollbackStrategy` member (`IMMEDIATE`, `ROLLING`, `BLUE_GREEN`, `CANARY`, `MANUAL`).
  - `reason`: Reason recorded in the rollback plan.
  - `workspace_dir`: Workspace directory for `rollback_plans/` and `rollback_history/` (default: current directory).
- **Return Value**: The `RollbackExecution` record. If execution raises, the error is logged and a record with `status="failed"` and the message in `errors` is returned instead of raising.

### Function: `optimize_pipeline_performance(pipeline_name: str, target_improvement: float = 0.2, workspace_dir: str | None = None) -> dict[str, Any]`

- **Description**: Build a performance optimization plan from metrics recorded with `PipelineOptimizer.record_metric()`, and save it as JSON under the workspace.
- **Parameters**:
  - `pipeline_name`: Name of the pipeline to optimize.
  - `target_improvement`: Target duration reduction as a fraction (`0.2` = 20%).
  - `workspace_dir`: Workspace directory (default: current directory).
- **Return Value**: When duration metrics exist:

    ```python
    {
        "pipeline_name": <str>,
        "current_performance": {"average_duration": <float>, "target_duration": <float>, "target_improvement": <str>},
        "analysis_summary": {"bottlenecks_identified": <int>, "suggestions_available": <int>, "relevant_suggestions": <int>},
        "optimization_suggestions": [<OptimizationSuggestion>],
        "implementation_timeline": [{"suggestion": <str>, "effort": <str>, "duration_weeks": <int>, "start_week": <int>, "end_week": <int>, "priority": <int>}],
        "expected_outcome": {"estimated_duration_improvement": <float>, "new_estimated_duration": <float>}
    }
    ```

    Without recorded metrics it returns `{"pipeline_name": ..., "message": "Insufficient data for optimization analysis", "suggestions": []}`.

## Data Structures

All of these are dataclasses or enums exported from `codomyrmex.ci_cd_automation` (`ReportType` lives in `codomyrmex.ci_cd_automation.pipeline.pipeline_monitor`).

### Pipeline

`Pipeline(name, description="", stages=[], variables={}, triggers={}, timeout=7200, ...)` with execution fields `status` (`PipelineStatus`), `created_at`, `started_at`, `finished_at` and `duration`. `to_dict()` returns the JSON-ready form.

### PipelineStage

`PipelineStage(name, jobs=[], dependencies=[], environment={}, allow_failure=False, parallel=True, ...)` plus `status`, `start_time` and `end_time`.

### PipelineJob

`PipelineJob(name, commands, environment={}, artifacts=[], dependencies=[], timeout=3600, retry_count=0, allow_failure=False, ...)` plus `status`, `start_time`, `end_time`, `output` and `error`.

### Deployment

`Deployment(name, version, environment, artifacts, strategy="rolling", timeout=1800, rollback_on_failure=True, ...)` plus `status` (`DeploymentStatus`), timestamps, `duration`, `logs`, `metrics` and `previous_version`.

### Environment

`Environment(name, type, host, port=22, user="deploy", key_path=None, docker_registry=None, kubernetes_context=None, variables={}, pre_deploy_hooks=[], post_deploy_hooks=[], health_checks=[])`, where `type` is an `EnvironmentType` (`DEVELOPMENT`, `STAGING`, `PRODUCTION`, `TESTING`).

### PipelineReport

`PipelineReport(pipeline_name, execution_id, status, start_time, end_time, duration, stages_executed, jobs_executed, jobs_passed, jobs_failed, jobs_skipped, artifacts_created, metrics, errors, warnings)`.

### RollbackStrategy

Enum of rollback strategies: `IMMEDIATE`, `ROLLING`, `BLUE_GREEN`, `CANARY`, `MANUAL`.

### RollbackExecution

`RollbackExecution(execution_id, deployment_id, strategy, status, start_time, end_time=None, current_step=0, completed_steps=0, failed_steps=0, errors=[], warnings=[])`, defined in `codomyrmex.ci_cd_automation.rollback_manager`.

## Error Handling

The module's exceptions are exported from `codomyrmex.ci_cd_automation` and inherit from `codomyrmex.exceptions.CICDError`:

- `PipelineError(message, pipeline_name=None, stage=None)`: pipeline creation, configuration or execution failures
- `StageError`: a pipeline stage failed
- `BuildError(message, build_id=None, build_target=None, exit_code=None)`: build failures
- `DeploymentError`: deployment failures
- `ArtifactError`: artifact handling failures
- `RollbackError`: rollback failures

The convenience functions above also raise `ValueError` for unknown pipelines or environments and let file and parse errors propagate.

## Integration Patterns

### With Build Synthesis

```python
from codomyrmex.ci_cd_automation import create_pipeline
from codomyrmex.ci_cd_automation.build import validate_build_config

# Describe and validate the build target
build_config = {"name": "my_app", "build_commands": [["uv", "build"]]}
is_valid, errors = validate_build_config(build_config)

# Create pipeline with build stage (config mapping or YAML/JSON path)
pipeline = create_pipeline({
    "name": "app_pipeline",
    "stages": [
        {"name": "build", "jobs": [{"name": "build", "commands": ["uv build"]}]},
        {"name": "test", "jobs": [{"name": "test", "commands": ["uv run pytest"]}]},
        {"name": "deploy", "jobs": [...]},
    ],
})
```

### With Project Orchestration

```python
from codomyrmex.logistics.orchestration.project import execute_workflow
from codomyrmex.ci_cd_automation import run_pipeline

# Execute full CI/CD workflow
result = execute_workflow("ci_cd_pipeline", {
    "ci_cd_automation": {
        "pipeline_name": "production_deploy",
        "environment": "production",
        "quality_gates": True
    }
})
```

## Security Considerations

- **Credential Management**: Pipeline configurations may contain sensitive credentials
- **Access Control**: Pipeline execution should be restricted based on user permissions
- **Audit Logging**: All pipeline activities are logged for compliance and debugging
- **Secure Rollbacks**: Rollback operations maintain data integrity and security
- **Environment Isolation**: Deployments are isolated between environments for security

## Performance Characteristics

- **Scalability**: Supports concurrent pipeline execution
- **Resource Efficiency**: Intelligent resource allocation and cleanup
- **Monitoring Overhead**: Minimal performance impact from monitoring systems
- **Caching**: Build artifacts and test results are cached for efficiency
- **Parallelization**: Pipeline stages can execute in parallel when dependencies allow

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
