"""Structured log context manager with automatic correlation IDs.

Enriches log records with correlation IDs, module tags, and structured
metadata for tracing requests across module boundaries.

Example::

    with LogContext(module="hermes", operation="chat") as ctx:
        logger.info("Processing request", extra=ctx.extra())
        # All logs within this block share the same correlation_id
"""

from __future__ import annotations

import contextvars
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Self

logger = logging.getLogger(__name__)

_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)
_log_tags: contextvars.ContextVar[dict[str, str] | None] = contextvars.ContextVar(
    "log_tags", default=None
)


@dataclass
class LogContext:
    """Structured log context with automatic correlation IDs.

    Args:
        module: Module name for tagging.
        operation: Operation name for tagging.
        correlation_id: Optional explicit correlation ID (auto-generated if empty).
        tags: Additional key-value tags.

    Example::

        ctx = LogContext(module="agents", operation="start")
        with ctx:
            logger.info("Agent starting", extra=ctx.extra())
    """

    module: str = ""
    operation: str = ""
    correlation_id: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    _start_time: float = field(default=0.0, repr=False)

    def __enter__(self) -> Self:
        if not self.correlation_id:
            self.correlation_id = uuid.uuid4().hex[:12]
        self._start_time = time.monotonic()
        _correlation_id.set(self.correlation_id)
        _log_tags.set({
            "module": self.module,
            "operation": self.operation,
            **self.tags,
        })
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed = (time.monotonic() - self._start_time) * 1000
        logger.debug(
            "Context closed: %s.%s (%.1fms, cid=%s)",
            self.module,
            self.operation,
            elapsed,
            self.correlation_id,
        )

    def extra(self) -> dict[str, Any]:
        """Generate extra dict for ``logger.*()`` calls.

        Returns:
            Dict with ``correlation_id``, ``module``, ``operation``, and tags.
        """
        return {
            "correlation_id": self.correlation_id,
            "module": self.module,
            "operation": self.operation,
            **self.tags,
        }

    @property
    def elapsed_ms(self) -> float:
        """Milliseconds since context was entered."""
        if self._start_time <= 0:
            return 0.0
        return (time.monotonic() - self._start_time) * 1000


def get_correlation_id() -> str:
    """Get the current correlation ID from context.

    Returns:
        Current correlation ID, or empty string if none set.
    """
    return _correlation_id.get()


def get_log_tags() -> dict[str, str]:
    """Get the current log tags from context.

    Returns:
        Current tags dict.
    """
    return _log_tags.get() or {}


class CorrelationFilter(logging.Filter):
    """Logging filter that injects correlation_id into all records.

    Attach to a handler to automatically enrich all log records
    with the current correlation ID.

    Example::

        handler = logging.StreamHandler()
        handler.addFilter(CorrelationFilter())
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = _correlation_id.get()  # type: ignore[attr-defined]
        tags = _log_tags.get() or {}
        record.log_module = tags.get("module", "")  # type: ignore[attr-defined]
        record.log_operation = tags.get("operation", "")  # type: ignore[attr-defined]
        return True


__all__ = [
    "CorrelationFilter",
    "LogContext",
    "get_correlation_id",
    "get_log_tags",
]
