# Codomyrmex Agents — src/codomyrmex/logging_monitoring

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Centralized logging infrastructure for the Codomyrmex platform. Implements unified logging system with consistent formatting, configurable output destinations (console, file), configurable log levels, JSON and text formatters, and proper log level management. Provides singleton-like configuration ensuring logging is set up once for the entire application.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `docs/` – Directory containing docs components
- `logger_config.py` – Core logging configuration implementation
- `requirements.txt` – Project file
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Module Functions (`logger_config.py`)
- `setup_logging() -> None` – Initialize and configure the logging system for the entire application (idempotent, reads from environment variables)
- `get_logger(name: str) -> Logger` – Get a logger instance for a module (standard way: `get_logger(__name__)`)

### Configuration Environment Variables
- `CODOMYRMEX_LOG_LEVEL` (str, optional) – Logging threshold: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" (default: "INFO")
- `CODOMYRMEX_LOG_FILE` (str, optional) – Path to log file (if not provided, logs only to console)
- `CODOMYRMEX_LOG_FORMAT` (str, optional) – Python logging format string or "DETAILED" keyword (default: standard format)
- `CODOMYRMEX_LOG_OUTPUT_TYPE` (str, optional) – Output format: "TEXT" or "JSON" (default: "TEXT")

### JsonFormatter (`logger_config.py`)
- `JsonFormatter` – JSON formatter for structured logging output

### LogContext (`logger_config.py`)
- `LogContext` – Context manager for structured logging with context information

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation