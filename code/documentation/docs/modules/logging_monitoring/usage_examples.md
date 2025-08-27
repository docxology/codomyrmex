---
sidebar_label: 'Usage Examples'
title: 'Logging & Monitoring - Usage Examples'
---

# Logging & Monitoring - Usage Examples

This document provides usage examples for the Logging & Monitoring module.

## Example 1: Basic Setup and Logging

This example demonstrates how to initialize the logging system in a main application script and use a logger in another module.

**1. Configure `.env` file (in project root):**

```env
# .env (Project Root)
CODOMYRMEX_LOG_LEVEL=DEBUG
CODOMYRMEX_LOG_FILE=logs/app_debug.log  # Ensure 'logs' directory exists or app has permission to create it
CODOMYRMEX_LOG_FORMAT="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
```
*Note: The logger itself doesn't create the `logs/` directory. It must exist, or the application needs rights to create it if the path includes a new directory.* 

**2. Main application script (e.g., `main_app.py` in project root):**

```python
# main_app.py
from codomyrmex.logging_monitoring import setup_logging, get_logger
# Assuming a module named 'worker_module.py' exists in your project
# For example, in the same directory or an accessible package:
# import worker_module

# Conceptual worker_module for the example
class WorkerModule:
    def __init__(self):
        self.logger = get_logger(__name__ + ".WorkerModule") # Using a more specific logger name

    def do_something(self):
        self.logger.info("do_something() called in WorkerModule.")
        try:
            x = 1 / 0
        except ZeroDivisionError:
            self.logger.error("Attempted to divide by zero!", exc_info=True) # exc_info=True logs stack trace
        self.logger.debug("Finished attempt in do_something().")

worker_module_instance = WorkerModule()

def run_application():
    # Initialize logging ONCE at the start of your application
    setup_logging()

    # Get a logger for the main script itself (optional)
    logger = get_logger(__name__) # __name__ will be '__main__' if script is run directly
    logger.info("Application starting...")
    logger.debug("This is a debug message from the main application.")

    # Call functions from other modules/instances that use logging
    worker_module_instance.do_something()

    logger.info("Application finished.")

if __name__ == "__main__":
    run_application()
```

### Expected Outcome

- **Console Output**: You will see log messages (DEBUG level and above) printed to the console, formatted as specified.
- **File Output**: A file named `app_debug.log` will be created (or appended to) inside a `logs` directory (relative to where `main_app.py` is run, assuming `logs/` exists). It will contain the same log messages.
- Log messages from `main_app.py` will typically have `__main__` as the logger name.
- Log messages from the `WorkerModule` instance will have `__main__.WorkerModule` (if `main_app.py` is run directly) or `your_package.main_app.WorkerModule` as the logger name, helping trace origins.

## Example 2: Using Detailed Log Format and Different Log Level

This example shows how to use the "DETAILED" log format and set a higher log level (e.g., WARNING) to reduce verbosity.

**1. Configure `.env` file (in project root):**

```env
# .env (Project Root)
CODOMYRMEX_LOG_LEVEL=WARNING
CODOMYRMEX_LOG_FORMAT=DETAILED
# CODOMYRMEX_LOG_FILE is omitted, so logs will only go to console
```

**2. Using the same Python script (`main_app.py` with `WorkerModule`) as in Example 1.**

### Expected Outcome

- **Console Output**:
    - Only WARNING and ERROR level messages will be displayed.
    - The format will be more detailed: `%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s`.
    - You would NOT see the "Application starting..." (INFO) or debug messages.
    - You WOULD see the "Attempted to divide by zero!" (ERROR) message from `WorkerModule`.
- **File Output**: No log file will be created as `CODOMYRMEX_LOG_FILE` is not set.

## Common Pitfalls & Troubleshooting

- **Issue**: No logs are appearing, or logs are not at the expected level.
  - **Solution**:
    1. Ensure `setup_logging()` is called once at the very beginning of your application.
    2. Verify the `CODOMYRMEX_LOG_LEVEL` in your `.env` file is set correctly (e.g., `DEBUG`, `INFO`). It is case-sensitive.
    3. Check that the `.env` file is in the project root and is being loaded (e.g., no typos in environment variable names, `python-dotenv` is installed and working).

- **Issue**: "No handlers could be found for logger X" message.
  - **Solution**: This usually means `setup_logging()` was not called before `get_logger()` was used for that specific logger instance, or the setup failed silently. Ensure `setup_logging()` is the first relevant call in your application's lifecycle.

- **Issue**: Log file is not being created or written to.
  - **Solution**:
    1. Check if `CODOMYRMEX_LOG_FILE` is correctly set in your `.env` file.
    2. Ensure the application has write permissions for the specified file path and that the directory path (e.g., `logs/`) exists. The logger typically does not create directories.
    3. Look for any warning messages printed to the console by `setup_logging()` regarding file access issues.

- **Issue**: Logs from third-party libraries are too verbose or are missing.
  - **Solution**:
    - The current `setup_logging()` configures the root logger. If third-party libraries use standard Python logging, their messages should be captured according to the root log level.
    - To silence a specific verbose library: `logging.getLogger("some_verbose_library").setLevel(logging.WARNING)` *after* your `setup_logging()` call.
    - To make a quiet library louder: `logging.getLogger("some_quiet_library").setLevel(logging.DEBUG)` *after* `setup_logging()`. Ensure your root logger level (set by `CODOMYRMEX_LOG_LEVEL`) is also at least `DEBUG`. 