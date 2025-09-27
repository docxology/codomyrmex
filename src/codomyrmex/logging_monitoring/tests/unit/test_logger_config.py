import pytest
import logging
import os
import json
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

# Make sure the module can be imported
# This assumes tests are run from the project root or PYTHONPATH is set up.
from codomyrmex.logging_monitoring import (
    logger_config,
)  # Direct import for _logging_configured
from codomyrmex.logging_monitoring import setup_logging, get_logger


# Helper to reset logging configuration for isolated tests
def reset_logging_state():
    logger_config._logging_configured = False
    # Remove all handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # Reset a specific logger if it was cached
    if "__main___test" in logging.Logger.manager.loggerDict:
        del logging.Logger.manager.loggerDict["__main___test"]


@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    reset_logging_state()
    yield
    reset_logging_state()


@pytest.fixture
def mock_env(mocker):
    """Fixture to mock environment variables."""
    return mocker.patch.dict(os.environ, {}, clear=True)


@pytest.fixture
def captured_stdout():
    """Fixture to capture stdout."""
    new_out = StringIO()
    old_out = sys.stdout
    try:
        sys.stdout = new_out
        yield new_out
    finally:
        sys.stdout = old_out


@pytest.fixture
def captured_stderr():
    """Fixture to capture stderr."""
    new_err = StringIO()
    old_err = sys.stderr
    try:
        sys.stderr = new_err
        yield new_err
    finally:
        sys.stderr = old_err


def test_setup_logging_defaults(mock_env, captured_stdout, captured_stderr):
    """Test setup_logging with default settings (INFO, TEXT, Console)."""
    setup_logging()
    log_output = captured_stdout.getvalue()
    err_output = captured_stderr.getvalue()

    assert (
        "Logging configured: Level=INFO, OutputType=TEXT, File='Console'" in log_output
    )
    assert not err_output  # No warnings expected

    logger = get_logger("__main___test")
    assert logger.level == logging.INFO  # Effective level after setup
    assert any(
        isinstance(h, logging.StreamHandler) for h in logging.getLogger().handlers
    )

    # Check formatter
    handler = next(
        h for h in logging.getLogger().handlers if isinstance(h, logging.StreamHandler)
    )
    assert isinstance(handler.formatter, logging.Formatter)
    # Can't easily check the exact format string of the default formatter, but we know it's not JSON

    # Test a log message
    logger.info("Default test message")
    log_output_after_msg = captured_stdout.getvalue()
    assert "Default test message" in log_output_after_msg
    assert "INFO" in log_output_after_msg


def test_setup_logging_debug_detailed_text(mock_env, captured_stdout):
    """Test DEBUG level and DETAILED text format."""
    mock_env["CODOMYRMEX_LOG_LEVEL"] = "DEBUG"
    mock_env["CODOMYRMEX_LOG_FORMAT"] = "DETAILED"

    setup_logging()
    log_output = captured_stdout.getvalue()
    assert (
        "Logging configured: Level=DEBUG, OutputType=TEXT, File='Console', Format='%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'"
        in log_output
    )

    logger = get_logger("__main___test")
    logger.debug("Detailed debug message")
    log_output_after_msg = captured_stdout.getvalue()
    assert "Detailed debug message" in log_output_after_msg
    assert "DEBUG" in log_output_after_msg
    assert "test_logger_config" in log_output_after_msg  # module name


def test_setup_logging_json_output(mock_env, captured_stdout):
    """Test JSON output format."""
    mock_env["CODOMYRMEX_LOG_LEVEL"] = "INFO"
    mock_env["CODOMYRMEX_LOG_OUTPUT_TYPE"] = "JSON"

    setup_logging()
    log_output_config = captured_stdout.getvalue()  # Capture config message
    assert (
        "Logging configured: Level=INFO, OutputType=JSON, File='Console', Format='JSON'"
        in log_output_config
    )

    logger = get_logger("__main___test_json")
    logger.info("JSON test message", extra={"key": "value"})

    # Clear stdout buffer for next capture or re-read
    captured_stdout.seek(0)
    captured_stdout.truncate()  # Clear existing content after config log

    # Relog and capture
    logger.info("JSON test message", extra={"key": "value"})
    log_output_msg_lines = captured_stdout.getvalue().strip().split("\\n")

    found_log = False
    for line in log_output_msg_lines:
        if not line:
            continue
        try:
            log_entry = json.loads(line)
            if log_entry["message"] == "JSON test message":
                assert log_entry["level"] == "INFO"
                assert log_entry["name"] == "__main___test_json"
                assert log_entry["extra"]["key"] == "value"
                found_log = True
                break
        except json.JSONDecodeError:
            pytest.fail(f"Failed to parse JSON log line: {line}")
    assert found_log, "JSON log message not found or incorrect"


def test_setup_logging_file_output(mock_env, tmp_path, captured_stdout):
    """Test logging to a file."""
    log_file = tmp_path / "test.log"
    mock_env["CODOMYRMEX_LOG_FILE"] = str(log_file)
    mock_env["CODOMYRMEX_LOG_LEVEL"] = "WARNING"

    setup_logging()
    config_log = captured_stdout.getvalue()
    assert f"File='{str(log_file)}'" in config_log

    logger = get_logger("__main___test_file")
    logger.warning("Message to file")

    assert log_file.exists()
    file_content = log_file.read_text()
    assert "Message to file" in file_content
    assert "WARNING" in file_content


def test_setup_logging_invalid_level(mock_env, captured_stderr):
    """Test fallback for invalid log level."""
    mock_env["CODOMYRMEX_LOG_LEVEL"] = "INVALID_LEVEL"
    setup_logging()
    err_output = captured_stderr.getvalue()
    assert (
        "Warning: Invalid CODOMYRMEX_LOG_LEVEL 'INVALID_LEVEL'. Defaulting to INFO."
        in err_output
    )

    logger = get_logger("__main___test")
    # Check that the effective level is INFO
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO


def test_setup_logging_invalid_output_type(mock_env, captured_stderr, captured_stdout):
    """Test fallback for invalid log output type."""
    mock_env["CODOMYRMEX_LOG_OUTPUT_TYPE"] = "INVALID_TYPE"
    setup_logging()
    err_output = captured_stderr.getvalue()
    log_output = captured_stdout.getvalue()

    assert (
        "Warning: Invalid CODOMYRMEX_LOG_OUTPUT_TYPE 'INVALID_TYPE'. Defaulting to TEXT."
        in err_output
    )
    assert (
        "OutputType=TEXT" in log_output
    )  # Check that it defaulted to TEXT in the config message

    handler = next(
        h for h in logging.getLogger().handlers if isinstance(h, logging.StreamHandler)
    )
    assert isinstance(
        handler.formatter, logging.Formatter
    )  # Should be standard text formatter
    assert not isinstance(handler.formatter, logger_config.JsonFormatter)


def test_logging_idempotency(mock_env, captured_stdout):
    """Test that setup_logging is idempotent."""
    setup_logging()  # First call
    first_call_log = captured_stdout.getvalue()

    # Clear stdout buffer
    captured_stdout.seek(0)
    captured_stdout.truncate()

    setup_logging()  # Second call
    second_call_log = captured_stdout.getvalue()

    assert "Logging configured" in first_call_log
    assert "Logging already configured. Skipping." in second_call_log


def test_get_logger_returns_logger_instance(mock_env):
    """Test that get_logger returns a Logger instance."""
    setup_logging()  # Ensure it's configured
    logger_name = "my_test_logger"
    logger = get_logger(logger_name)
    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name


def test_get_logger_before_setup(captured_stderr):
    """Test get_logger behavior before setup_logging (relies on Python's default)."""
    # Note: logger_config.py has a commented-out warning for this.
    # Python's default is to log WARNING and above to stderr.
    # It also creates a default handler if no handlers are configured for the root logger
    # when the first log message is emitted.

    logger = get_logger("unconfigured_logger")
    assert isinstance(logger, logging.Logger)

    # Check that no handlers were added by our setup_logging
    root_logger = logging.getLogger()
    assert not any(
        isinstance(h, (logging.StreamHandler, logging.FileHandler))
        and isinstance(h.formatter, (logging.Formatter, logger_config.JsonFormatter))
        for h in root_logger.handlers
    )


def test_json_formatter_with_exception(mock_env, captured_stdout):
    mock_env["CODOMYRMEX_LOG_OUTPUT_TYPE"] = "JSON"
    setup_logging()

    logger = get_logger("json_exception_logger")

    captured_stdout.seek(0)
    captured_stdout.truncate()  # Clear config log

    try:
        1 / 0
    except ZeroDivisionError:
        logger.error("Division error occurred", exc_info=True)

    log_output_lines = captured_stdout.getvalue().strip().split("\\n")
    found_log = False
    for line in log_output_lines:
        if not line:
            continue
        log_entry = json.loads(line)
        if log_entry["message"] == "Division error occurred":
            assert log_entry["level"] == "ERROR"
            assert "exception" in log_entry
            assert "ZeroDivisionError" in log_entry["exception"]
            found_log = True
            break
    assert found_log


def test_json_formatter_with_extra_fields(mock_env, captured_stdout):
    mock_env["CODOMYRMEX_LOG_OUTPUT_TYPE"] = "JSON"
    setup_logging()

    logger = get_logger("json_extra_logger")

    captured_stdout.seek(0)
    captured_stdout.truncate()  # Clear config log

    extra_data = {"user_id": 123, "transaction_id": "abc"}
    logger.info("Info with extra fields", extra=extra_data)

    log_output_lines = captured_stdout.getvalue().strip().split("\\n")
    found_log = False
    for line in log_output_lines:
        if not line:
            continue
        log_entry = json.loads(line)
        if log_entry["message"] == "Info with extra fields":
            assert log_entry["level"] == "INFO"
            assert "extra" in log_entry
            assert log_entry["extra"]["user_id"] == 123
            assert log_entry["extra"]["transaction_id"] == "abc"
            found_log = True
            break
    assert found_log


@patch("codomyrmex.logging_monitoring.logger_config.logging.FileHandler")
def test_file_handler_io_error(
    mock_file_handler, mock_env, captured_stderr, captured_stdout
):
    """Test that an IOError when setting up FileHandler is caught and warned."""
    mock_file_handler.side_effect = IOError("Permission denied")
    log_file_path = "dummy/path/test.log"
    mock_env["CODOMYRMEX_LOG_FILE"] = log_file_path

    setup_logging()

    err_output = captured_stderr.getvalue()
    log_output = captured_stdout.getvalue()  # Config log

    assert (
        f"Warning: Could not open log file '{log_file_path}': Permission denied. Logging to console only."
        in err_output
    )
    assert (
        f"File='Console'" in log_output
    )  # Check that it correctly states console only in config

    # Ensure only console handler is present
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)
    assert root_logger.handlers[0].stream == sys.stdout
