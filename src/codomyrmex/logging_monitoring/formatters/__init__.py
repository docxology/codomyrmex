"""Logging formatters subpackage.

Provides structured log formatters for the Codomyrmex logging system.
The primary formatter is JSONFormatter, which outputs log records as
JSON objects for structured logging and log aggregation.
"""

from .json_formatter import JSONFormatter

__all__ = ["JSONFormatter"]
