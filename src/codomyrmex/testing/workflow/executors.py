"""
Workflow Testing Executors

Step executors for workflow assertions, waits, and scripts.
"""

import ast
import time
from abc import ABC, abstractmethod
from typing import Any

from .models import StepResult, StepStatus, WorkflowStep


class StepExecutor(ABC):
    """Base class for step executors."""

    @abstractmethod
    def execute(self, step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        """Execute a step."""


class AssertionExecutor(StepExecutor):
    """Executor for assertion steps."""

    def execute(self, step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        """Execute assertion step."""
        start = time.time()

        try:
            assertion_type = step.config.get("type", "equals")
            expected = step.config.get("expected")
            actual_key = step.config.get("actual_key")
            actual = (
                context.get(actual_key) if actual_key else step.config.get("actual")
            )

            passed = False
            if assertion_type == "equals":
                passed = actual == expected
            elif assertion_type == "contains":
                passed = expected in str(actual)  # type: ignore
            elif assertion_type == "not_null":
                passed = actual is not None
            elif assertion_type == "greater_than":
                passed = float(actual) > float(expected)
            elif assertion_type == "less_than":
                passed = float(actual) < float(expected)

            duration = (time.time() - start) * 1000

            return StepResult(
                step_id=step.id,
                status=StepStatus.PASSED if passed else StepStatus.FAILED,
                output={"actual": actual, "expected": expected},
                duration_ms=duration,
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            return StepResult(
                step_id=step.id,
                status=StepStatus.ERROR,
                error=str(e),
                duration_ms=duration,
            )


class WaitExecutor(StepExecutor):
    """Executor for wait steps."""

    def execute(self, step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        """Execute wait step."""
        start = time.time()

        seconds = step.config.get("seconds", 1.0)
        time.sleep(seconds)

        duration = (time.time() - start) * 1000

        return StepResult(
            step_id=step.id,
            status=StepStatus.PASSED,
            output={"waited": seconds},
            duration_ms=duration,
        )


class ScriptExecutor(StepExecutor):
    """Executor for script steps."""

    def execute(self, step: WorkflowStep, context: dict[str, Any]) -> StepResult:
        """Execute script step."""
        start = time.time()

        try:
            script_fn = step.config.get("function")
            if callable(script_fn):
                result = script_fn(context)
            else:
                expr_str = step.config.get("expression", "True")

                # SECURITY: Restricted eval — only 'ctx' is accessible, builtins disabled.
                # Adding defense-in-depth AST validation to prevent access to dunders and private attributes.
                tree = ast.parse(expr_str, mode='eval')
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute) and node.attr.startswith('_'):
                        raise ValueError(f"Access to private attribute '{node.attr}' is not allowed.")
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec'):
                        raise ValueError(f"Call to '{node.func.id}' is not allowed.")

                result = eval(
                    expr_str,
                    {"__builtins__": {}},
                    {"ctx": context},
                )

            duration = (time.time() - start) * 1000

            return StepResult(
                step_id=step.id,
                status=StepStatus.PASSED,
                output=result,
                duration_ms=duration,
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            return StepResult(
                step_id=step.id,
                status=StepStatus.ERROR,
                error=str(e),
                duration_ms=duration,
            )
