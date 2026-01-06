# Codomyrmex Agents — src/codomyrmex/logging_monitoring

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Logging Monitoring Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Foundation module providing centralized logging infrastructure for the Codomyrmex platform. This module implements a unified logging system that ensures consistent log formatting, configurable output destinations, and proper log level management across all platform components.

The logging_monitoring module serves as the backbone for observability, enabling debugging, monitoring, and troubleshooting throughout the entire Codomyrmex ecosystem.

## Module Overview

### Key Capabilities
- **Centralized Configuration**: Unified logging setup via environment variables and configuration files
- **Multiple Output Formats**: Support for text and JSON log formats
- **Flexible Destinations**: Console and file output with configurable paths
- **Structured Logging**: JSON formatter for machine-readable logs
- **Logger Factory**: Consistent logger instantiation across modules

### Key Features
- Environment-based configuration (log level, format, output type)
- Custom JSON formatter with timestamps and structured data
- Hierarchical logger naming for clear source identification
- Performance-optimized logging with minimal overhead
- Integration with Python's standard logging framework

## Function Signatures

### Core Functions

```python
def setup_logging() -> None
```

Initializes and configures the logging system for the entire Codomyrmex application. This function should be called once, typically at the application's entry point.

**Environment Variables:**
- `CODOMYRMEX_LOG_LEVEL` (str, optional): Sets the logging threshold ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"). Defaults to "INFO"
- `CODOMYRMEX_LOG_FILE` (str, optional): Path to a file where logs should be written. If not provided, logs go to console only
- `CODOMYRMEX_LOG_FORMAT` (str, optional): Python logging format string or "DETAILED" for text output. Ignored if output type is "JSON"
- `CODOMYRMEX_LOG_OUTPUT_TYPE` (str, optional): Log output format ("TEXT" or "JSON"). Defaults to "TEXT"

**Returns:** None (configures logging as a side effect)

**Side Effects**:
- Configures Python's logging system using `logging.basicConfig()`
- Sets log levels for verbose libraries (httpx, httpcore)
- Creates console and optional file handlers

```python
def get_logger(name: str) -> logging.Logger
```

Retrieves a configured `logging.Logger` instance. This is the primary way other modules should obtain a logger.

**Parameters:**
- `name` (str): The name for the logger. Recommended to use `__name__` from the calling module

**Returns:** `logging.Logger` instance ready for use

**Note**: If `setup_logging()` hasn't been called, returns logger with default Python configuration

### Advanced Logging Functions

```python
def log_with_context(level: str, message: str, context: Dict[str, Any]) -> None
```

Log a message with structured context information.

**Parameters:**
- `level` (str): Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `message` (str): Log message
- `context` (Dict[str, Any]): Dictionary of context information to include in the log

**Behavior**: Adds context as extra fields; includes correlation ID if available

```python
def create_correlation_id() -> str
```

Generate a unique correlation ID for request tracing using UUID.

**Returns:** `str` - UUID-based correlation ID string

### Context Managers

```python
class LogContext:
    def __init__(
        self,
        correlation_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> None
```

Context manager for automatic correlation ID injection in logs.

**Parameters:**
- `correlation_id` (Optional[str]): Correlation ID to use (generates one if not provided)
- `additional_context` (Optional[Dict[str, Any]]): Additional context to include in logs

**Usage**:
```python
with LogContext(correlation_id="req-123") as ctx:
    logger.info("Processing request")  # Correlation ID automatically added
```

**Methods:**
- `__enter__(self) -> LogContext`: Enter context, set thread-local correlation ID
- `__exit__(self, exc_type, exc_val, exc_tb) -> None`: Exit context, restore previous ID

### Performance Logging

```python
class PerformanceLogger:
    def __init__(self, logger_name: str = "performance") -> None
```

Specialized logger for performance metrics and timing.

**Parameters:**
- `logger_name` (str): Name for the logger instance. Defaults to "performance"

**Methods:**

```python
def start_timer(self, operation: str, context: Optional[Dict[str, Any]] = None) -> None
```

Start timing an operation.

**Parameters:**
- `operation` (str): Name of the operation being timed
- `context` (Optional[Dict[str, Any]]): Additional context for the operation

```python
def end_timer(self, operation: str, context: Optional[Dict[str, Any]] = None) -> float
```

End timing an operation and log the duration.

**Parameters:**
- `operation` (str): Name of the operation being timed
- `context` (Optional[Dict[str, Any]]): Additional context for the operation

**Returns:** `float` - Duration in seconds

```python
@contextmanager
def time_operation(self, operation: str, context: Optional[Dict[str, Any]] = None)
```

Context manager for timing operations.

**Parameters:**
- `operation` (str): Name of the operation being timed
- `context` (Optional[Dict[str, Any]]): Additional context for the operation

**Usage**:
```python
perf_logger = PerformanceLogger()
with perf_logger.time_operation("database_query"):
    # Code to time
    pass
```

```python
def log_metric(
    self,
    metric_name: str,
    value: Any,
    unit: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> None
```

Log a performance metric.

**Parameters:**
- `metric_name` (str): Name of the metric
- `value` (Any): Metric value
- `unit` (Optional[str]): Unit of measurement (e.g., "ms", "MB", "requests/sec")
- `context` (Optional[Dict[str, Any]]): Additional context

### Custom Formatters

```python
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str
```

Custom JSON formatter for machine-readable logs.

**Parameters:**
- `record` (logging.LogRecord): Log record to format

**Returns:** `str` - JSON-formatted log entry

**Output Format**:
```json
{
  "timestamp": "2025-12-26T10:30:00.000Z",
  "level": "INFO",
  "name": "module.name",
  "module": "module",
  "funcName": "function_name",
  "lineno": 42,
  "message": "Log message",
  "extra": {...}
}
```

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `logger_config.py` – Main logging configuration and utilities

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations and best practices
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite


### Additional Files
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `docs` – Docs
- `tests` – Tests

## Operating Contracts

### Universal Logging Protocols

All logging within the Codomyrmex platform must:

1. **Use Centralized Configuration** - All modules obtain loggers via `get_logger(__name__)` from this module
2. **Follow Consistent Naming** - Logger names should match module hierarchy for clear identification
3. **Respect Log Levels** - Appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) for different message types
4. **Include Context** - Log messages should provide sufficient context for debugging and monitoring
5. **Handle Sensitive Data** - Never log passwords, API keys, or other sensitive information

### Module-Specific Guidelines

#### Logger Usage
- Import logger at module level: `logger = get_logger(__name__)`
- Use appropriate log levels for different scenarios
- Include relevant context in log messages
- Avoid excessive logging in performance-critical paths

#### Configuration Management
- Configure logging once at application startup via `setup_logging()`
- Use environment variables for runtime configuration
- Support both development and production logging needs
- Enable JSON logging for production monitoring systems

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation