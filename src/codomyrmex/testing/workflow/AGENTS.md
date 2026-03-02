# Workflow Testing -- Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a structured workflow test framework with step-based execution, assertion validation, and context passing between steps. Agents use this module to define multi-step test workflows with typed executors and retry logic.

## Key Components

| Component | Source | Role |
|-----------|--------|------|
| `Workflow` | `models.py` | Test definition with `add_step()`, `add_assertion()`, `add_wait()` helpers and shared `variables` |
| `WorkflowStep` | `models.py` | Single step with `step_type`, `config`, `dependencies`, `retry_count`, `timeout_seconds` |
| `WorkflowRunner` | `runner.py` | Executor orchestrator with step-type-to-executor registry, context passing, and retry logic |
| `StepExecutor` (ABC) | `executors.py` | Base executor: `execute(step, context) -> StepResult` |
| `AssertionExecutor` | `executors.py` | Assertion checks: equals, contains, not_null, greater_than, less_than |
| `WaitExecutor` | `executors.py` | Time delay step (`time.sleep`) |
| `ScriptExecutor` | `executors.py` | Callable or restricted `eval` expression execution with `{"__builtins__": {}}` sandbox |

## Operating Contracts

1. **Step Types**: `WorkflowStepType` enum: `HTTP_REQUEST`, `ASSERTION`, `WAIT`, `SCRIPT`, `CONDITIONAL`. Only ASSERTION, WAIT, and SCRIPT have registered executors by default.
2. **Context Passing**: `WorkflowRunner.run()` maintains a shared `context` dict. Step output is stored as `step_{id}` in context for downstream steps.
3. **Retry Logic**: `WorkflowRunner._run_step()` retries up to `step.retry_count` times. Only the last `StepResult` is returned.
4. **Error Propagation**: Steps returning `StepStatus.ERROR` cause the workflow to stop (break). `FAILED` steps continue execution of remaining steps.
5. **Custom Executors**: `WorkflowRunner.register_executor(step_type, executor)` allows extending with new step types.
6. **Workflow Result**: `WorkflowResult` provides `pass_rate`, `total_steps`, `passed_steps`, `duration_ms` properties. Status is PASSED only if all steps pass.

## Integration Points

- **testing parent**: Part of the `testing` module alongside `chaos`, `fixtures`, and `generators`
- **CLI**: `cli_commands()` in `__init__.py` exposes workflow testing commands
- **Serialization**: `WorkflowStep`, `StepResult`, and `WorkflowResult` all provide `to_dict()` methods

## Navigation

- **Parent**: [testing/](../README.md)
- **Siblings**: [chaos/](../chaos/), [fixtures/](../fixtures/), [generators/](../generators/)
- **Spec**: [SPEC.md](SPEC.md)
