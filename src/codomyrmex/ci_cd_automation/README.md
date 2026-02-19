# CI/CD Automation Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

CI/CD pipeline management module providing end-to-end continuous integration and deployment capabilities. The `PipelineManager` creates and executes multi-stage pipelines composed of `PipelineStage` and `PipelineJob` definitions. `DeploymentOrchestrator` handles deployment to target environments with promotion and rollback support. `PipelineMonitor` tracks pipeline health and generates analytics reports. `RollbackManager` implements configurable rollback strategies for failed deployments. `PipelineOptimizer` identifies and applies performance improvements to pipeline execution. Includes a full exception hierarchy for granular error handling across pipeline, build, deployment, artifact, stage, and rollback operations.

## Key Exports

### Pipeline Management

- **`PipelineManager`** -- Creates, configures, and executes CI/CD pipelines
- **`create_pipeline()`** -- Create a new pipeline with stages and configuration
- **`run_pipeline()`** -- Execute a pipeline with full stage orchestration
- **`Pipeline`** -- Pipeline definition with stages, triggers, and metadata
- **`PipelineJob`** -- Individual job within a pipeline stage
- **`PipelineStage`** -- Pipeline stage grouping related jobs with ordering

### Deployment Orchestration

- **`DeploymentOrchestrator`** -- Manages deployment lifecycle across environments
- **`manage_deployments()`** -- Orchestrate deployments with environment promotion
- **`Deployment`** -- Deployment configuration with target, strategy, and status
- **`Environment`** -- Target environment definition (dev, staging, production)

### Pipeline Monitoring

- **`PipelineMonitor`** -- Tracks pipeline execution health and metrics
- **`monitor_pipeline_health()`** -- Monitor running pipelines for failures and bottlenecks
- **`generate_pipeline_reports()`** -- Generate analytics reports for pipeline performance
- **`PipelineReport`** -- Pipeline execution report with timing, success rates, and trends

### Rollback Management

- **`RollbackManager`** -- Manages rollback operations for failed deployments
- **`handle_rollback()`** -- Execute a rollback with the configured strategy
- **`RollbackStrategy`** -- Rollback strategy configuration (blue-green, canary, immediate)

### Performance Optimization

- **`PipelineOptimizer`** -- Analyzes and optimizes pipeline performance
- **`optimize_pipeline_performance()`** -- Apply optimizations to reduce pipeline duration

### Exceptions

- **`PipelineError`** -- Base exception for pipeline operations
- **`BuildError`** -- Error during build stage execution
- **`DeploymentError`** -- Error during deployment operations
- **`ArtifactError`** -- Error with build artifact handling
- **`StageError`** -- Error in a specific pipeline stage
- **`RollbackError`** -- Error during rollback execution

## Directory Contents

- `__init__.py` - Module entry point aggregating all manager and orchestrator exports
- `pipeline_manager.py` - `PipelineManager`, `Pipeline`, `PipelineStage`, and `PipelineJob`
- `deployment_orchestrator.py` - `DeploymentOrchestrator`, `Deployment`, and `Environment`
- `pipeline_monitor.py` - `PipelineMonitor` and `PipelineReport` for monitoring and analytics
- `rollback_manager.py` - `RollbackManager` and `RollbackStrategy` for rollback operations
- `performance_optimizer.py` - `PipelineOptimizer` for pipeline performance tuning
- `exceptions.py` - Exception hierarchy for CI/CD operations

## Quick Start

```python
from codomyrmex.ci_cd_automation import DeploymentStatus, EnvironmentType

# Create a DeploymentStatus instance
deploymentstatus = DeploymentStatus()

# Use EnvironmentType for additional functionality
environmenttype = EnvironmentType()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k ci_cd_automation -v
```


## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`build/`** | Build automation, scaffolding, and deployment orchestration |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/ci_cd_automation/](../../../docs/modules/ci_cd_automation/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
