---
sidebar_label: 'Logging & Monitoring'
title: 'Logging & Monitoring Module'
slug: /modules/logging_monitoring
---

# Logging & Monitoring

## Overview

The Logging & Monitoring module provides a centralized and configurable logging mechanism for all Codomyrmex modules. It aims to offer a simple, flexible, and consistent way to record application events, errors, and diagnostic information.

Key features include:
- Easy setup via a single function call.
- Configuration through environment variables (leveraging `.env` files).
- Support for standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Customizable log formats.
- Output to console and/or a log file.
- Straightforward integration into other modules using a `get_logger(__name__)` pattern.

## Key Components

- **`logger_config.py`**: This core file contains the primary logic:
    - `setup_logging()`: Initializes and configures the logging system based on environment variables or sensible defaults.
    - `get_logger(name: str)`: A factory function that other modules use to obtain a named logger instance.
- **Environment Variables**: Configuration is primarily managed via environment variables (see Configuration section).

## Integration Points

- **Provides**:
    - `setup_logging()`: A function to be called once at application startup to configure the entire logging system.
    - `get_logger(name: str)`: A function that returns a `logging.Logger` instance, allowing other modules to emit log messages through the centralized system.
    - These are exposed via `from codomyrmex.logging_monitoring import setup_logging, get_logger`.
- **Consumes**:
    - Environment variables for configuration (e.g., `CODOMYRMEX_LOG_LEVEL`, `CODOMYRMEX_LOG_FILE`). It uses `python-dotenv` to load these from a `.env` file in the project root.
    - Relies on the standard Python `logging` module.
- Refer to the [API Specification](./api_specification.md) and [MCP Tool Specification](./mcp_tool_specification.md) (if applicable for future tools) for detailed programmatic interfaces.

## Getting Started

To use the logging module:

### Prerequisites

- Python 3.7+ (due to `logging.basicConfig(force=True)` usage, though `logging` itself is older).
- The `python-dotenv` package should be listed in the main project `requirements.txt` and installed in your environment. The [Environment Setup documentation](../environment_setup/index.md) provides guidance on this.

### Installation

This module is part of the Codomyrmex project. Ensure it's available in your Python path. No separate installation beyond project setup is typically required.

### Configuration

1.  **Create/Update `.env` file**:
    In the root directory of the Codomyrmex project, create or update a `.env` file. Add the following variables to customize logging (all are optional):

    ```env
    # Logging Configuration
    CODOMYRMEX_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL (Default: INFO)
    CODOMYRMEX_LOG_FILE=logs/codomyrmex.log  # Path to log file. If commented out or empty, logs to console only.
    CODOMYRMEX_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s" # Or use "DETAILED"
    # Example of detailed format: "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    ```
    *Ensure the directory for `CODOMYRMEX_LOG_FILE` (e.g., `logs/`) exists if you specify a file, or ensure the application has permissions to create it.* The logger does not create directories.

2.  **Initialize Logging in Your Main Application Script**:
    Call `setup_logging()` once at the beginning of your main application script or entry point.

    ```python
    # main_script.py or app.py
    from codomyrmex.logging_monitoring import setup_logging, get_logger # Corrected import path

    def main():
        setup_logging() # Initialize logging system
        # ... rest of your application logic ...
        logger = get_logger(__name__) # Example usage in main script
        logger.info("Application started.")

    if __name__ == "__main__":
        main()
    ```

3.  **Use Loggers in Other Modules**:
    In any other module, import `get_logger` and use it to obtain a logger instance.

    ```python
    # some_module.py
    from codomyrmex.logging_monitoring import get_logger # Corrected import path

    logger = get_logger(__name__) # Best practice to use module's name

    def my_function():
        logger.info("my_function was called.")
        try:
            # ... some operation ...
            result = 10 / 0
        except ZeroDivisionError as e:
            logger.error(f"An error occurred: {e}", exc_info=True) # Log exception info
    ```

## Development

(Information for developers contributing to this module.)

### Code Structure

- `__init__.py`: Exports public functions and provides module documentation.
- `logger_config.py`: Contains the core implementation of `setup_logging` and `get_logger`.

For a more detailed architectural view, see the [Technical Overview](./docs/technical_overview.md).

### Building & Testing

- To test this module, you can run `python -m logging_monitoring.logger_config` which includes a basic `if __name__ == '__main__':` block for demonstration.
- For integrated testing, ensure your main application calls `setup_logging()` and then verify log outputs based on your configuration when other modules use `get_logger()`.
- Refer to the main project's testing guidelines and the `tests/` directory within this module for specific test scripts.

## Further Information

- [API Specification](./api_specification.md)
- [MCP Tool Specification](./mcp_tool_specification.md) (If this module exposes tools via MCP - Not currently applicable for basic logging functions)
- [Usage Examples](./usage_examples.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](./changelog.md)
- [Security Policy](./security.md) 