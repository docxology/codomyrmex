"""Core logging configuration subpackage.

Provides the fundamental logging setup, logger retrieval, context management,
and correlation ID generation for the Codomyrmex logging system.
"""

from .logger_config import (
    AuditLogger,
    DEFAULT_LOG_FORMAT,
    DETAILED_LOG_FORMAT,
    JSONFormatter,
    LogContext,
    create_correlation_id,
    get_logger,
    log_with_context,
    setup_logging,
)
from ..handlers.performance import PerformanceLogger

__all__ = [
    "AuditLogger",
    "DEFAULT_LOG_FORMAT",
    "DETAILED_LOG_FORMAT",
    "JSONFormatter",
    "LogContext",
    "PerformanceLogger",
    "create_correlation_id",
    "get_logger",
    "log_with_context",
    "setup_logging",
]
