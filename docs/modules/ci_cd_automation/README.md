# CI/CD Automation Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Continuous integration and deployment pipeline automation.

## Key Features

- **Pipelines** — Define CI/CD pipelines
- **Workflows** — GitHub Actions/GitLab CI
- **Artifacts** — Manage build artifacts
- **Parallel** — Parallel stage execution

## Quick Start

```python
from codomyrmex.ci_cd_automation import PipelineBuilder

pipeline = PipelineBuilder("main")
pipeline.add_stage("lint", ["ruff check ."])
pipeline.add_stage("test", ["pytest"])
pipeline.add_stage("build", ["python -m build"])
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/ci_cd_automation/](../../../src/codomyrmex/ci_cd_automation/)
- **Parent**: [Modules](../README.md)
