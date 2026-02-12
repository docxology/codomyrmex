# workflow_testing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

End-to-end workflow validation and testing framework. Defines multi-step workflows composed of typed steps (HTTP requests, assertions, waits, scripts, conditionals) with dependency tracking and retry support. Includes pluggable step executors, shared context propagation between steps, and aggregate pass/fail reporting with per-step duration metrics.

## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Enums

- **`WorkflowStepType`** -- Step classification: HTTP_REQUEST, ASSERTION, WAIT, SCRIPT, CONDITIONAL
- **`StepStatus`** -- Step execution status: PENDING, RUNNING, PASSED, FAILED, SKIPPED, ERROR

### Data Classes

- **`WorkflowStep`** -- A single workflow step with id, name, type, config dict, dependency list, retry count, and timeout
- **`StepResult`** -- Result of executing one step with status, output, error, duration in milliseconds, and retry count
- **`WorkflowResult`** -- Aggregate result of a complete workflow run with per-step results, pass rate, total duration, and timestamps
- **`Workflow`** -- A workflow test definition with ordered steps, variables, tags, and convenience methods for adding assertion and wait steps

### Executors

- **`StepExecutor`** -- Abstract base class for step executors; subclasses implement `execute(step, context) -> StepResult`
- **`AssertionExecutor`** -- Executes assertion steps supporting equals, contains, not_null, greater_than, and less_than comparisons
- **`WaitExecutor`** -- Executes wait/delay steps for a configurable number of seconds
- **`ScriptExecutor`** -- Executes script steps via callable functions or evaluated expressions with access to workflow context

### Core

- **`WorkflowRunner`** -- Main workflow execution engine that runs steps sequentially, propagates context between steps, applies retries on failure, and stops on error; supports custom executor registration

## Directory Contents

- `models.py` - Data models (WorkflowStep, StepResult, etc.)
- `executors.py` - Step executors (StepExecutor, AssertionExecutor, etc.)
- `runner.py` - Workflow runner logic (WorkflowRunner)
- `__init__.py` - Public API re-exports
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Detailed API documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Quick Start

```python
from codomyrmex.workflow_testing import WorkflowStepType, StepStatus, WorkflowStep

# Initialize WorkflowStepType
instance = WorkflowStepType()
```

## Navigation

- **Full Documentation**: [docs/modules/workflow_testing/](../../../docs/modules/workflow_testing/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
