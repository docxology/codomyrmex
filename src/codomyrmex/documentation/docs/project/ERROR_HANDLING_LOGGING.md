# Project-Wide Error Handling and Logging Best Practices

This document outlines the best practices for error handling and logging within the Codomyrmex project. Consistent and effective error management is crucial for maintainability, debugging, and operational stability.

## 1. Core Principles

*   **Clarity**: Error messages, both in exceptions and logs, should be clear, concise, and provide sufficient context to understand the problem.
*   **Consistency**: Follow consistent patterns for raising exceptions, logging errors, and formatting messages across all modules.
*   **Actionability**: Errors should, where possible, guide developers or users towards a resolution or provide enough information for effective debugging.
*   **Structured Logging**: Utilize the centralized `logging_monitoring` module, which should be configured for structured logging (e.g., JSON format) to facilitate easier parsing, searching, and analysis by log management systems.
*   **Fail Fast, Fail Loud (Appropriately)**: For unrecoverable errors or invalid states, it's generally better to raise an exception promptly rather than continuing in an unpredictable state. However, for user-facing components or resilient services, provide graceful degradation or informative error messages.

## 2. Exception Handling

### 2.1. When to Raise Exceptions

*   **Invalid Input/State**: Raise exceptions when a function or method receives invalid arguments that prevent it from performing its operation, or when an object is in an invalid state for a requested operation.
    *   Use built-in exceptions like `ValueError`, `TypeError` where appropriate.
    *   Define custom exceptions for application-specific error conditions (see section 2.4).
*   **External System Failures**: When an interaction with an external system (e.g., database, API, file system) fails in an unrecoverable way for the current operation.
*   **Contract Violations**: If a function's preconditions are not met or postconditions cannot be satisfied.

### 2.2. When *Not* to Raise Exceptions (or to catch and handle)

*   **Expected/Alternative Flows**: If an error condition is an expected part of a workflow and can be handled gracefully (e.g., file not found when it's optional, optimistic locking failure that can be retried), consider returning a specific value (e.g., `None`, an empty list, a status object) or handling it internally rather than raising an exception that bubbles up unnecessarily.
*   **User Input Validation**: For direct user input (e.g., in a CLI or API), catch validation errors and return informative messages to the user rather than letting raw exceptions propagate.

### 2.3. Catching Exceptions

*   **Be Specific**: Catch the most specific exception type possible (e.g., `except FileNotFoundError:` instead of `except Exception:`). Avoid overly broad `except` clauses that can hide unrelated bugs.
*   **Handle or Re-raise**: If you catch an exception, either handle it meaningfully (e.g., retry, return a default, log and continue if appropriate) or re-raise it (or a new, more specific exception wrapping the original) if the current level cannot handle it.
*   **Don't Suppress Unnecessarily**: Avoid catching exceptions and doing nothing (`pass`) unless you have a very specific and justified reason. This can make debugging very difficult.
*   **Contextual Logging**: When catching and handling an exception, log it with sufficient context (see Logging section).

### 2.4. Custom Exceptions

*   Define custom exception classes that inherit from Python's `Exception` or more specific built-in exceptions. This allows for more granular error handling.
*   Place module-specific custom exceptions within the module itself (e.g., `ai_code_editing/exceptions.py`).
*   Consider a base custom exception for the project (e.g., `CodomyrmexError`) if common project-wide error handling logic is needed.

    ```python
    # Example: my_module/exceptions.py
    class MyModuleError(Exception):
        """Base exception for MyModule."""
        pass

    class ConfigurationError(MyModuleError):
        """Indicates an error in module configuration."""
        pass

    class ProcessingError(MyModuleError):
        """Indicates an error during data processing."""
        def __init__(self, message, details=None):
            super().__init__(message)
            self.details = details # Optional additional structured details
    ```

### 2.5. Exception Chaining

*   When catching an exception and raising a new one, use exception chaining (`raise NewException("...") from original_exception`) to preserve the context of the original error. This is the default behavior in Python 3 if an exception is raised from within an `except` block.

## 3. Logging Practices

All logging should be done via the `get_logger` function from the `logging_monitoring.logger_config` module.

### 3.1. Log Levels

Use appropriate log levels:

*   **`DEBUG`**: Detailed information, typically of interest only when diagnosing problems. Includes verbose information about program state, variable values, etc.
*   **`INFO`**: Confirmation that things are working as expected. General operational messages, start/stop of services, significant events.
*   **`WARNING`**: An indication that something unexpected happened, or indicative of some problem in the near future (e.g., 'disk space low'). The software is still working as expected.
*   **`ERROR`**: Due to a more serious problem, the software has not been able to perform some function. Typically used when exceptions are caught and handled, or a significant operation failed.
*   **`CRITICAL`**: A serious error, indicating that the program itself may be unable to continue running.

### 3.2. What to Log

*   **Key Decisions and Actions**: Log important decisions made by the application and actions taken (e.g., "User X initiated process Y", "Configuration loaded from Z").
*   **Errors and Exceptions**:
    *   Always log exceptions that are caught and handled, especially if they are not re-raised. Include the stack trace if it's helpful (the logger configuration can handle this).
    *   Log errors from external systems.
*   **Contextual Information**: Include relevant contextual data in log messages. Structured logging helps here.
    *   Instead of: `logger.error("Failed to process item")`
    *   Prefer: `logger.error("Failed to process item", item_id=item.id, user_id=user.id, error_details=str(e))`
    *   The `logging_monitoring` module should be configured to allow passing extra keyword arguments to log methods, which are then included in the structured log output.
*   **Performance Metrics (Optional/Specific Cases)**: For critical operations, log start/end times or duration. (Consider dedicated metrics systems for extensive performance monitoring).

### 3.3. How to Log

*   **Use f-strings or `%(key)s` style formatting for messages**: The logger itself will handle the formatting. Let the logger handle message formatting for performance and flexibility.
    *   Good: `logger.info("Processing file %s for user %s", filename, user_id)`
    *   Also good (if logger is configured for structured logging with `extra`): `logger.info("Processing file", filename=filename, user_id=user_id)`
    *   Avoid: `logger.info(f"Processing file {filename} for user {user_id}")` if the message string itself is logged as a single entity and not further processed by handlers for structured data. The `logging_monitoring` module's `get_logger` should ideally provide a logger that supports structured logging naturally.
*   **One Event, One Log Entry**: Avoid splitting a single logical event across multiple log lines if possible.
*   **Avoid Logging Sensitive Information**: Be extremely careful not to log passwords, API keys, personal identifiable information (PII), or other sensitive data unless explicitly required and properly secured (e.g., encrypted logs, access controls). Implement filtering or scrubbing if necessary.

### 3.4. Log Message Format (Guidance for `logging_monitoring` configuration)

The `logging_monitoring` module should ideally be configured to output logs in a structured format (e.g., JSON). A typical structured log entry might include:

*   `timestamp`: Time of the log event (ISO 8601 format).
*   `level`: Log level (e.g., "INFO", "ERROR").
*   `name`: Name of the logger (e.g., "my_module.my_component").
*   `message`: The main log message.
*   `module`: The Python module where the log originated.
*   `funcName`: The function name where the log originated.
*   `lineno`: The line number where the log originated.
*   `exc_info` (if an exception occurred and logged): Stack trace.
*   Any additional key-value pairs passed as `extra` to the logging call (e.g., `item_id`, `user_id`).

## 4. Integration with `logging_monitoring`

*   **Import**: `from logging_monitoring.logger_config import get_logger`
*   **Initialization**: `logger = get_logger(__name__)` at the module level.
*   **Usage**: `logger.info("An event occurred")`, `logger.error("An error happened", exc_info=True)` (or let logger config handle `exc_info` automatically for errors).

## 5. Review and Evolution

These guidelines should be reviewed periodically and updated as the project evolves and new patterns or challenges emerge. 