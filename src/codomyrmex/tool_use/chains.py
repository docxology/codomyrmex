"""
Tool chain composition for sequential tool execution.

Provides a pipeline abstraction where multiple tools execute in
sequence, with each step's output feeding into the next step's input
via configurable mappings.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.schemas import Result, ResultStatus

from .registry import ToolRegistry
from .validation import ValidationResult


@dataclass
class ChainStep:
    """
    A single step in a tool chain.

    Attributes:
        tool_name: Name of the tool to invoke (must exist in the registry).
        input_mapping: Dict mapping tool input keys to keys in the
            accumulated chain context. If empty, the entire context
            is passed as input.

            Example: {"text": "previous_output.content"} means the
            tool receives {"text": <value of context["previous_output.content"]>}.

            Dot-notation is supported for one level of nesting.
        output_key: Key under which this step's output is stored in the
            chain context for downstream steps. If empty, the output
            dict is merged directly into the context.
    """

    tool_name: str
    input_mapping: dict[str, str] = field(default_factory=dict)
    output_key: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "input_mapping": self.input_mapping,
            "output_key": self.output_key,
        }


@dataclass
class ChainResult:
    """
    Result of executing an entire tool chain.

    Attributes:
        success: Whether all steps completed successfully.
        context: The accumulated context after all steps ran.
        step_results: Per-step Result objects, in execution order.
        errors: Aggregated errors from all steps.
        duration_ms: Total wall-clock time for the chain.
    """

    success: bool = True
    context: dict[str, Any] = field(default_factory=dict)
    step_results: list[Result] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "context": self.context,
            "step_results": [r.to_dict() for r in self.step_results],
            "errors": self.errors,
            "duration_ms": self.duration_ms,
        }


def _resolve_key(context: dict[str, Any], key: str) -> Any:
    """
    Resolve a key from the context, supporting one level of dot-notation.

    Examples:
        _resolve_key({"a": 1}, "a")           -> 1
        _resolve_key({"a": {"b": 2}}, "a.b")  -> 2
        _resolve_key({"a": 1}, "missing")      -> None
    """
    parts = key.split(".", 1)
    value = context.get(parts[0])
    if len(parts) == 1 or value is None:
        return value
    if isinstance(value, dict):
        return value.get(parts[1])
    return None


class ToolChain:
    """
    A pipeline of tools that execute sequentially.

    Each step invokes a tool from the registry. Outputs from earlier
    steps are available to later steps via the accumulated context dict.

    Example::

        registry = ToolRegistry()
        # ... register tools "fetch" and "parse" ...

        chain = ToolChain(registry=registry)
        chain.add_step(ChainStep(
            tool_name="fetch",
            output_key="raw",
        ))
        chain.add_step(ChainStep(
            tool_name="parse",
            input_mapping={"content": "raw.body"},
            output_key="parsed",
        ))

        result = chain.execute({"url": "https://example.com"})
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry
        self._steps: list[ChainStep] = []

    # ------------------------------------------------------------------
    # Building the chain
    # ------------------------------------------------------------------

    def add_step(self, step: ChainStep) -> "ToolChain":
        """
        Append a step to the chain.

        Returns self for fluent chaining.
        """
        self._steps.append(step)
        return self

    @property
    def steps(self) -> list[ChainStep]:
        """Return a copy of the current step list."""
        return list(self._steps)

    def clear(self) -> None:
        """Remove all steps from the chain."""
        self._steps.clear()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> ValidationResult:
        """
        Validate that all tools referenced by steps exist in the registry.

        Returns:
            ValidationResult with errors for any missing tools.
        """
        errors: list[str] = []

        if not self._steps:
            errors.append("Chain has no steps.")

        seen_names: set[str] = set()
        for i, step in enumerate(self._steps):
            if not step.tool_name:
                errors.append(f"Step {i}: tool_name is empty.")
                continue
            if step.tool_name not in self._registry:
                errors.append(
                    f"Step {i}: tool '{step.tool_name}' not found in registry."
                )
            if step.tool_name in seen_names:
                # Not an error, just a note -- tools can repeat
                pass
            seen_names.add(step.tool_name)

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        initial_input: dict[str, Any] | None = None,
        *,
        stop_on_failure: bool = True,
        validate_tools: bool = True,
    ) -> ChainResult:
        """
        Execute all steps sequentially.

        Args:
            initial_input: Starting context dict available to the first step.
            stop_on_failure: If True (default), stop the chain on the first
                tool failure. If False, continue executing remaining steps.
            validate_tools: If True (default), validate that all referenced
                tools exist before executing. Skips execution if validation fails.

        Returns:
            ChainResult with accumulated context, per-step results, and
            overall success status.
        """
        chain_start = time.monotonic()
        context: dict[str, Any] = dict(initial_input) if initial_input else {}
        step_results: list[Result] = []
        all_errors: list[str] = []
        success = True

        # Pre-flight validation
        if validate_tools:
            vr = self.validate()
            if not vr.valid:
                elapsed = (time.monotonic() - chain_start) * 1000
                return ChainResult(
                    success=False,
                    context=context,
                    step_results=[],
                    errors=vr.errors,
                    duration_ms=elapsed,
                )

        for i, step in enumerate(self._steps):
            # Build input for this step
            if step.input_mapping:
                step_input = {}
                for target_key, source_key in step.input_mapping.items():
                    step_input[target_key] = _resolve_key(context, source_key)
            else:
                step_input = dict(context)

            # Invoke the tool
            result = self._registry.invoke(step.tool_name, step_input)
            step_results.append(result)

            if not result.ok:
                success = False
                all_errors.extend(result.errors)
                all_errors.append(
                    f"Step {i} ('{step.tool_name}') failed: {result.message}"
                )
                if stop_on_failure:
                    break
                continue

            # Store output in context
            output = result.data
            if step.output_key:
                context[step.output_key] = output
            elif isinstance(output, dict):
                context.update(output)

        elapsed = (time.monotonic() - chain_start) * 1000
        return ChainResult(
            success=success,
            context=context,
            step_results=step_results,
            errors=all_errors,
            duration_ms=elapsed,
        )

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        names = [s.tool_name for s in self._steps]
        return f"ToolChain(steps={names})"


__all__ = [
    "ChainStep",
    "ChainResult",
    "ToolChain",
]
