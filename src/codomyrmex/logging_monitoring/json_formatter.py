"""Structured JSON formatter for logging.

This module provides a JSONFormatter class that outputs log records as
JSON objects, enabling structured logging for easier parsing, querying,
and analysis by log aggregation systems.

Example:
    >>> import logging
    >>> from codomyrmex.logging_monitoring.json_formatter import JSONFormatter
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(JSONFormatter())
    >>> logger = logging.getLogger("myapp")
    >>> logger.addHandler(handler)
    >>> logger.info("Request processed")
    # Output: {"timestamp": "2024-01-15 10:30:00", "level": "INFO", ...}
"""

import json
import logging
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatter that outputs log records as JSON objects.

    Converts standard Python log records into JSON-formatted strings containing
    timestamp, level, logger name, message, module, line number, and any
    exception information or extra fields.

    Attributes:
        Inherits all attributes from logging.Formatter.

    Example:
        >>> formatter = JSONFormatter()
        >>> handler = logging.FileHandler("app.json.log")
        >>> handler.setFormatter(formatter)
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Converts the log record to a dictionary and serializes it to JSON.
        Includes exception information if present and merges any extra
        fields attached to the record.

        Args:
            record: The log record to format.

        Returns:
            A JSON-formatted string containing the log entry with fields:
            - timestamp: Formatted time of the log event
            - level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            - name: Logger name
            - message: The formatted log message
            - module: Source module name
            - line: Source line number
            - exception: (optional) Formatted exception traceback
            - Any additional fields from record.extra

        Example:
            >>> record = logging.LogRecord(...)
            >>> json_str = formatter.format(record)
            >>> data = json.loads(json_str)
            >>> print(data["level"])  # "INFO"
        """
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        return json.dumps(log_entry)

