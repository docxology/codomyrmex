# Workflow Testing — Functional Specification

**Module**: `codomyrmex.workflow_testing`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

End-to-end workflow validation and testing.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `WorkflowStepType` | Class | Types of workflow steps. |
| `StepStatus` | Class | Status of a step execution. |
| `WorkflowStep` | Class | A single step in a workflow test. |
| `StepResult` | Class | Result of executing a step. |
| `WorkflowResult` | Class | Result of running a complete workflow. |
| `StepExecutor` | Class | Base class for step executors. |
| `AssertionExecutor` | Class | Executor for assertion steps. |
| `WaitExecutor` | Class | Executor for wait steps. |
| `ScriptExecutor` | Class | Executor for script steps. |
| `Workflow` | Class | A workflow test definition. |
| `to_dict()` | Function | Convert to dictionary. |
| `passed()` | Function | Check if step passed. |
| `to_dict()` | Function | Convert to dictionary. |
| `total_steps()` | Function | Get total steps. |
| `passed_steps()` | Function | Get passed steps. |

## 3. Dependencies

See `src/codomyrmex/workflow_testing/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.workflow_testing import WorkflowStepType, StepStatus, WorkflowStep, StepResult, WorkflowResult
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k workflow_testing -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/workflow_testing/)
