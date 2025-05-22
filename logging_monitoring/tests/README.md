# Testing Logging Monitoring

This document describes how to run tests for the `logging_monitoring` module within the Codomyrmex project.

## Prerequisites

- **Python Environment**: A Python environment (3.7+ recommended) with `pytest` and `python-dotenv` installed. These are typically part of the main project's development dependencies (see root `requirements.txt`).
- **Project Root**: Tests should generally be run from the Codomyrmex project root directory to ensure correct path resolution for `.env` files and module imports.

## Running Tests

### Unit Tests

Unit tests for the `logging_monitoring` module are located in the `logging_monitoring/tests/unit/` directory. The primary file is `test_logger_config.py`.

To run these tests:

1.  Navigate to the project root directory in your terminal.
2.  Execute `pytest` targeting the module's test directory:

    ```bash
    pytest logging_monitoring/tests/unit/
    ```

    Alternatively, to run a specific test file:

    ```bash
    pytest logging_monitoring/tests/unit/test_logger_config.py
    ```

### Integration Tests

Currently, there are no dedicated integration tests for this module beyond the implicit integration of its usage in other modules. The unit tests for `logger_config.py` cover interactions with environment variables and file system (via mocking where appropriate).

### End-to-End (E2E) Tests

Not applicable for this foundational logging utility module in isolation. E2E tests for the overall application would verify that logging output is correctly generated as part of broader functionalities.

## Test Structure

-   `unit/`: Contains unit tests.
    -   `test_logger_config.py`: Tests the functionality of `setup_logging()` and `get_logger()` from `logger_config.py`, including various configurations for log levels, formats (TEXT, JSON), and output destinations (console, file).
-   `integration/`: (Currently no specific integration tests for this module itself).
-   `fixtures/` or `data/`: (Currently not used, but could be added for complex test data if needed).

## Writing Tests

When contributing new tests for `logger_config.py` or other components of this module:

-   **Framework**: Use `pytest`.
-   **Mocking**: Utilize `pytest` fixtures and `unittest.mock` (e.g., `mocker` fixture from `pytest-mock`) to mock:
    -   Environment variables (`os.getenv`).
    -   File system operations (`logging.FileHandler`, `os.path.exists`, etc.) if testing file output aspects without creating actual files, or use `tmp_path` fixture for temporary files.
    -   `logging.basicConfig` and `logging.getLogger().addHandler` calls to inspect their arguments.
-   **Assertions**: Assert on:
    -   The configuration of loggers (level, handlers, formatters).
    -   The content of log messages (if capturing output).
    -   Warnings printed to `stderr` for invalid configurations.
-   **Idempotency**: Ensure `setup_logging()` remains idempotent even if called multiple times in tests (though the `_logging_configured` flag handles this, tests can verify it).
-   **Coverage**: Aim to cover different code paths based on environment variable settings.
-   Refer to existing tests in `test_logger_config.py` for patterns.

## Troubleshooting Failed Tests

-   **Environment Variables**: Ensure that tests properly mock or isolate environment variables to avoid interference from your actual `.env` files or shell environment.
-   **File Paths**: If testing file logging, ensure paths are handled correctly, especially if using temporary files/directories provided by `pytest` (like `tmp_path`).
-   **Mocking Issues**: Double-check that mocks are configured correctly and that the functions/objects you intend to mock are the ones actually being called.
-   **`_logging_configured` state**: Some tests might need to reset the `logging_monitoring.logger_config._logging_configured` flag to `False` if they need to re-run `setup_logging()` under different conditions within the same test session (though `pytest` usually isolates test functions). If issues arise, check this state variable. 