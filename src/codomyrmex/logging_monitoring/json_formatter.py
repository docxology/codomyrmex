"""Structured JSON formatter - Backward Compatibility Shim.

This module re-exports JSONFormatter from its new location in the
formatters subpackage. All existing import paths continue to work unchanged.

The canonical implementation now lives in:
    formatters/json_formatter.py

For new code, prefer:
    >>> from codomyrmex.logging_monitoring.formatters import JSONFormatter
"""

from .formatters.json_formatter import JSONFormatter  # noqa: F401
