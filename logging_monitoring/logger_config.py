import logging
import os
import sys
from dotenv import load_dotenv
import json
from datetime import datetime

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# More detailed log format for debug purposes, can be set via env variable
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"

_logging_configured = False

# Custom JSON Formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_entry["stack_info"] = self.formatStack(record.stack_info)
        
        # Include extra fields passed to the logger
        # Standard arguments that are already part of 'record' or handled above
        standard_attrs = {'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename', 'levelname', 'levelno', 'message', 'module', 'msecs', 'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName', 'funcName', 'lineno', 'timestamp', 'level'}
        extra = {k: v for k, v in record.__dict__.items() if k not in standard_attrs and not k.startswith('_')}
        if extra:
            log_entry['extra'] = extra
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    """
    Configures logging for the Codomyrmex project.

    This function should be called once, typically at the application's entry point.
    It reads configuration from environment variables:
    - CODOMYRMEX_LOG_LEVEL: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.
    - CODOMYRMEX_LOG_FILE: Optional path to a log file. If not set, logs to console.
    - CODOMYRMEX_LOG_FORMAT: Optional custom log format string for TEXT output.
                           Defaults to DEFAULT_LOG_FORMAT. Set to "DETAILED" to use DETAILED_LOG_FORMAT.
    - CODOMYRMEX_LOG_OUTPUT_TYPE: Output type ("TEXT" or "JSON"). Defaults to "TEXT".

    Uses `python-dotenv` to load environment variables from a .env file.
    """
    global _logging_configured
    if _logging_configured:
        logging.getLogger(__name__).debug("Logging already configured. Skipping.")
        return

    load_dotenv()  # Load .env file from current dir or parent dirs

    log_level_str = os.getenv('CODOMYRMEX_LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('CODOMYRMEX_LOG_FILE')
    log_format_str_text = os.getenv('CODOMYRMEX_LOG_FORMAT', DEFAULT_LOG_FORMAT)
    log_output_type = os.getenv('CODOMYRMEX_LOG_OUTPUT_TYPE', 'TEXT').upper()

    if log_format_str_text == "DETAILED":
        log_format_str_text = DETAILED_LOG_FORMAT
    elif not log_format_str_text: # Handles empty string case for text format
        log_format_str_text = DEFAULT_LOG_FORMAT

    # Validate and get the logging level
    log_level = getattr(logging, log_level_str, logging.INFO)
    if not isinstance(log_level, int):
        print(f"Warning: Invalid CODOMYRMEX_LOG_LEVEL '{log_level_str}'. Defaulting to INFO.", file=sys.stderr)
        log_level = logging.INFO
    
    # Determine the formatter
    if log_output_type == 'JSON':
        formatter = JsonFormatter()
        actual_log_format_for_display = "JSON"
    elif log_output_type == 'TEXT':
        formatter = logging.Formatter(log_format_str_text)
        actual_log_format_for_display = log_format_str_text
    else:
        print(f"Warning: Invalid CODOMYRMEX_LOG_OUTPUT_TYPE '{log_output_type}'. Defaulting to TEXT.", file=sys.stderr)
        formatter = logging.Formatter(log_format_str_text) # Default to text
        log_output_type = 'TEXT' # Correct the type for display
        actual_log_format_for_display = log_format_str_text

    handlers = []
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File Handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='a') # 'a' for append
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except IOError as e:
            print(f"Warning: Could not open log file '{log_file}': {e}. Logging to console only.", file=sys.stderr)

    logging.basicConfig(level=log_level, handlers=handlers, force=True)
    
    # If specific libraries are too verbose, their log levels can be adjusted here:
    # logging.getLogger("some_verbose_library").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging configured: Level={log_level_str}, OutputType={log_output_type}, File='{log_file if log_file else 'Console'}', Format='{actual_log_format_for_display}'"
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
    
    # Test Case 1: Default Text Logging
    print("\n--- Test Case 1: Default Text Logging ---")
    os.environ['CODOMYRMEX_LOG_LEVEL'] = 'DEBUG'
    os.environ['CODOMYRMEX_LOG_FILE'] = 'test_module_text.log'
    os.environ['CODOMYRMEX_LOG_FORMAT'] = 'DETAILED'
    os.environ['CODOMYRMEX_LOG_OUTPUT_TYPE'] = 'TEXT'
    _logging_configured = False # Reset for test
    setup_logging()
    logger_text = get_logger(__name__ + "_text")
    logger_text.debug("This is a debug message from logger_config (text).", extra={"custom_field": "value1"})
    logger_text.info("This is an info message (text).")
    try:
        1/0
    except ZeroDivisionError:
        logger_text.error("This is an error message with exception (text).", exc_info=True)
    print(f"Text log output should be in console and in '{os.environ['CODOMYRMEX_LOG_FILE']}'")

    # Test Case 2: JSON Logging
    print("\n--- Test Case 2: JSON Logging ---")
    os.environ['CODOMYRMEX_LOG_LEVEL'] = 'INFO'
    os.environ['CODOMYRMEX_LOG_FILE'] = 'test_module_json.log'
    # CODOMYRMEX_LOG_FORMAT is ignored for JSON output type
    os.environ['CODOMYRMEX_LOG_OUTPUT_TYPE'] = 'JSON'
    _logging_configured = False # Reset for test
    setup_logging()
    logger_json = get_logger(__name__ + "_json")
    logger_json.debug("This debug message should NOT appear due to INFO level (json).") # Won't be logged
    logger_json.info("This is an info message (json).", extra={"key1": "value1", "key2": 123})
    logger_json.warning("This is a warning message (json).")
    try:
        x = {}
        print(x['missing_key'])
    except KeyError:
        logger_json.error("This is an error message with exception (json).", exc_info=True, extra={"user_id": "test_user"})
    
    another_logger_json = get_logger("another.module_json")
    another_logger_json.info("Info from another module (json).", extra={"transaction_id": "xyz789"})

    print(f"JSON log output should be in console and in '{os.environ['CODOMYRMEX_LOG_FILE']}'")

    # Clean up the test log files
    # try:
    #     if os.path.exists('test_module_text.log'): os.remove('test_module_text.log')
    #     if os.path.exists('test_module_json.log'): os.remove('test_module_json.log')
    # except OSError:
    #     pass 