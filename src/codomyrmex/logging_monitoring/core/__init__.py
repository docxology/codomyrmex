"""Core logging configuration subpackage.

Provides the fundamental logging setup, logger retrieval, context management,
and correlation ID generation for the Codomyrmex logging system.
"""

from codomyrmex.logging_monitoring.handlers.performance import PerformanceLogger

from .correlation import (
    CorrelationFilter,
    clear_correlation_id,
    create_mcp_correlation_header,
    enrich_event_data,
    get_correlation_id,
    new_correlation_id,
    set_correlation_id,
    with_correlation,
)
from .log_aggregator import *
from .logger_config import (
    DEFAULT_LOG_FORMAT,
    DETAILED_LOG_FORMAT,
    AuditLogger,
    JSONFormatter,
    LogContext,
    create_correlation_id,
    get_logger,
    log_with_context,
    setup_logging,
)

__all__ = [
    "DEFAULT_LOG_FORMAT",
    "DETAILED_LOG_FORMAT",
    "AuditLogger",
    "JSONFormatter",
    "LogContext",
    "PerformanceLogger",
    "create_correlation_id",
    "get_logger",
    "log_with_context",
    "setup_logging",
]
