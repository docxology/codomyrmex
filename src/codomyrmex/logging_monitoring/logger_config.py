"""
Logger Configuration Module - Backward Compatibility Shim.

This module re-exports all symbols from their new canonical location in
core/logger_config.py. All existing import paths continue to work unchanged,
including module-level attribute access (e.g., logger_config._logging_configured).

The canonical implementations now live in:
    - core/logger_config.py: setup_logging, get_logger, log_with_context,
      create_correlation_id, LogContext, JSONFormatter, AuditLogger,
      DEFAULT_LOG_FORMAT, DETAILED_LOG_FORMAT
    - handlers/performance.py: PerformanceLogger

For new code, prefer importing from the top-level package:
    >>> from codomyrmex.logging_monitoring import setup_logging, get_logger
"""

import sys as _sys

# Import the canonical module
from .core import logger_config as _canonical  # noqa: F401

# Replace this shim module in sys.modules with the canonical module.
# This ensures that `from codomyrmex.logging_monitoring import logger_config`
# and `from codomyrmex.logging_monitoring.logger_config import X` both resolve
# to the same module, and mutable module-level state (like _logging_configured)
# is shared correctly.
_sys.modules[__name__] = _canonical
