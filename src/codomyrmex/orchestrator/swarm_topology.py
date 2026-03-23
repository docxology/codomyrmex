"""Swarm execution topologies for multi-agent DAG orchestration.

Provides first-class Fan-Out, Fan-In, Pipeline, and Broadcast primitives
that wire into the existing :class:`~codomyrmex.orchestrator.engines.parallel.ParallelEngine`.

Example::

    topo = SwarmTopology()
    tasks = [
        {"id": "a", "fn": my_fn, "args": [1]},
        {"id": "b", "fn": my_fn, "args": [2]},
    ]
    result = topo.run(TopologyMode.FAN_OUT, tasks)
    merged = topo.fan_in(result["results"])
"""

from __future__ import annotations

import concurrent.futures
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class TopologyMode(StrEnum):
    """Execution topology for a swarm run."""

    FAN_OUT = "fan_out"
    FAN_IN = "fan_in"
    PIPELINE = "pipeline"
    BROADCAST = "broadcast"


@dataclass
class TaskSpec:
    """Specification for a single swarm task.

    Attributes:
        task_id: Unique task identifier.
        fn: Callable to execute.
        args: Positional arguments for *fn*.
        kwargs: Keyword arguments for *fn*.
        metadata: Arbitrary metadata attached to the result.
    """

    task_id: str
    fn: Any  # callable
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of a single swarm task.

    Attributes:
        task_id: Originating task ID.
        output: Return value of the callable.
        error: Error string if execution failed, else empty.
        duration_ms: Wall-clock execution time in milliseconds.
        metadata: Metadata forwarded from :class:`TaskSpec`.
    """

    task_id: str
    output: Any
    error: str = ""
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """True if the task completed without error."""
        return not self.error


class SwarmTopology:
    """First-class swarm execution topologies.

    Wraps Python's :mod:`concurrent.futures` so the caller deals only in
    :class:`TaskSpec` / :class:`TaskResult` pairs, not thread management.

    Args:
        max_workers: Thread-pool size for parallel modes.
    """

    def __init__(self, max_workers: int = 8) -> None:
        self._max_workers = max_workers

    # ── primitive operations ─────────────────────────────────────────

    def fan_out(self, tasks: list[TaskSpec]) -> list[TaskResult]:
        """Dispatch all tasks in parallel (Fan-Out).

        All tasks are submitted to the thread pool simultaneously.
        Results are returned in submission order once all complete.

        Args:
            tasks: List of :class:`TaskSpec` to execute concurrently.

        Returns:
            List of :class:`TaskResult` in the same order as *tasks*.
        """
        results: list[TaskResult] = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(self._max_workers, len(tasks) or 1)
        ) as pool:
            futures: dict[concurrent.futures.Future[Any], TaskSpec] = {
                pool.submit(self._run_one, spec): spec for spec in tasks
            }
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        # Re-sort to match submission order
        id_order = {spec.task_id: idx for idx, spec in enumerate(tasks)}
        results.sort(key=lambda r: id_order.get(r.task_id, 999))
        return results

    def fan_in(self, results: list[TaskResult]) -> dict[str, Any]:
        """Collect and merge Fan-Out results (Fan-In).

        Produces a single aggregated dict containing:
        - ``results``: All individual :class:`TaskResult` objects
        - ``success_count`` / ``error_count``
        - ``merged_outputs``: Concatenated non-None outputs (if all are dicts, merged)

        Args:
            results: Output of :meth:`fan_out`.

        Returns:
            Aggregated result dict.
        """
        successes = [r for r in results if r.success]
        errors = [r for r in results if not r.success]

        # If all outputs are dicts, deep-merge them
        merged: dict[str, Any] = {}
        for r in successes:
            if isinstance(r.output, dict):
                merged.update(r.output)

        return {
            "success_count": len(successes),
            "error_count": len(errors),
            "results": [
                {
                    "task_id": r.task_id,
                    "output": r.output,
                    "error": r.error,
                    "duration_ms": r.duration_ms,
                }
                for r in results
            ],
            "merged_outputs": merged,
            "errors": [{"task_id": r.task_id, "error": r.error} for r in errors],
        }

    def pipeline(self, tasks: list[TaskSpec]) -> list[TaskResult]:
        """Execute tasks sequentially, chaining output to next input.

        The ``output`` of task *n* is passed as the first positional argument
        of task *n+1*.  The initial task runs with its own ``args``/``kwargs``.

        Args:
            tasks: Ordered list of :class:`TaskSpec` to chain.

        Returns:
            List of :class:`TaskResult` in execution order.
        """
        results: list[TaskResult] = []
        carry: Any = None
        for idx, spec in enumerate(tasks):
            if idx > 0 and carry is not None:
                spec.args = [carry, *spec.args]
            result = self._run_one(spec)
            results.append(result)
            carry = result.output if result.success else None
        return results

    def broadcast(
        self, message: dict[str, Any], tasks: list[TaskSpec]
    ) -> list[TaskResult]:
        """Send the same message to all agents in parallel (Broadcast).

        Injects *message* as ``kwargs["broadcast_message"]`` for every task.

        Args:
            message: Shared payload injected into each task's kwargs.
            tasks: List of :class:`TaskSpec` to receive the broadcast.

        Returns:
            List of :class:`TaskResult`.
        """
        for spec in tasks:
            spec.kwargs["broadcast_message"] = message
        return self.fan_out(tasks)

    # ── unified dispatcher ───────────────────────────────────────────

    def run(
        self,
        mode: TopologyMode | str,
        tasks: list[TaskSpec],
        *,
        broadcast_message: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Dispatch tasks using the specified topology.

        Args:
            mode: Topology mode (``fan_out``, ``fan_in``, ``pipeline``, ``broadcast``).
            tasks: Tasks to execute.
            broadcast_message: Payload for ``broadcast`` mode.

        Returns:
            Aggregated result dict from :meth:`fan_in`, or sequential list wrapped in a dict.

        Raises:
            ValueError: If *mode* is not a recognised :class:`TopologyMode`.
        """
        mode = TopologyMode(mode)

        if mode == TopologyMode.FAN_OUT:
            raw = self.fan_out(tasks)
            return self.fan_in(raw)

        if mode == TopologyMode.FAN_IN:
            # fan_in without prior fan_out is a no-op aggregation
            raw = self.fan_out(tasks)
            return self.fan_in(raw)

        if mode == TopologyMode.PIPELINE:
            raw = self.pipeline(tasks)
            return {
                "results": [
                    {"task_id": r.task_id, "output": r.output, "error": r.error}
                    for r in raw
                ],
                "success_count": sum(1 for r in raw if r.success),
                "error_count": sum(1 for r in raw if not r.success),
            }

        if mode == TopologyMode.BROADCAST:
            raw = self.broadcast(broadcast_message or {}, tasks)
            return self.fan_in(raw)

        msg = f"Unknown topology mode: {mode}"
        raise ValueError(msg)

    # ── internal helpers ─────────────────────────────────────────────

    @staticmethod
    def _run_one(spec: TaskSpec) -> TaskResult:
        """Execute a single task, catching all exceptions."""
        t0 = time.time()
        try:
            output = spec.fn(*spec.args, **spec.kwargs)
            return TaskResult(
                task_id=spec.task_id,
                output=output,
                duration_ms=(time.time() - t0) * 1000,
                metadata=spec.metadata,
            )
        except Exception as exc:
            logger.warning("Swarm task '%s' failed: %s", spec.task_id, exc)
            return TaskResult(
                task_id=spec.task_id,
                output=None,
                error=str(exc),
                duration_ms=(time.time() - t0) * 1000,
                metadata=spec.metadata,
            )


__all__ = [
    "SwarmTopology",
    "TaskResult",
    "TaskSpec",
    "TopologyMode",
]
