# Workflow Testing -- Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Workflow testing framework providing step-based test definition, typed executors with assertion validation, shared context passing, and retry logic. Supports extensible step types via executor registration.

## Architecture

```
workflow/
  __init__.py    -- Re-exports from models, executors, runner; cli_commands()
  models.py      -- WorkflowStepType, StepStatus, WorkflowStep, StepResult, WorkflowResult, Workflow
  executors.py   -- StepExecutor ABC, AssertionExecutor, WaitExecutor, ScriptExecutor
  runner.py      -- WorkflowRunner with executor registry and retry logic
```

## Key Classes

### Workflow (dataclass)

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_step` | `(step: WorkflowStep) -> Workflow` | Append step (fluent) |
| `add_assertion` | `(id, name, assertion_type, expected, actual_key=None) -> Workflow` | Convenience: create and add assertion step |
| `add_wait` | `(id: str, seconds: float) -> Workflow` | Convenience: create and add wait step |

Fields: `id`, `name`, `description`, `steps: list[WorkflowStep]`, `variables: dict`, `tags: list[str]`

### WorkflowStep (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | required | Unique step identifier |
| `name` | `str` | required | Human-readable name |
| `step_type` | `WorkflowStepType` | required | Step category |
| `config` | `dict[str, Any]` | `{}` | Step-specific configuration |
| `dependencies` | `list[str]` | `[]` | Step IDs this depends on |
| `retry_count` | `int` | `0` | Max retry attempts |
| `timeout_seconds` | `float` | `30.0` | Step timeout supplied to an executor |
| `continue_on_error` | `bool` | `False` | Explicitly allow later steps after a non-passing result |

### WorkflowRunner

| Method | Signature | Description |
|--------|-----------|-------------|
| `register_executor` | `(step_type, executor) -> None` | Register custom executor for a step type |
| `run` | `(workflow, initial_context=None) -> WorkflowResult` | Execute workflow: iterate steps, pass context, handle retries |

Default executors: `ASSERTION -> AssertionExecutor`, `WAIT -> WaitExecutor`, `SCRIPT -> ScriptExecutor`

### StepExecutor (ABC)

| Method | Signature | Description |
|--------|-----------|-------------|
| `execute` | `(step: WorkflowStep, context: dict) -> StepResult` | Execute a single step (abstract) |

### AssertionExecutor

Assertion types supported via `step.config["type"]`:

| Type | Check |
|------|-------|
| `equals` | `actual == expected` |
| `contains` | `expected in str(actual)` |
| `not_null` | `actual is not None` |
| `greater_than` | `float(actual) > float(expected)` |
| `less_than` | `float(actual) < float(expected)` |

### WorkflowResult (dataclass)

| Property | Type | Description |
|----------|------|-------------|
| `total_steps` | `int` | Count of step results |
| `passed_steps` | `int` | Count of passing steps |
| `duration_ms` | `float` | Sum of all step durations |
| `pass_rate` | `float` | `passed_steps / total_steps` (0.0 if no steps) |

### StepStatus (Enum)

Values: `PENDING`, `RUNNING`, `PASSED`, `FAILED`, `TIMEOUT`, `SKIPPED`, `ERROR`

### WorkflowStepType (Enum)

Values: `HTTP_REQUEST`, `ASSERTION`, `WAIT`, `SCRIPT`, `CONDITIONAL`

## Dependencies

- Standard library only: `time`, `abc`, `dataclasses`, `datetime`, `enum`

## Constraints

- `HTTP_REQUEST` and `CONDITIONAL` step types are defined but have no default executor; using them without registering a custom executor returns an ERROR result.
- `ScriptExecutor` restricted eval disables all builtins; only `ctx` (the context dict) is accessible. Callable functions bypass eval.
- `WorkflowRunner.run()` stops after any non-passing step by default, including
  `FAILED`, `TIMEOUT`, `ERROR`, `SKIPPED`, and missing-executor results. Set the
  step's `continue_on_error=True` only when continuation is an intentional part of
  the workflow contract.
- `WorkflowStep.dependencies` field is defined but not enforced by `WorkflowRunner` (steps execute in list order).
- `WorkflowStep.timeout_seconds` is passed to custom executors through the step
  definition; the default synchronous executors do not interrupt a running Python
  call. A timeout-aware executor should return `StepStatus.TIMEOUT`.

### Trusted workflow boundary

`ScriptExecutor` supports callable functions and a restricted expression DSL for
local test workflows. Workflow definitions and expressions are trusted inputs only;
do not load them from untrusted users or expose them as a general-purpose shell or
remote code-execution interface.

## Error Handling

- `AssertionExecutor` catches all exceptions and returns `StepStatus.ERROR` with error message
- `ScriptExecutor` catches all exceptions from callable or eval and returns `StepStatus.ERROR`
- `WorkflowRunner._run_step()` returns `StepStatus.ERROR` with message if no executor is registered for the step type
- No custom exception classes; relies on `StepResult.error` string field for error reporting

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
