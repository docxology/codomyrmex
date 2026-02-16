"""
Workflow Testing Module

Test workflows with step-based assertions, waits, and scripts.
"""

from .models import (
    StepResult,
    StepStatus,
    Workflow,
    WorkflowResult,
    WorkflowStep,
    WorkflowStepType,
)
from .executors import (
    AssertionExecutor,
    ScriptExecutor,
    StepExecutor,
    WaitExecutor,
)
from .runner import WorkflowRunner

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the workflow_testing module."""
    return {
        "suites": lambda: print(
            "Workflow Test Suites\n"
            "  Step types: " + ", ".join(st.value for st in WorkflowStepType) + "\n"
            "  Step statuses: " + ", ".join(ss.value for ss in StepStatus) + "\n"
            "  Use WorkflowRunner to discover and list test suites."
        ),
        "run": lambda: print(
            "Run Workflow Tests\n"
            "  Use WorkflowRunner to execute workflow test suites.\n"
            "  Executors: AssertionExecutor, WaitExecutor, ScriptExecutor\n"
            "  Results include per-step StepResult and overall WorkflowResult."
        ),
    }


__all__ = [
    "WorkflowStepType",
    "StepStatus",
    "WorkflowStep",
    "StepResult",
    "WorkflowResult",
    "Workflow",
    "StepExecutor",
    "AssertionExecutor",
    "WaitExecutor",
    "ScriptExecutor",
    "WorkflowRunner",
    # CLI
    "cli_commands",
]
