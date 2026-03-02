"""Structured log formatter with context injection.

Provides JSON-lines log formatting with automatic correlation ID,
module context, and configurable field inclusion for production
log pipelines (ELK, Loki, Datadog, etc.).
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Standard log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogContext:
    """Contextual metadata attached to every log line.

    Attributes:
        correlation_id: Request or workflow correlation ID.
        module: Source module name.
        function: Source function name.
        extra: Additional key-value context.
    """

    correlation_id: str = ""
    module: str = ""
    function: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class FormatterConfig:
    """Configuration for the structured formatter.

    Attributes:
        include_timestamp: Include ISO 8601 timestamp.
        include_level: Include log level field.
        include_module: Include module/function fields.
        include_correlation_id: Include correlation ID.
        include_stacktrace: Include stacktrace on errors.
        timestamp_key: JSON key for the timestamp field.
        level_key: JSON key for the level field.
        message_key: JSON key for the message field.
        pretty_print: Indent JSON output for readability.
        max_message_length: Truncate messages beyond this length (0=no limit).
        static_fields: Fields to include in every log line.
    """

    include_timestamp: bool = True
    include_level: bool = True
    include_module: bool = True
    include_correlation_id: bool = True
    include_stacktrace: bool = True
    timestamp_key: str = "timestamp"
    level_key: str = "level"
    message_key: str = "message"
    pretty_print: bool = False
    max_message_length: int = 0
    static_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class StructuredLogEntry:
    """A single structured log entry.

    Attributes:
        level: Log level.
        message: Log message.
        context: Contextual metadata.
        timestamp: Unix timestamp of the log event.
        error: Optional exception info.
        fields: Additional structured fields.
    """

    level: LogLevel
    message: str
    context: LogContext = field(default_factory=LogContext)
    timestamp: float = field(default_factory=time.time)
    error: BaseException | None = None
    fields: dict[str, Any] = field(default_factory=dict)


class StructuredFormatter:
    """Formats log entries as JSON-lines for structured logging.

    Produces one JSON object per log line with configurable fields,
    automatic timestamp and correlation ID injection, and optional
    stacktrace capture on error-level logs.

    Example::

        formatter = StructuredFormatter(config=FormatterConfig(
            static_fields={"service": "codomyrmex", "env": "dev"},
        ))
        ctx = LogContext(correlation_id="req-123", module="agents")
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            message="Agent started",
            context=ctx,
        )
        json_line = formatter.format(entry)
    """

    def __init__(self, config: FormatterConfig | None = None) -> None:
        """Initialize this instance."""
        self._config = config or FormatterConfig()
        self._line_count = 0

    @property
    def config(self) -> FormatterConfig:
        """Current formatter configuration."""
        return self._config

    @property
    def lines_formatted(self) -> int:
        """Number of log lines formatted."""
        return self._line_count

    def format(self, entry: StructuredLogEntry) -> str:
        """Format a log entry as a JSON string.

        Args:
            entry: The structured log entry.

        Returns:
            A single-line JSON string (unless pretty_print).
        """
        cfg = self._config
        record: dict[str, Any] = {}

        # Static fields first (can be overridden by entry)
        record.update(cfg.static_fields)

        # Timestamp
        if cfg.include_timestamp:
            record[cfg.timestamp_key] = self._format_timestamp(entry.timestamp)

        # Level
        if cfg.include_level:
            record[cfg.level_key] = entry.level.value

        # Message
        message = entry.message
        if cfg.max_message_length > 0 and len(message) > cfg.max_message_length:
            message = message[: cfg.max_message_length] + "..."
        record[cfg.message_key] = message

        # Context
        if cfg.include_correlation_id and entry.context.correlation_id:
            record["correlation_id"] = entry.context.correlation_id

        if cfg.include_module:
            if entry.context.module:
                record["module"] = entry.context.module
            if entry.context.function:
                record["function"] = entry.context.function

        # Extra context
        if entry.context.extra:
            record["context"] = entry.context.extra

        # Entry-level fields
        if entry.fields:
            record.update(entry.fields)

        # Stacktrace on errors
        if (
            cfg.include_stacktrace
            and entry.error is not None
            and entry.level in (LogLevel.ERROR, LogLevel.CRITICAL)
        ):
            record["error_type"] = type(entry.error).__name__
            record["error_message"] = str(entry.error)
            record["stacktrace"] = traceback.format_exception(
                type(entry.error), entry.error, entry.error.__traceback__
            )

        self._line_count += 1

        indent = 2 if cfg.pretty_print else None
        return json.dumps(record, default=str, indent=indent)

    def format_batch(self, entries: list[StructuredLogEntry]) -> str:
        """Format multiple entries as newline-delimited JSON.

        Args:
            entries: List of log entries.

        Returns:
            Newline-separated JSON strings.
        """
        return "\n".join(self.format(e) for e in entries)

    def _format_timestamp(self, ts: float) -> str:
        """Format a unix timestamp as ISO 8601 UTC."""
        import datetime

        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return dt.isoformat()

    def reset_count(self) -> None:
        """Reset the formatted line counter."""
        self._line_count = 0
