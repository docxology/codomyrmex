# Agent Guidelines - CI/CD Automation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Continuous integration and deployment pipeline automation.

## Key Classes

- **PipelineBuilder** — Build CI/CD pipelines
- **WorkflowGenerator** — Generate GitHub Actions/GitLab CI
- **StageRunner** — Run pipeline stages
- **ArtifactManager** — Manage build artifacts

## Agent Instructions

1. **Fail fast** — Run quick checks first
2. **Cache dependencies** — Speed up builds
3. **Parallelize** — Run independent stages in parallel
4. **Version artifacts** — Tag artifacts with version
5. **Notify on failure** — Alert on failed builds

## Common Patterns

```python
from codomyrmex.ci_cd_automation import (
    PipelineBuilder, WorkflowGenerator, ArtifactManager
)

# Build pipeline
pipeline = PipelineBuilder("main")
pipeline.add_stage("lint", ["ruff check ."])
pipeline.add_stage("test", ["pytest"])
pipeline.add_stage("build", ["python -m build"])
pipeline.add_stage("deploy", ["./deploy.sh"], on_branch="main")

# Generate GitHub Actions workflow
generator = WorkflowGenerator("github")
workflow = generator.from_pipeline(pipeline)
workflow.save(".github/workflows/ci.yml")

# Manage artifacts
artifacts = ArtifactManager()
artifacts.upload("dist/*.whl", version="1.0.0")
```

## Testing Patterns

```python
# Verify pipeline structure
pipeline = PipelineBuilder("test")
pipeline.add_stage("build", ["echo build"])
assert "build" in pipeline.stages

# Verify workflow generation
generator = WorkflowGenerator("github")
workflow = generator.from_pipeline(pipeline)
assert "jobs" in workflow.to_dict()
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
