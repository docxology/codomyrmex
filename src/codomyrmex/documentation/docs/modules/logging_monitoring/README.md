<!-- readme: generated -->

# logging_monitoring

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/logging_monitoring/`

## Overview

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

## Public Exports

`logging_monitoring` exports 20 public symbols via `__all__`:

`DEFAULT_LOG_FORMAT`, `DETAILED_LOG_FORMAT`, `CorrelationFilter`, `JSONFormatter`, `LogContext`, `PerformanceLogger`, `clear_correlation_id`, `cli_commands`, `configure_all_structured`, `create_correlation_id`, `create_mcp_correlation_header`, `enable_structured_json`, `enrich_event_data`, `get_correlation_id`, `get_logger`, `log_with_context`, `new_correlation_id`, `set_correlation_id`, `setup_logging`, `with_correlation`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../logging_monitoring/](../../../../logging_monitoring/)
