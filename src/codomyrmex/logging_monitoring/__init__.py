"""
Codomyrmex Logging Monitoring Module.

This module provides centralized logging facilities for the Codomyrmex project.
It allows for consistent log formatting, configurable log levels, and outputs
(console, file) across all other modules.

To use:
1. Ensure `python-dotenv` is installed (usually in the root `pyproject.toml`).
2. Create a `.env` file in the project root to specify logging configurations:
   - `CODOMYRMEX_LOG_LEVEL` (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - `CODOMYRMEX_LOG_FILE` (e.g., /path/to/codomyrmex.log)
   - `CODOMYRMEX_LOG_FORMAT` (e.g., "%(asctime)s - %(name)s - %(levelname)s - %(message)s" or "DETAILED")
3. In your main application script, call `setup_logging()` once at the beginning:
   ```python
   from codomyrmex.logging_monitoring import setup_logging
   setup_logging()
   ```
4. In any module, get a logger instance:
   ```python
   from codomyrmex.logging_monitoring import get_logger
   logger = get_logger(__name__)
   logger.info("This is an informational message.")
   ```

Subpackages:
    core/       - Logger configuration, setup, context management
    formatters/ - Structured log formatters (JSON)
    audit/      - Security and compliance audit logging
    handlers/   - Log handlers (rotation, performance)
"""

# This file makes the 'logging_monitoring' directory a Python package.

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .core.logger_config import get_logger, setup_logging

# Correlation ID propagation (v0.2.0 Stream 3)
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

def cli_commands():
    """Return CLI commands for the logging_monitoring module."""
    def _show_config():
        import os
        print("Logging configuration:")
        print(f"  CODOMYRMEX_LOG_LEVEL: {os.environ.get('CODOMYRMEX_LOG_LEVEL', 'INFO (default)')}")
        print(f"  CODOMYRMEX_LOG_FILE: {os.environ.get('CODOMYRMEX_LOG_FILE', 'None (console only)')}")
        print(f"  CODOMYRMEX_LOG_FORMAT: {os.environ.get('CODOMYRMEX_LOG_FORMAT', 'default')}")

    def _list_levels():
        import logging
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        print("Available log levels:")
        for level in levels:
            value = getattr(logging, level)
            print(f"  {level} ({value})")

    return {
        "config": _show_config,
        "levels": _list_levels,
    }


__all__ = [
    "cli_commands",
    "setup_logging",
    "get_logger",
    # v0.2.0 correlation
    "new_correlation_id",
    "get_correlation_id",
    "set_correlation_id",
    "clear_correlation_id",
    "with_correlation",
    "CorrelationFilter",
    "enrich_event_data",
    "create_mcp_correlation_header",
]
