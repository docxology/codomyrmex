# DEPRECATED(v0.2.0): Shim module. Import from logging_monitoring.core.correlation instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: logging_monitoring.core.correlation"""
from .core.correlation import *  # noqa: F401,F403
from .core.correlation import (
    new_correlation_id,
    get_correlation_id,
    set_correlation_id,
    clear_correlation_id,
    with_correlation,
    CorrelationFilter,
    enrich_event_data,
    create_mcp_correlation_header,
)
