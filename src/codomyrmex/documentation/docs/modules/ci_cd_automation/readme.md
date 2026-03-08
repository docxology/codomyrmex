# CI/CD Automation Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

CI/CD pipeline management module providing end-to-end continuous integration and deployment capabilities. This module supports programmatic pipeline construction, multi-platform workflow generation, and robust deployment orchestration.

### Key Components

- **`PipelineBuilder`** -- Programmatically create CI/CD pipelines with stages and jobs.
- **`WorkflowGenerator`** -- Generate platform-specific CI/CD workflows (GitHub Actions, GitLab CI).
- **`PipelineManager`** -- Orchestrate and execute pipelines locally with parallel/sequential support.
- **`DeploymentOrchestrator`** -- Manage deployments to target environments (dev, staging, prod).
- **`ArtifactManager`** -- Handle build artifacts with versioning and storage.
- **`RollbackManager`** -- Implement automated and manual rollback strategies.
- **`PipelineOptimizer`** -- Identify and apply performance improvements.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **PLAN** | Review pipeline dependencies and workflow structure | Direct Python import |
| **EXECUTE** | Trigger CI/CD pipelines for automated build and test | Direct Python import |
| **VERIFY** | Confirm pipeline results meet quality gates | Direct Python import |

PAI's EXECUTE phase triggers CI/CD workflows for automated validation. Engineer agents manage pipeline configuration during BUILD; QATester validates pipeline outputs during VERIFY.

## Key Exports

### Pipeline Management

- **`PipelineBuilder(name)`** -- Builder for creating pipelines programmatically.
- **`WorkflowGenerator(platform)`** -- Generator for CI/CD workflow files.
- **`PipelineManager(workspace_dir)`** -- Orchestrator for local pipeline execution.
- **`create_pipeline(config_path)`** -- Create a pipeline from a configuration file.
- **`run_pipeline(pipeline_name)`** -- Execute a pipeline with full orchestration.

### Deployment Orchestration

- **`DeploymentOrchestrator(config_path)`** -- Manages deployment lifecycle.
- **`manage_deployments(config_path)`** -- Convenience function for deployment orchestration.
- **`Deployment`** -- Deployment configuration and status.
- **`Environment`** -- Target environment definition.

### Artifact Management

- **`ArtifactManager(storage_dir)`** -- Manage build artifacts with versioning.

### Pipeline Monitoring & Optimization

- **`PipelineMonitor`** -- Tracks pipeline execution health and metrics.
- **`PipelineOptimizer`** -- Analyzes and optimizes pipeline performance.
- **`RollbackManager`** -- Manages rollback operations for failed deployments.

## Quick Start

```python
from codomyrmex.ci_cd_automation import PipelineBuilder, WorkflowGenerator

# Build a pipeline
builder = PipelineBuilder("my-ci")
builder.add_stage("lint", ["ruff check ."])
builder.add_stage("test", ["pytest"], dependencies=["lint"])
pipeline = builder.build()

# Generate GitHub Actions workflow
generator = WorkflowGenerator("github")
workflow = generator.from_pipeline(pipeline)
workflow.save(".github/workflows/ci.yml")
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k ci_cd_automation -v
```

## Navigation

- **Full Documentation**: [docs/modules/ci_cd_automation/](../../../docs/modules/ci_cd_automation/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
