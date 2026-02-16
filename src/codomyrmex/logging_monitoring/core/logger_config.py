"""
Logger Configuration Module.

Provides centralized logging configuration for the Codomyrmex project with support
for multiple output formats (text, JSON), log levels, and destinations (console, file).

Environment Variables:
    CODOMYRMEX_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO
    CODOMYRMEX_LOG_FILE: Optional file path for log output.
    CODOMYRMEX_LOG_FORMAT: Log format string or "DETAILED" for verbose format.
    CODOMYRMEX_LOG_OUTPUT_TYPE: Output format ("TEXT" or "JSON"). Default: TEXT

Example:
    >>> from codomyrmex.logging_monitoring import setup_logging, get_logger
    >>> setup_logging()
    >>> logger = get_logger(__name__)
    >>> logger.info("Application started")
"""

import json
import logging
import os
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any
from collections.abc import Iterator

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# More detailed log format for debug purposes, can be set via env variable
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"

_logging_configured = False


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging output.

    Formats log records as JSON objects containing timestamp, level, logger name,
    message, module info, and any additional context or correlation IDs.

    Attributes:
        None specific; inherits from logging.Formatter.

    Example:
        >>> formatter = JSONFormatter()
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> # Logs will output as: {"timestamp": "...", "level": "INFO", ...}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            A JSON-formatted string containing the log data with fields:
            timestamp, level, name, message, module, function, line,
            and optionally exception, context, and correlation_id.
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name, # Use "name" instead of "logger" for test compliance
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "context"):
            log_data["context"] = record.context
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "context", "correlation_id"
            ]:
                log_data[key] = value

        return json.dumps(log_data)

def setup_logging(force: bool = True) -> None:
    """Configure the logging system for the application.

    Sets up logging handlers, formatters, and log levels based on environment
    variables. Should be called once at application startup.

    Args:
        force: If True, reconfigure logging even if already configured.
            Defaults to True for test robustness.

    Returns:
        None

    Environment Variables:
        CODOMYRMEX_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        CODOMYRMEX_LOG_FILE: Optional file path for log output.
        CODOMYRMEX_LOG_FORMAT: Format string or "DETAILED" for verbose format.
        CODOMYRMEX_LOG_OUTPUT_TYPE: "TEXT" or "JSON" output format.

    Example:
        >>> setup_logging()  # Configure with defaults
        >>> setup_logging(force=True)  # Force reconfiguration
    """
    global _logging_configured
    if _logging_configured and not force:
        return

    log_level_str = os.getenv("CODOMYRMEX_LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("CODOMYRMEX_LOG_FILE")
    log_format_str_text = os.getenv("CODOMYRMEX_LOG_FORMAT", DEFAULT_LOG_FORMAT)
    log_output_type = os.getenv("CODOMYRMEX_LOG_OUTPUT_TYPE", "TEXT").upper()

    if log_format_str_text == "DETAILED":
        log_format_str_text = DETAILED_LOG_FORMAT
    elif not log_format_str_text:
        log_format_str_text = DEFAULT_LOG_FORMAT

    log_level = getattr(logging, log_level_str, logging.INFO)
    if not isinstance(log_level, int):
        log_level = logging.INFO

    if log_output_type == "JSON":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(log_format_str_text)

    handlers = []
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    if log_file:
        try:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode="a")
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except OSError:
            pass

    logging.basicConfig(level=log_level, handlers=handlers, force=True)
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Creates or retrieves a logger from the logging hierarchy. The logger
    inherits configuration from the root logger set up by setup_logging().

    Args:
        name: The name of the logger, typically __name__ of the calling module.

    Returns:
        A configured Logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    return logging.getLogger(name)


def log_with_context(level: str, message: str, context: dict[str, Any]) -> None:
    """Log a message with additional context data.

    Logs a message at the specified level with context dictionary attached.
    Automatically includes correlation_id if one is set in the current context.

    Args:
        level: The log level as a string (e.g., "info", "error", "debug").
        message: The log message to record.
        context: A dictionary of additional context data to include in the log.

    Returns:
        None

    Example:
        >>> log_with_context("info", "User logged in", {"user_id": "123", "ip": "192.168.1.1"})
        >>> log_with_context("error", "Payment failed", {"order_id": "456", "amount": 99.99})
    """
    logger = get_logger(__name__)
    log_method = getattr(logger, level.lower(), logger.info)
    extra = {"context": context}
    if hasattr(_correlation_context, "correlation_id"):
        extra["correlation_id"] = _correlation_context.correlation_id
    log_method(message, extra=extra)


def create_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing.

    Creates a UUID4-based correlation ID that can be used to trace
    related log entries across different services or components.

    Returns:
        A unique string identifier (UUID4 format).

    Example:
        >>> correlation_id = create_correlation_id()
        >>> print(correlation_id)  # e.g., "550e8400-e29b-41d4-a716-446655440000"
    """
    return str(uuid.uuid4())


_correlation_context = threading.local()


class LogContext:
    """Context manager for correlation ID and contextual logging.

    Manages correlation IDs for distributed tracing, ensuring all log messages
    within the context share the same correlation ID. Supports nesting with
    automatic restoration of previous context on exit.

    Attributes:
        correlation_id: The correlation ID for this context.
        additional_context: Extra context data attached to logs in this context.

    Example:
        >>> with LogContext(correlation_id="request-123") as ctx:
        ...     logger.info("Processing request")  # Includes correlation_id
        ...     with LogContext() as nested_ctx:
        ...         logger.info("Nested operation")  # New correlation_id
        ...     logger.info("Back to outer context")  # Original correlation_id
    """

    def __init__(self, correlation_id: str | None = None, additional_context: dict[str, Any] | None = None):
        """Initialize a new LogContext.

        Args:
            correlation_id: Optional correlation ID. If not provided, a new UUID is generated.
            additional_context: Optional dictionary of additional context to include in logs.
        """
        self.correlation_id = correlation_id or create_correlation_id()
        self.additional_context = additional_context or {}
        self.previous_context = getattr(_correlation_context, 'correlation_id', None)

    def __enter__(self) -> "LogContext":
        """Enter the context, setting the correlation ID for subsequent logs.

        Returns:
            The LogContext instance.
        """
        _correlation_context.correlation_id = self.correlation_id
        _correlation_context.additional_context = self.additional_context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context, restoring the previous correlation ID if any.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception value if an exception was raised.
            exc_tb: Exception traceback if an exception was raised.
        """
        if self.previous_context is not None:
            _correlation_context.correlation_id = self.previous_context
        elif hasattr(_correlation_context, 'correlation_id'):
            delattr(_correlation_context, 'correlation_id')


# Import PerformanceLogger and AuditLogger from their new locations for
# backward compatibility. Code that imports these from logger_config will
# continue to work.
from ..handlers.performance import PerformanceLogger  # noqa: E402
from ..audit.audit_logger import AuditLogger as _StandaloneAuditLogger  # noqa: E402, F401

# The AuditLogger class that was originally defined in logger_config.py
# is a different implementation from the standalone one in audit.py.
# We keep it here for backward compatibility since existing code imports
# it from logger_config.
import uuid as _uuid
from datetime import datetime as _datetime


class AuditLogger:
    """Logger specialized for security and compliance audit trails.

    Provides structured audit logging with immutable records containing
    actor, action, resource, outcome, and timestamp information. Designed
    for compliance and security audit requirements.

    Attributes:
        logger: The underlying logger instance configured for audit output.

    Example:
        >>> audit = AuditLogger(log_file="/var/log/audit.log")
        >>> audit.log("user:john", "update", "document:123", "success")
        >>> audit.log_access("user:jane", "file:/etc/passwd", "read", granted=False)
    """

    def __init__(self, logger_name: str = "audit", log_file: str | None = None):
        """Initialize an AuditLogger.

        Args:
            logger_name: Name for the underlying logger. Defaults to "audit".
            log_file: Optional file path for audit log output. If provided,
                logs are written to this file in JSON format.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        formatter = JSONFormatter()
        if log_file:
            handler = logging.FileHandler(log_file, mode='a')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, actor: str, action: str, resource: str, outcome: str = "success", details: dict[str, Any] | None = None) -> None:
        """Record an audit event.

        Creates an immutable audit record with a unique ID, timestamp, and
        the provided event details.

        Args:
            actor: The entity performing the action (e.g., "user:john", "service:api").
            action: The action being performed (e.g., "create", "delete", "update").
            resource: The resource being acted upon (e.g., "document:123", "user:456").
            outcome: The result of the action ("success", "failure", "denied").
                Defaults to "success".
            details: Optional dictionary of additional details about the event.

        Returns:
            None

        Example:
            >>> audit.log("user:admin", "delete", "user:inactive_user", "success",
            ...           {"reason": "account_expired", "requested_by": "system"})
        """
        audit_record = {
            "audit_id": str(_uuid.uuid4()),
            "timestamp": _datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "details": details or {}
        }
        self.logger.info(f"AUDIT: {actor} {action} {resource} -> {outcome}", extra={"audit": audit_record})

    def log_access(self, actor: str, resource: str, access_type: str = "read", granted: bool = True) -> None:
        """Record an access control event.

        Convenience method for logging resource access attempts with
        granted/denied outcomes.

        Args:
            actor: The entity attempting access (e.g., "user:john").
            resource: The resource being accessed (e.g., "file:/data/secret.txt").
            access_type: The type of access attempted ("read", "write", "execute").
                Defaults to "read".
            granted: Whether access was granted. Defaults to True.

        Returns:
            None

        Example:
            >>> audit.log_access("user:guest", "admin_panel", "read", granted=False)
            >>> audit.log_access("user:admin", "config_file", "write", granted=True)
        """
        self.log(actor=actor, action=f"access:{access_type}", resource=resource, outcome="granted" if granted else "denied")
