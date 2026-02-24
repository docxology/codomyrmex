"""MCP tool definitions for the logging_monitoring module.

Exposes structured log formatting and log aggregation as MCP tools.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        """Execute Mcp Tool operations natively."""
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


@mcp_tool(
    category="logging",
    description="Format a log entry as structured JSON for pipeline ingestion.",
)
def logging_format_structured(
    level: str,
    message: str,
    module: str = "",
    correlation_id: str = "",
    fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Format a single log entry as JSON.

    Args:
        level: Log level (debug, info, warning, error, critical).
        message: Log message text.
        module: Source module name.
        correlation_id: Request/workflow correlation ID.
        fields: Additional structured fields.
    """
    try:
        import json
        from codomyrmex.logging_monitoring.formatters.structured_formatter import (
            StructuredFormatter, StructuredLogEntry, LogLevel, LogContext,
        )
        entry = StructuredLogEntry(
            level=LogLevel(level.lower()),
            message=message,
            context=LogContext(module=module, correlation_id=correlation_id),
            fields=fields or {},
        )
        formatter = StructuredFormatter()
        line = formatter.format(entry)
        return {"status": "ok", "formatted": json.loads(line)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
