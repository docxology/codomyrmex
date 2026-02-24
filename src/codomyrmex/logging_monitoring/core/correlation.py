"""Correlation ID propagation for end-to-end tracing.

Provides a context-based correlation ID system that threads a single
identifier through MCP tool invocations → EventBus events → log records
→ audit trail entries.

Usage::

    from codomyrmex.logging_monitoring.core.correlation import (
        new_correlation_id,
        get_correlation_id,
        with_correlation,
        CorrelationFilter,
    )

    # Auto-generate and set a correlation ID for a block.
    with with_correlation() as cid:
        logger.info("Processing request")  # cid injected into log record
        event_bus.emit("tool.called", correlation_id=cid)
"""

from __future__ import annotations

import contextvars
import logging
import uuid
from contextlib import contextmanager
from typing import Any, Generator

logger = logging.getLogger(__name__)

# ── Context Variable ─────────────────────────────────────────────────

_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)


def new_correlation_id() -> str:
    """Generate and store a new correlation ID in the current context.

    Returns:
        The new UUID-based correlation ID.
    """
    cid = f"cid-{uuid.uuid4().hex[:12]}"
    _correlation_id.set(cid)
    return cid


def get_correlation_id() -> str:
    """Retrieve the current correlation ID.

    Returns:
        The current correlation ID, or empty string if none set.
    """
    return _correlation_id.get()


def set_correlation_id(cid: str) -> None:
    """Explicitly set the correlation ID.

    Args:
        cid: The correlation ID to set.
    """
    _correlation_id.set(cid)


def clear_correlation_id() -> None:
    """Clear the current correlation ID."""
    _correlation_id.set("")


@contextmanager
def with_correlation(cid: str | None = None) -> Generator[str, None, None]:
    """Context manager that sets and clears a correlation ID.

    Args:
        cid: Explicit correlation ID.  If ``None``, a new one is generated.

    Yields:
        The active correlation ID.
    """
    token = _correlation_id.set(cid or f"cid-{uuid.uuid4().hex[:12]}")
    try:
        yield _correlation_id.get()
    finally:
        _correlation_id.reset(token)


# ── Logging Integration ──────────────────────────────────────────────

class CorrelationFilter(logging.Filter):
    """Logging filter that injects ``correlation_id`` into log records.

    Add this filter to a handler or logger to automatically include
    the current correlation ID in every log record::

        handler.addFilter(CorrelationFilter())

    Then reference ``%(correlation_id)s`` in your format string, or
    access ``record.correlation_id`` in structured output.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Execute Filter operations natively."""
        record.correlation_id = get_correlation_id()  # noqa: E501
        return True


# ── Event Integration ────────────────────────────────────────────────

def enrich_event_data(data: dict[str, Any]) -> dict[str, Any]:
    """Add the current correlation ID to an event data dict.

    Args:
        data: Event data dictionary.

    Returns:
        The same dict with ``correlation_id`` added (if set).
    """
    cid = get_correlation_id()
    if cid:
        data["correlation_id"] = cid
    return data


# ── MCP Integration ──────────────────────────────────────────────────

def create_mcp_correlation_header() -> dict[str, str]:
    """Generate MCP metadata headers with the current correlation ID.

    Returns:
        Dict suitable for MCP message metadata.
    """
    cid = get_correlation_id()
    if cid:
        return {"x-correlation-id": cid}
    return {}
