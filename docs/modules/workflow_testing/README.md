# Workflow Testing Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Workflow Testing module provides end-to-end workflow validation and integration testing capabilities. It offers a structured framework for defining multi-step test workflows with typed steps (assertions, waits, scripts, HTTP requests, conditionals), dependency-aware execution, retry logic, and comprehensive result reporting including pass rates and timing metrics.

## Key Features

- **Multi-Step Workflows**: Define sequential test workflows with typed steps and inter-step dependencies
- **Built-In Executors**: Assertion executor (equals, contains, not_null, greater_than, less_than), wait executor, and script executor
- **Retry Logic**: Configurable per-step retry counts with automatic re-execution on failure
- **Context Propagation**: Step outputs are stored in a shared context dictionary, accessible by subsequent steps via `step_{id}` keys
- **Result Reporting**: Comprehensive workflow results with pass/fail counts, pass rates, duration tracking, and per-step detail
- **Extensible Architecture**: Register custom step executors for new step types via the `StepExecutor` abstract base class
- **Fluent API**: Builder-style methods on `Workflow` for adding assertions and waits with method chaining

## Key Components

### Enums

| Component | Description |
|-----------|-------------|
| `WorkflowStepType` | Types of workflow steps: `HTTP_REQUEST`, `ASSERTION`, `WAIT`, `SCRIPT`, `CONDITIONAL` |
| `StepStatus` | Execution status: `PENDING`, `RUNNING`, `PASSED`, `FAILED`, `SKIPPED`, `ERROR` |

### Data Classes

| Component | Description |
|-----------|-------------|
| `WorkflowStep` | Defines a single step with id, name, type, config, dependencies, retry count, and timeout |
| `StepResult` | Result of a step execution with status, output, error message, duration, and retry count |
| `WorkflowResult` | Aggregate result with all step results, pass rate, total duration, and timestamps |
| `Workflow` | Complete workflow definition with steps, variables, tags, and fluent `add_step()`, `add_assertion()`, `add_wait()` methods |

### Executors

| Component | Description |
|-----------|-------------|
| `StepExecutor` | Abstract base class for implementing custom step executors |
| `AssertionExecutor` | Executes assertion steps supporting equals, contains, not_null, greater_than, and less_than comparisons |
| `WaitExecutor` | Executes timed wait steps with configurable duration |
| `ScriptExecutor` | Executes script steps via callable functions or Python expressions |

### Core

| Component | Description |
|-----------|-------------|
| `WorkflowRunner` | Orchestrates workflow execution: resolves executors, runs steps sequentially with retries, propagates context, and collects results |

## Quick Start

```python
from codomyrmex.workflow_testing import (
    Workflow, WorkflowStep, WorkflowStepType, WorkflowRunner
)

# Define a workflow
workflow = Workflow(id="api-test", name="API Validation Workflow")

# Add an assertion step
workflow.add_assertion(
    id="check-status",
    name="Verify status code",
    assertion_type="equals",
    expected=200,
    actual_key="response_status",
)

# Add a wait step
workflow.add_wait(id="pause", seconds=1.0)

# Add a custom step
workflow.add_step(WorkflowStep(
    id="validate-body",
    name="Check response body",
    step_type=WorkflowStepType.ASSERTION,
    config={"type": "contains", "actual": "success", "expected": "success"},
))

# Run the workflow
runner = WorkflowRunner()
result = runner.run(workflow, initial_context={"response_status": 200})

print(f"Status: {result.status.value}")
print(f"Pass rate: {result.pass_rate:.1%}")
print(f"Duration: {result.duration_ms:.1f}ms")

# Register a custom executor
from codomyrmex.workflow_testing import StepExecutor

class HttpExecutor(StepExecutor):
    def execute(self, step, context):
        # Custom HTTP request logic
        ...

runner.register_executor(WorkflowStepType.HTTP_REQUEST, HttpExecutor())
```

## Related Modules

- [testing](../testing/) - Test fixtures and data generators for unit-level testing
- [ci_cd_automation](../ci_cd_automation/) - CI/CD pipeline management where workflow tests integrate
- [logging_monitoring](../logging_monitoring/) - Structured logging for workflow test diagnostics

## Navigation

- **Source**: [src/codomyrmex/workflow_testing/](../../../src/codomyrmex/workflow_testing/)
- **Parent**: [docs/modules/](../README.md)
