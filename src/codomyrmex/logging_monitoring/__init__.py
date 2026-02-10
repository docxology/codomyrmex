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
"""

# This file makes the 'logging_monitoring' directory a Python package.

from .logger_config import get_logger, setup_logging

__all__ = ["setup_logging", "get_logger"]
