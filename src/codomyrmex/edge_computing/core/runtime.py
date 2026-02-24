"""Edge function runtime execution with metrics and cold-start tracking.

Provides:
- EdgeRuntime: function deploy/undeploy/invoke lifecycle
- Invocation metrics (latency, call count, error rate)
- Cold-start detection
- Function health and warm-up
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .models import EdgeExecutionError, EdgeFunction, EdgeNode


@dataclass
class InvocationMetrics:
    """Metrics for a single function invocation."""

    function_id: str
    duration_seconds: float
    success: bool
    cold_start: bool
    error: str = ""


class EdgeRuntime:
    """Runtime for edge function execution with metrics.

    Tracks invocation latency, cold-start events, and per-function
    call counts for monitoring.

    Example::

        node = EdgeNode(id="edge-1", region="us-west")
        runtime = EdgeRuntime(node)
        fn = EdgeFunction(id="greet", handler=lambda name: f"Hello {name}")
        runtime.deploy(fn)
        result = runtime.invoke("greet", "world")
        assert result == "Hello world"
    """

    def __init__(self, node: EdgeNode) -> None:
        """Execute   Init   operations natively."""
        self.node = node
        self._functions: dict[str, EdgeFunction] = {}
        self._metrics: list[InvocationMetrics] = []
        self._call_counts: dict[str, int] = {}
        self._warm_functions: set[str] = set()  # functions invoked at least once

    def deploy(self, function: EdgeFunction) -> None:
        """Deploy a function to this edge runtime."""
        self._functions[function.id] = function
        self._call_counts[function.id] = 0
        # Not warm until first invocation
        self._warm_functions.discard(function.id)

    def undeploy(self, function_id: str) -> bool:
        """Undeploy a function."""
        if function_id in self._functions:
            del self._functions[function_id]
            self._call_counts.pop(function_id, None)
            self._warm_functions.discard(function_id)
            return True
        return False

    def invoke(self, function_id: str, *args: Any, **kwargs: Any) -> Any:
        """Invoke an edge function with metrics tracking.

        Args:
            function_id: ID of the deployed function.
            *args, **kwargs: Arguments to pass to the function handler.

        Returns:
            The function's return value.

        Raises:
            ValueError: If function not found.
            EdgeExecutionError: If function execution fails or exceeds timeout.
        """
        func = self._functions.get(function_id)
        if not func:
            raise ValueError(f"Function not found: {function_id}")

        cold_start = function_id not in self._warm_functions
        start = time.time()

        try:
            result = func.handler(*args, **kwargs)
            elapsed = time.time() - start

            if elapsed > func.timeout_seconds:
                raise TimeoutError(f"Function exceeded timeout: {elapsed:.3f}s > {func.timeout_seconds}s")

            self._warm_functions.add(function_id)
            self._call_counts[function_id] = self._call_counts.get(function_id, 0) + 1
            self._metrics.append(InvocationMetrics(
                function_id=function_id,
                duration_seconds=elapsed,
                success=True,
                cold_start=cold_start,
            ))
            return result

        except Exception as e:
            elapsed = time.time() - start
            self._metrics.append(InvocationMetrics(
                function_id=function_id,
                duration_seconds=elapsed,
                success=False,
                cold_start=cold_start,
                error=str(e),
            ))
            raise EdgeExecutionError(f"Edge function failed: {e}") from e

    def warm_up(self, function_id: str) -> bool:
        """Pre-warm a function to avoid cold-start latency.

        Invokes the function with no args to initialize it. Catches errors silently.
        """
        func = self._functions.get(function_id)
        if not func:
            return False
        try:
            func.handler()
        except Exception:
            pass
        self._warm_functions.add(function_id)
        return True

    def list_functions(self) -> list[EdgeFunction]:
        """Execute List Functions operations natively."""
        return list(self._functions.values())

    def is_warm(self, function_id: str) -> bool:
        """Execute Is Warm operations natively."""
        return function_id in self._warm_functions

    @property
    def function_count(self) -> int:
        """Execute Function Count operations natively."""
        return len(self._functions)

    @property
    def total_invocations(self) -> int:
        """Execute Total Invocations operations natively."""
        return sum(self._call_counts.values())

    @property
    def cold_start_count(self) -> int:
        """Execute Cold Start Count operations natively."""
        return sum(1 for m in self._metrics if m.cold_start)

    def get_function_stats(self, function_id: str) -> dict[str, Any]:
        """Get per-function invocation statistics."""
        fn_metrics = [m for m in self._metrics if m.function_id == function_id]
        if not fn_metrics:
            return {"calls": 0}
        successes = [m for m in fn_metrics if m.success]
        return {
            "calls": len(fn_metrics),
            "successes": len(successes),
            "errors": len(fn_metrics) - len(successes),
            "avg_latency_ms": (sum(m.duration_seconds for m in successes) / max(len(successes), 1)) * 1000,
            "cold_starts": sum(1 for m in fn_metrics if m.cold_start),
        }

    def summary(self) -> dict[str, Any]:
        """Return runtime-level summary."""
        return {
            "node_id": self.node.id,
            "functions_deployed": self.function_count,
            "total_invocations": self.total_invocations,
            "cold_starts": self.cold_start_count,
            "warm_functions": len(self._warm_functions),
        }
