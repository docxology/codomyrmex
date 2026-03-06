"""
Integration and zero-mock unit tests for JSON-structured logging infrastructure.

Covers:
- JSON formatting (timestamps, levels, extra fields, correlation IDs)
- Log level filtering (logger level vs handler level)
- File rotation (LogRotationManager)
- Structured field injection
"""

import json
import logging
import shutil
import tempfile
from pathlib import Path

import pytest

from codomyrmex.logging_monitoring.core.correlation import (
    CorrelationFilter,
    with_correlation,
)
from codomyrmex.logging_monitoring.formatters.json_formatter import JSONFormatter
from codomyrmex.logging_monitoring.handlers.rotation import LogRotationManager


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)

@pytest.mark.unit
class TestJSONLoggingIntegration:
    """Tests for JSON logging infrastructure."""

    def test_json_formatter_fields(self):
        """Verify that JSONFormatter includes all expected fields."""
        formatter = JSONFormatter()
        logger = logging.getLogger("test_fields")
        logger.setLevel(logging.INFO)

        # Capture output using a custom handler
        class CapturingHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []
            def emit(self, record):
                self.records.append(self.format(record))

        handler = CapturingHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        try:
            with with_correlation("test-correlation-123"):
                logger.addFilter(CorrelationFilter())
                logger.info("Test message", extra={"custom_field": "custom_value"})

            assert len(handler.records) == 1
            log_entry = json.loads(handler.records[0])

            assert "timestamp" in log_entry
            assert log_entry["level"] == "INFO"
            assert log_entry["message"] == "Test message"
            assert log_entry["custom_field"] == "custom_value"
            assert log_entry["correlation_id"] == "test-correlation-123"
            assert "module" in log_entry
            assert "function" in log_entry
            assert "line" in log_entry
        finally:
            logger.removeHandler(handler)

    def test_log_level_filtering(self):
        """Verify that log level filtering works at both logger and handler levels."""
        logger = logging.getLogger("test_filtering")
        logger.setLevel(logging.INFO)

        class CapturingHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []
            def emit(self, record):
                self.records.append(record)

        handler = CapturingHandler()
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)

        try:
            logger.debug("Debug message")    # Filtered by logger level
            logger.info("Info message")      # Filtered by handler level
            logger.warning("Warning message") # Should pass
            logger.error("Error message")     # Should pass

            assert len(handler.records) == 2
            assert handler.records[0].levelname == "WARNING"
            assert handler.records[1].levelname == "ERROR"
        finally:
            logger.removeHandler(handler)

    def test_file_rotation(self, temp_log_dir):
        """Verify that LogRotationManager correctly rotates log files."""
        manager = LogRotationManager(temp_log_dir)
        logger_name = "test_rotation"
        filename = "rotation.log"

        # Max size 100 bytes, keep 2 backups
        handler = manager.attach_rotating_handler(
            logger_name,
            filename,
            max_bytes=100,
            backup_count=2,
            formatter=JSONFormatter()
        )

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        try:
            # Send enough logs to trigger rotation
            # Each JSON log entry will be > 100 bytes
            for i in range(10):
                logger.info(f"Log message {i} with some extra padding to ensure rotation occurs quickly")

            log_path = Path(temp_log_dir)
            files = list(log_path.glob("rotation.log*"))

            # Should have rotation.log, rotation.log.1, rotation.log.2
            assert len(files) == 3

            # Verify they are all JSON
            for f in files:
                with open(f) as log_file:
                    for line in log_file:
                        if line.strip():
                            json.loads(line)
        finally:
            manager.remove_handler(logger_name, filename)

    def test_structured_field_injection(self):
        """Verify that extra fields and context are correctly injected into JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test msg",
            args=(),
            exc_info=None
        )
        # Manually add context and other fields as it would happen in setup_logging or with extra
        record.context = {"user_id": 42}
        record.task_id = "abc-123"

        result = formatter.format(record)
        log_entry = json.loads(result)

        assert log_entry["context"] == {"user_id": 42}
        assert log_entry["task_id"] == "abc-123"

    def test_redaction_integration(self):
        """Verify that RedactedJSONFormatter works with the improved JSONFormatter base."""
        from codomyrmex.logging_monitoring.formatters.json_formatter import (
            RedactedJSONFormatter,
        )

        formatter = RedactedJSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test msg",
            args=(),
            exc_info=None
        )
        record.password = "secret123"
        record.safe_field = "safe_value"

        result = formatter.format(record)
        log_entry = json.loads(result)

        assert log_entry["password"] == "[REDACTED]"
        assert log_entry["safe_field"] == "safe_value"
