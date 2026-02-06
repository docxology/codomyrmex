# Orchestrator Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Workflow orchestration and multi-step execution.

## Key Features

- **Workflows** — Define workflows
- **Steps** — Sequential/parallel
- **State** — State management
- **Retry** — Retry logic

## Quick Start

```python
from codomyrmex.orchestrator import Workflow, Step

workflow = Workflow("deployment")
workflow.add_step(Step("build", build_func))
workflow.add_step(Step("test", test_func))
workflow.add_step(Step("deploy", deploy_func))

result = workflow.run()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/orchestrator/](../../../src/codomyrmex/orchestrator/)
- **Parent**: [Modules](../README.md)
