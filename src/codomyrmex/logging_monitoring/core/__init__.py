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
from .correlation import (
    new_correlation_id,
    get_correlation_id,
    set_correlation_id,
    clear_correlation_id,
    with_correlation,
    CorrelationFilter,
    enrich_event_data,
    create_mcp_correlation_header,
)
from .log_aggregator import *  # noqa: F401,F403

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
