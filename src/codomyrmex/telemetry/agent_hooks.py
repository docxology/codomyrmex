"""Agent-specific telemetry hooks for granular performance tracking."""

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Optional

from codomyrmex.telemetry.metrics import get_metrics
from codomyrmex.telemetry.tracing import SpanKind, SpanStatus, get_tracer


class AgentTelemetryHooks:
    """Hooks for tracking agent execution performance and latency."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.tracer = get_tracer(f"agent.{agent_name}")
        # Use default in_memory backend for metrics
        self.metrics = get_metrics()

    def _get_metric_labels(self, phase: str, **extra_labels) -> dict[str, str]:
        labels = {"agent": self.agent_name, "phase": phase}
        labels.update(extra_labels)
        return labels

    @contextmanager
    def track_phase(
        self,
        phase_name: str,
        attributes: Optional[dict[str, Any]] = None,
        **extra_labels,
    ) -> Generator[None, None, None]:
        """Track a generic agent execution phase."""
        span_name = f"agent.{self.agent_name}.{phase_name}"
        labels = self._get_metric_labels(phase_name, **extra_labels)

        start_time = time.perf_counter()
        with self.tracer.span(
            span_name, kind=SpanKind.INTERNAL, **(attributes or {})
        ) as span:
            try:
                yield
                span.set_status(SpanStatus.OK)
            except Exception as e:
                span.record_exception(e)
                self.metrics.counter(
                    "agent_phase_errors_total",
                    labels=labels,
                    description="Total errors during agent phases",
                ).inc()
                raise
            finally:
                duration = time.perf_counter() - start_time
                self.metrics.histogram(
                    "agent_phase_latency_seconds",
                    labels=labels,
                    description="Latency of agent execution phases",
                ).observe(duration)
                self.metrics.counter(
                    "agent_phase_executions_total",
                    labels=labels,
                    description="Total executions of agent phases",
                ).inc()

    @contextmanager
    def track_plan(self, **attributes) -> Generator[None, None, None]:
        """Track agent planning phase."""
        with self.track_phase("plan", attributes=attributes):
            yield

    @contextmanager
    def track_act(self, action_type: str, **attributes) -> Generator[None, None, None]:
        """Track agent acting phase."""
        attrs = {"action_type": action_type}
        attrs.update(attributes)
        with self.track_phase("act", attributes=attrs, action_type=action_type):
            yield

    @contextmanager
    def track_observe(self, **attributes) -> Generator[None, None, None]:
        """Track agent observation phase."""
        with self.track_phase("observe", attributes=attributes):
            yield

    @contextmanager
    def track_task(self, task_id: str, **attributes) -> Generator[None, None, None]:
        """Track a complete agent task."""
        attrs = {"task_id": task_id}
        attrs.update(attributes)
        with self.track_phase("task", attributes=attrs, task_id=task_id):
            yield
