---
sidebar_label: 'Logging & Monitoring'
title: 'Logging & Monitoring Module'
slug: /modules/logging_monitoring
---

# Logging & Monitoring

## Overview

The Logging & Monitoring module provides a centralized and configurable logging mechanism for all Codomyrmex modules. It aims to offer a simple, flexible, and consistent way to record application events, errors, and diagnostic information.

Key features include:
- Easy setup via a single function call: `setup_logging()`.
- Configuration through environment variables (leveraging `.env` files via `python-dotenv`).
- Support for standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Customizable log formats for text output, including a "DETAILED" predefined format.
- Option for structured JSON log output for easier parsing by log management systems.
- Output to console and/or a log file.
- Straightforward integration into other modules using the standard Python `logging.getLogger(__name__)` pattern, facilitated by a helper `get_logger(__name__)` function.

## Key Components

- **`logger_config.py`**: This core file contains the primary logic:
    - `setup_logging()`: Initializes and configures the Python root logger based on environment variables or sensible defaults. This should be called once at application startup.
    - `get_logger(name: str)`: A simple factory function that other modules use to obtain a named `logging.Logger` instance, ensuring consistency.
- **Environment Variables**: Configuration is primarily managed via environment variables (see Configuration section below), loaded from a `.env` file in the project root.

## Integration Points

- **Provides**:
    - `setup_logging()`: A function to be called once at application startup to configure the entire logging system for the project.
    - `get_logger(name: str)`: A utility function that returns a standard `logging.Logger` instance, allowing other modules to emit log messages through the centrally configured system.
    - These are exposed for import: `from codomyrmex.logging_monitoring import setup_logging, get_logger`.
- **Consumes**:
    - **Environment Variables**: For configuration (e.g., `CODOMYRMEX_LOG_LEVEL`, `CODOMYRMEX_LOG_FILE`, `CODOMYRMEX_LOG_FORMAT`, `CODOMYRMEX_LOG_OUTPUT_TYPE`). It relies on `python-dotenv` (expected to be a project-level dependency) to load these from a `.env` file.
    - **Standard Python `logging` module**: This module configures and utilizes the built-in `logging` library.
- Refer to the [API Specification](./API_SPECIFICATION.md) for detailed programmatic interfaces. The [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) is currently N/A as this module provides internal logging utilities rather than agent-callable tools.

## Getting Started

To use the logging module within the Codomyrmex project:

### Prerequisites

- Python 3.7+ (as per project standard; specific features like `force=True` in `logging.basicConfig` benefit from this).
- The `python-dotenv` package must be installed in the project's Python environment. This is typically handled by the root `requirements.txt` and the general project `environment_setup` process.

### Installation

This module is an integral part of the Codomyrmex project. No separate installation steps are required beyond cloning the main repository and setting up the project's Python environment as per the `environment_setup/README.md`.

### Configuration

The logging behavior is configured via environment variables, typically set in a `.env` file in the project root directory.

1.  **Create/Update `.env` file**:
    In the root directory of the Codomyrmex project (e.g., alongside the main `requirements.txt`), create or update a `.env` file. Add the following variables to customize logging (all are optional; defaults will be used if not set):

    ```env
    # Codomyrmex Logging Configuration
    CODOMYRMEX_LOG_LEVEL=INFO          # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default: INFO.
    CODOMYRMEX_LOG_FILE=logs/codomyrmex.log  # Path to log file. If commented out, blank, or not set, logs to console only.
                                        # Ensure the 'logs/' directory exists or the application has permission to create it.
    CODOMYRMEX_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s" # Custom Python logging format string.
                                        # Alternatively, use "DETAILED" for a predefined detailed format.
                                        # This is ignored if CODOMYRMEX_LOG_OUTPUT_TYPE=JSON. Default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s".
    CODOMYRMEX_LOG_OUTPUT_TYPE=TEXT    # Options: "TEXT" or "JSON". Default: TEXT.
    ```
    **Note**: The logging system itself does not create directories for `CODOMYRMEX_LOG_FILE`. Ensure the specified path is writable or the directory exists.

2.  **Initialize Logging in Your Main Application Script**:
    Call `setup_logging()` once at the very beginning of your main application script or entry point.

    ```python
    # Example: main_project_script.py
    from codomyrmex.logging_monitoring import setup_logging, get_logger

    def main_application_logic():
        # First thing to do is set up logging
        setup_logging()

        logger = get_logger(__name__) # Get a logger for this main script
        logger.info("Application starting up...")
        # ... rest of your application initialization and logic ...
        logger.info("Application finished its main task.")

    if __name__ == "__main__":
        main_application_logic()
    ```

3.  **Use Loggers in Other Modules**:
    In any other module of the Codomyrmex project, simply import and use `get_logger`.

    ```python
    # Example: codomyrmex/some_other_module/utils.py
    from codomyrmex.logging_monitoring import get_logger

    # It's a best practice to use the module's __name__ for the logger
    logger = get_logger(__name__)

    def process_data(data):
        logger.debug(f"Received data: {data}")
        try:
            result = perform_complex_operation(data)
            logger.info("Data processing successful.")
            return result
        except ValueError as e:
            logger.error(f"Error processing data: {str(e)}", exc_info=True) # Log exception details
            # exc_info=True automatically adds traceback information to the log record
            raise # Re-raise the exception or handle as appropriate
    ```

## Development

Developers contributing to this module should focus on maintaining its simplicity, reliability, and adherence to standard Python logging practices.

### Code Structure

The module is straightforward:
- `__init__.py`: Exports the public functions `setup_logging` and `get_logger` from `logger_config`.
- `logger_config.py`: Contains the core implementation of `setup_logging` and the `get_logger` utility. It includes logic for parsing environment variables, setting up log handlers (console, file), and formatters (text, JSON).
- `docs/`, `tests/`, etc.: Standard supporting directories.

For a more detailed architectural view, if needed, refer to the [Technical Overview](./docs/technical_overview.md) (currently a placeholder).

### Building & Testing

- **Building**: This module is Python-based and does not have a separate build step beyond normal Python packaging if the project were to be distributed.
- **Testing**:
    1.  **Install Dependencies**: Ensure all project development dependencies (like `pytest`, `python-dotenv`) are installed from the root `requirements.txt`.
    2.  **Run Tests**: Unit tests for `logger_config.py` should be located in `logging_monitoring/tests/unit/`. These tests would typically involve:
        - Mocking environment variables (`os.environ`).
        - Checking that `logging.basicConfig` or `logging.getLogger().addHandler` are called with correct parameters based on mocked env vars.
        - Verifying the types and configurations of handlers and formatters created.
        - Testing the `get_logger()` function.
        - Example command (from project root):
          ```bash
          pytest logging_monitoring/tests/
          ```
    - The `logger_config.py` file also contains a basic `if __name__ == '__main__':` block that can be run directly (`python -m codomyrmex.logging_monitoring.logger_config`) for a simple demonstration of its functionality with various environment variable settings (you might need to set them manually or use a temporary `.env` file for this direct run).
    - Refer to `logging_monitoring/tests/README.md` for specific instructions if available.

Ensure any contributions maintain or improve test coverage and adhere to project coding standards.

## Further Information

- [API Specification](./API_SPECIFICATION.md)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) (N/A for this module)
- [Usage Examples](./USAGE_EXAMPLES.md) (Primarily covered in "Getting Started" and API spec)
- [Detailed Documentation](./docs/index.md) (Placeholder for more in-depth guides if needed)
- [Changelog](./CHANGELOG.md)
- [Security Policy](./SECURITY.md) (Focuses on ensuring log content does not inadvertently expose sensitive data, and file logging paths are secure)