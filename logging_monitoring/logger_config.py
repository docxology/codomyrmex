import logging
import os
import sys
from dotenv import load_dotenv

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# More detailed log format for debug purposes, can be set via env variable
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"

_logging_configured = False

def setup_logging():
    """
    Configures logging for the Codomyrmex project.

    This function should be called once, typically at the application's entry point.
    It reads configuration from environment variables:
    - CODOMYRMEX_LOG_LEVEL: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.
    - CODOMYRMEX_LOG_FILE: Optional path to a log file. If not set, logs to console.
    - CODOMYRMEX_LOG_FORMAT: Optional custom log format string. Defaults to DEFAULT_LOG_FORMAT.
                           Set to "DETAILED" to use DETAILED_LOG_FORMAT.

    Uses `python-dotenv` to load environment variables from a .env file.
    """
    global _logging_configured
    if _logging_configured:
        # logging.getLogger(__name__).debug("Logging already configured. Skipping.")
        return

    load_dotenv()  # Load .env file from current dir or parent dirs

    log_level_str = os.getenv('CODOMYRMEX_LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('CODOMYRMEX_LOG_FILE')
    log_format_str = os.getenv('CODOMYRMEX_LOG_FORMAT', DEFAULT_LOG_FORMAT)

    if log_format_str == "DETAILED":
        log_format_str = DETAILED_LOG_FORMAT
    elif not log_format_str: # Handles empty string case
        log_format_str = DEFAULT_LOG_FORMAT

    # Validate and get the logging level
    log_level = getattr(logging, log_level_str, logging.INFO)
    if not isinstance(log_level, int):
        print(f"Warning: Invalid CODOMYRMEX_LOG_LEVEL '{log_level_str}'. Defaulting to INFO.", file=sys.stderr)
        log_level = logging.INFO

    # Create a root logger or a specific project logger
    # Using basicConfig is simpler if we want a single configuration point.
    # If we configure the root logger, all loggers inherit from it.
    
    handlers = []
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format_str))
    handlers.append(console_handler)

    # File Handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='a') # 'a' for append
            file_handler.setFormatter(logging.Formatter(log_format_str))
            handlers.append(file_handler)
        except IOError as e:
            print(f"Warning: Could not open log file '{log_file}': {e}. Logging to console only.", file=sys.stderr)

    logging.basicConfig(level=log_level, handlers=handlers, force=True)
    
    # If specific libraries are too verbose, their log levels can be adjusted here:
    # logging.getLogger("some_verbose_library").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging configured: Level={log_level_str}, File='{log_file if log_file else 'Console'}', Format='{log_format_str}'"
    )
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger instance with the specified name.

    It's recommended to use `__name__` as the logger name for module-level logging.
    `setup_logging()` should be called before using loggers obtained from this function
    to ensure they are properly configured. If `setup_logging()` has not been called,
    this function will still return a logger, but it might use Python's default
    logging configuration (which logs warnings and above to stderr).

    Args:
        name: The name for the logger. Typically `__name__`.

    Returns:
        A logging.Logger instance.
    """
    global _logging_configured
    if not _logging_configured:
        # This provides a fallback, though it's better to ensure setup_logging() is called.
        # The user might see a "No handlers could be found for logger X" if not configured
        # or it will use default Python logging settings (WARNING to stderr).
        # print("Warning: get_logger called before setup_logging. Logger may not be fully configured.", file=sys.stderr)
        # For robustness, we could call setup_logging() here with defaults,
        # but it's usually better to have explicit setup.
        # For now, we'll rely on the user calling setup_logging().
        pass # Python's default logging will take over if not configured.
        
    return logging.getLogger(name)

# Example of how to use it (primarily for testing this file directly):
if __name__ == '__main__':
    # Simulate setting environment variables for testing
    # In a real application, these would be in a .env file or set in the environment
    os.environ['CODOMYRMEX_LOG_LEVEL'] = 'DEBUG'
    os.environ['CODOMYRMEX_LOG_FILE'] = 'test_module.log'
    os.environ['CODOMYRMEX_LOG_FORMAT'] = 'DETAILED'

    setup_logging()

    logger = get_logger(__name__)
    logger.debug("This is a debug message from logger_config.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    another_module_logger = get_logger("another.module")
    another_module_logger.info("Info message from another module.")

    print(f"Test log output should be in console and in '{os.environ['CODOMYRMEX_LOG_FILE']}'")
    # Clean up the test log file
    # try:
    #     os.remove('test_module.log')
    # except OSError:
    #     pass 