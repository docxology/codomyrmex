# Workflow Testing Module — Agent Coordination

## Purpose

End-to-end workflow validation and testing.

## Key Capabilities

- **WorkflowStepType**: Types of workflow steps.
- **StepStatus**: Status of a step execution.
- **WorkflowStep**: A single step in a workflow test.
- **StepResult**: Result of executing a step.
- **WorkflowResult**: Result of running a complete workflow.
- `to_dict()`: Convert to dictionary.
- `passed()`: Check if step passed.
- `to_dict()`: Convert to dictionary.

## Agent Usage Patterns

```python
from codomyrmex.workflow_testing import WorkflowStepType

# Agent initializes workflow testing
instance = WorkflowStepType()
```

## Integration Points

- **Source**: [src/codomyrmex/workflow_testing/](../../../src/codomyrmex/workflow_testing/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Key Components

- **`WorkflowStepType`** — Types of workflow steps.
- **`StepStatus`** — Status of a step execution.
- **`WorkflowStep`** — A single step in a workflow test.
- **`StepResult`** — Result of executing a step.
- **`WorkflowResult`** — Result of running a complete workflow.

