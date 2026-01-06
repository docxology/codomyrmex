# Logging Monitoring - Usage Examples

This document provides usage examples for the Logging Monitoring module.

## Example 1: Basic Setup and Logging

This example demonstrates how to initialize the logging system in a main application script and use a logger in another module.

**1. Configure `.env` file (in project root):**

```env
# .env
CODOMYRMEX_LOG_LEVEL=DEBUG
CODOMYRMEX_LOG_FILE=app_debug.log
CODOMYRMEX_LOG_FORMAT="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
CODOMYRMEX_LOG_OUTPUT_TYPE=TEXT
```

**2. Main application script (e.g., `main.py` in project root):**

```python
from codomyrmex.logging_monitoring import setup_logging, get_logger
import my_module # Assuming my_module.py exists

def run_app():
    # Initialize logging ONCE at the start of your application
    setup_logging()

    # Get a logger for the main script itself (optional)
    logger = get_logger(__name__) # __name__ will be '__main__' here
    logger.info("Application starting...")
    logger.debug("This is a debug message from the main application.")

    # Call functions from other modules that use logging
    my_module.do_something()

    logger.info("Application finished.")

if __name__ == "__main__":
    run_app()
```

**3. Another module (e.g., `my_module.py`):**

```python
from codomyrmex.logging_monitoring import get_logger

# Get a logger specific to this module
# Using __name__ (which will be 'my_module') is a best practice
logger = get_logger(__name__)

def do_something():
    logger.info("do_something() called in my_module.")
    # Simulate some work
    try:
        x = 1 / 0
    except ZeroDivisionError:
        logger.error("Attempted to divide by zero!", exc_info=True) # exc_info=True logs stack trace
    logger.debug("Finished attempt in do_something().")
```

### Expected Outcome

- **Console Output**: You will see log messages (DEBUG level and above) printed to the console, formatted as specified in `CODOMYRMEX_LOG_FORMAT`.
- **File Output**: A file named `app_debug.log` will be created (or appended to) in the same directory as `main.py` (or wherever the relative path resolves from the CWD). It will contain the same log messages.
- Log messages from `main.py` will have `__main__` as the logger name.
- Log messages from `my_module.py` will have `my_module` as the logger name.

## Example 2: Using Detailed Log Format and Different Log Level

This example shows how to use the "DETAILED" log format and set a higher log level (e.g., WARNING) to reduce verbosity.

**1. Configure `.env` file (in project root):**

```env
# .env
CODOMYRMEX_LOG_LEVEL=WARNING
CODOMYRMEX_LOG_FORMAT=DETAILED
CODOMYRMEX_LOG_OUTPUT_TYPE=TEXT
```

**2. Using the same Python scripts as in Example 1.**

### Expected Outcome

- **Console Output**: 
    - Only WARNING and ERROR level messages will be displayed.
    - The format will be more detailed: `%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s`.
    - You would *not* see the "Application starting..." (INFO) and debug messages because the level is WARNING.
    - You *would* see the "Attempted to divide by zero!" (ERROR) message from `my_module`.
- **File Output**: No log file will be created as `CODOMYRMEX_LOG_FILE` is not set.

## Example 3: JSON Log Output

This example demonstrates how to configure the logging system to output logs in JSON format.

**1. Configure `.env` file (in project root):**

```env
# .env
CODOMYRMEX_LOG_LEVEL=INFO
CODOMYRMEX_LOG_FILE=app_json.log
CODOMYRMEX_LOG_OUTPUT_TYPE=JSON
# CODOMYRMEX_LOG_FORMAT is ignored when CODOMYRMEX_LOG_OUTPUT_TYPE is JSON
```

**2. Using the same Python scripts as in Example 1 (`main.py` and `my_module.py`).**

### Expected Outcome

- **Console Output**: Log messages (INFO level and above) will be printed to the console, formatted as JSON objects, one per line.
- **File Output**: A file named `app_json.log` will be created (or appended to). It will contain the same JSON log messages.
- Each JSON log entry will contain fields like `timestamp`, `level`, `name`, `module`, `funcName`, `lineno`, and `message`.
- If `extra` data is passed to a log call (e.g., `logger.info("message", extra={"custom_key": "custom_value"})`), it will appear under an `"extra"` field in the JSON.

**Example JSON Log Entry (content will vary):**
```json
{"timestamp":"2023-10-27T12:34:56.789012Z","level":"INFO","name":"my_module","module":"my_module","funcName":"do_something","lineno":10,"message":"do_something() called in my_module."}
{"timestamp":"2023-10-27T12:34:56.790000Z","level":"ERROR","name":"my_module","module":"my_module","funcName":"do_something","lineno":15,"message":"Attempted to divide by zero!","exception":"Traceback (most recent call last):\
  File \\"my_module.py\\\", line 13, in do_something\
    x = 1 / 0\
ZeroDivisionError: division by zero"}
```

## Common Pitfalls & Troubleshooting

- **Issue**: No logs are appearing, or logs are not at the expected level.
  - **Solution**: 
    1. Ensure `setup_logging()` is called once at the very beginning of your application.
    2. Verify the `CODOMYRMEX_LOG_LEVEL` in your `.env` file is set correctly (e.g., `DEBUG`, `INFO`).
    3. Check that the `.env` file is in the project root and is being loaded (e.g., no typos in environment variable names).
    4. Ensure `python-dotenv` is installed.

- **Issue**: "No handlers could be found for logger X" message.
  - **Solution**: This usually means `setup_logging()` was not called before `get_logger()` was used, or the setup failed silently. Ensure `setup_logging()` is called first and check for any warning messages during its execution (e.g., problems opening a log file).

- **Issue**: Log file is not being created or written to.
  - **Solution**:
    1. Check if `CODOMYRMEX_LOG_FILE` is correctly set in your `.env` file.
    2. Ensure the application has write permissions for the specified file path and that the directory path exists. The logger does not create directories.
    3. Look for any warning messages printed to the console by `setup_logging()` regarding file access issues.

- **Issue**: Logs from third-party libraries are too verbose or are missing.
  - **Solution**: 
    - The current `setup_logging()` configures the root logger. If third-party libraries use standard Python logging, their messages should be captured.
    - To silence a specific verbose library: `logging.getLogger("some_verbose_library").setLevel(logging.WARNING)` *after* your `setup_logging()` call.
    - To make a quiet library louder (if it logs to a specific logger and its level is higher than your root logger): `logging.getLogger("some_quiet_library").setLevel(logging.DEBUG)` *after* `setup_logging()`. You also need to ensure your root logger level (set by `CODOMYRMEX_LOG_LEVEL`) is also at least DEBUG. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
