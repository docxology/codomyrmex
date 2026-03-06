"""Structured JSON formatter with pretty printing, filtering, and redaction.

Provides:
- JSONFormatter: structured log output as JSON with extensible fields
- PrettyJSONFormatter: indented JSON for development/debug
- RedactedJSONFormatter: automatic redaction of sensitive fields
"""

from __future__ import annotations

import datetime
import json
import logging
import re
from typing import Any

# Standard LogRecord attributes to exclude from JSON 'extra' fields
_RESERVED_ATTRS: set[str] = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}

# Sensitive field patterns for automatic redaction
_SENSITIVE_PATTERNS = re.compile(
    r"(password|secret|token|api_key|auth|credential|ssn|credit_card)",
    re.IGNORECASE,
)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON strings.

    Converts standard Python log records into structured JSON containing
    timestamp, level, logger name, message, module, line number, and any
    exception or extra fields.

    Example::

        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger = logging.getLogger("myapp")
        logger.addHandler(handler)
        logger.info("Request processed")
    """

    def __init__(
        self,
        datefmt: str | None = None,
        include_fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
    ) -> None:
        super().__init__(datefmt=datefmt)
        self._include = set(include_fields) if include_fields else None
        self._exclude = set(exclude_fields) if exclude_fields else set()

    def _build_entry(self, record: logging.LogRecord) -> dict[str, Any]:
        """Build the base log entry dict."""
        # Use ISO format for timestamp if no datefmt is provided
        if self.datefmt:
            timestamp = self.formatTime(record, self.datefmt)
        else:
            timestamp = datetime.datetime.fromtimestamp(
                record.created, tz=datetime.UTC
            ).isoformat()

        log_entry: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Inject correlation_id if present (common in this codebase)
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id

        # Inject context if present
        if hasattr(record, "context"):
            log_entry["context"] = record.context

        # Add any extra fields attached to the record
        for key, value in record.__dict__.items():
            if key not in _RESERVED_ATTRS and key not in log_entry:
                log_entry[key] = value

        # Apply include/exclude filters
        if self._include:
            log_entry = {k: v for k, v in log_entry.items() if k in self._include}
        for key in self._exclude:
            log_entry.pop(key, None)

        return log_entry

    def format(self, record: logging.LogRecord) -> str:
        """Format the record as a compact JSON string."""
        return json.dumps(self._build_entry(record), default=str)


class PrettyJSONFormatter(JSONFormatter):
    """Human-readable JSON formatter with indentation.

    Useful for development and debugging where readability is preferred
    over compactness.
    """

    def __init__(self, indent: int = 2, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._indent = indent

    def format(self, record: logging.LogRecord) -> str:
        """Format the value for output."""
        return json.dumps(
            self._build_entry(record),
            indent=self._indent,
            default=str,
        )


class RedactedJSONFormatter(JSONFormatter):
    """JSON formatter that automatically redacts sensitive fields.

    Fields whose names match common sensitive patterns (password, token,
    api_key, etc.) are replaced with '[REDACTED]'.

    Args:
        patterns: Additional regex patterns to redact.
        replacement: Replacement string for redacted values.
    """

    def __init__(
        self,
        patterns: list[str] | None = None,
        replacement: str = "[REDACTED]",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._replacement = replacement
        if patterns:
            combined = "|".join(patterns)
            self._pattern = re.compile(
                f"({_SENSITIVE_PATTERNS.pattern}|{combined})",
                re.IGNORECASE,
            )
        else:
            self._pattern = _SENSITIVE_PATTERNS

    def _redact(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively redact sensitive fields."""
        result: dict[str, Any] = {}
        for key, value in data.items():
            if self._pattern.search(key):
                result[key] = self._replacement
            elif isinstance(value, dict):
                result[key] = self._redact(value)
            else:
                result[key] = value
        return result

    def format(self, record: logging.LogRecord) -> str:
        """Format the value for output."""
        entry = self._build_entry(record)
        return json.dumps(self._redact(entry), default=str)
