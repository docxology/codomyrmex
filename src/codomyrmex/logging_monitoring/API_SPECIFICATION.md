# Logging Monitoring - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Logging Monitoring module. The primary purpose of this API is to provide a centralized and configurable way for other modules within the Codomyrmex project to perform logging.

## Endpoints / Functions / Interfaces

### Function 1: `setup_logging()`

- **Description**: Initializes and configures the logging system for the entire Codomyrmex application. This function should be called once, typically at the application's entry point. It configures aspects like log level, log format, and log output destinations (console, file) based on environment variables or sensible defaults.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - This function currently takes no direct arguments. It reads its configuration from environment variables:
        - `CODOMYRMEX_LOG_LEVEL` (str, optional): Sets the logging threshold. Examples: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL". Defaults to "INFO".
        - `CODOMYRMEX_LOG_FILE` (str, optional): Path to a file where logs should be written. If not provided or empty, logs are only sent to the console. Example: `logs/app.log`.
        - `CODOMYRMEX_LOG_FORMAT` (str, optional): A Python logging format string or the keyword "DETAILED" for text output. Defaults to `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`. "DETAILED" uses `"%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"`. This is ignored if `CODOMYRMEX_LOG_OUTPUT_TYPE` is "JSON".
        - `CODOMYRMEX_LOG_OUTPUT_TYPE` (str, optional): Specifies the log output format. Can be "TEXT" or "JSON". Defaults to "TEXT".
- **Request Body**: N/A
- **Returns/Response**: None. This function configures the logging system as a side effect.
- **Events Emitted**: N/A
- **Idempotency**: The function is designed to be idempotent; subsequent calls after the first successful configuration will have no further effect.

### Function 2: `get_logger(name: str)`

- **Description**: Retrieves a `logging.Logger` instance, configured according to the settings applied by `setup_logging()`. This is the primary way other modules should obtain a logger to emit messages.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `name` (str): The name for the logger. It is highly recommended to use the `__name__` special variable of the calling module for this argument (e.g., `logger = get_logger(__name__)`). This helps in identifying the source of log messages.
- **Request Body**: N/A
- **Returns/Response**:
    - `logging.Logger`: An instance of a Python logger, ready for use.
- **Events Emitted**: N/A

### Function 3: `log_with_context(level: str, message: str, context: Dict[str, Any])`

- **Description**: Logs a message with structured context information, automatically including correlation IDs if available in the current log context.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `level` (str): Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    - `message` (str): Log message text
    - `context` (Dict[str, Any]): Dictionary of context information to include in the log entry
- **Request Body**: N/A
- **Returns/Response**: None
- **Events Emitted**: N/A

### Function 4: `create_correlation_id() -> str`

- **Description**: Generates a unique correlation ID using UUID4 for request tracing and log correlation.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**: None
- **Request Body**: N/A
- **Returns/Response**: `str` - UUID-based correlation ID string
- **Events Emitted**: N/A

### Class 1: `LogContext`

- **Description**: Context manager for automatic correlation ID injection in logs. Manages thread-local correlation context.
- **Method**: N/A (Python class)
- **Parameters/Arguments** (constructor):
    - `correlation_id` (Optional[str]): Optional correlation ID, generates one if not provided
    - `additional_context` (Optional[Dict[str, Any]]): Additional context to include in logs
- **Methods**:
    - `__enter__()`: Sets up the correlation context
    - `__exit__(exc_type, exc_val, exc_tb)`: Cleans up the correlation context
- **Events Emitted**: N/A

### Class 2: `PerformanceLogger`

- **Description**: Specialized logger for performance metrics and operation timing.
- **Method**: N/A (Python class)
- **Parameters/Arguments** (constructor):
    - `logger_name` (str, optional): Name for the logger instance (default: "performance")
- **Methods**:
    - `start_timer(operation: str, context: Optional[Dict[str, Any]] = None)`: Start timing an operation
    - `end_timer(operation: str, context: Optional[Dict[str, Any]] = None) -> float`: End timing and return duration
    - `time_operation(operation: str, context: Optional[Dict[str, Any]] = None)`: Context manager for timing operations
    - `log_metric(metric_name: str, value: Any, unit: Optional[str] = None, context: Optional[Dict[str, Any]] = None)`: Log performance metrics
- **Events Emitted**: N/A

## Data Models

(No specific complex data models are exposed by this logging API beyond standard Python types and `logging.Logger` objects.)

## Authentication & Authorization

(Not applicable for this internal logging module.)

## Rate Limiting

(Not applicable for this internal logging module.)

## Versioning

(This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.) 