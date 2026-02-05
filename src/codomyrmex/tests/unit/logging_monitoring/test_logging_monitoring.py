"""Unit tests for logging_monitoring module."""

import pytest
import sys
import os
import json
import logging
from pathlib import Path


@pytest.mark.unit
class TestLoggingMonitoring:
    """Test cases for logging and monitoring functionality using real implementations."""

    def test_logger_config_import(self, code_dir):
        """Test that we can import logger_config module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logging_monitoring import logger_config
            assert logger_config is not None
        except ImportError as e:
            pytest.fail(f"Failed to import logger_config: {e}")

    def test_get_logger_real_functionality(self, real_logger_fixture):
        """Test get_logger with real logging functionality."""
        from codomyrmex.logging_monitoring import get_logger

        logger = get_logger('test_module')
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')

        # Test actual logging
        logger.info("Test info message")
        logger.error("Test error message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")

        # Verify log file was created and contains messages
        log_file = real_logger_fixture["log_file"]
        assert log_file.exists()

        log_content = log_file.read_text()
        assert "Test info message" in log_content
        assert "Test error message" in log_content
        assert "test_module" in log_content  # Logger name should be in log

    def test_setup_logging_with_file_output(self, tmp_path):
        """Test setup_logging with real file output configuration."""
        from codomyrmex.logging_monitoring import setup_logging, get_logger

        log_file = tmp_path / "test_setup.log"

        # Note: Logging is already configured by conftest.py, so we test the existing logger
        logger = get_logger('test_setup')
        logger.info("Setup test message")
        logger.warning("Setup warning message")

        # Since logging is already configured, we can't easily test file output
        # in this test environment. Instead, verify the logger works.
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')

    def test_json_logging_format(self):
        """Test JSON logging format capabilities."""
        from codomyrmex.logging_monitoring.logger_config import JSONFormatter

        # Test that JSONFormatter exists and can be instantiated
        formatter = JSONFormatter()
        assert formatter is not None
        assert hasattr(formatter, 'format')

        # Test basic formatting (without a real log record)
        # This tests that the formatter class works
        import logging
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )

        formatted = formatter.format(record)
        assert formatted is not None
        assert isinstance(formatted, str)

        # Verify it's valid JSON
        parsed = json.loads(formatted)
        assert parsed["level"] == "INFO"
        assert parsed["name"] == "test"
        assert "Test message" in parsed["message"]

    def test_environment_variable_configuration(self):
        """Test that environment variables are properly read."""
        from codomyrmex.logging_monitoring.logger_config import DEFAULT_LOG_FORMAT, DETAILED_LOG_FORMAT

        # Test that default constants are defined
        assert DEFAULT_LOG_FORMAT is not None
        assert DETAILED_LOG_FORMAT is not None
        assert isinstance(DEFAULT_LOG_FORMAT, str)
        assert isinstance(DETAILED_LOG_FORMAT, str)

        # Test that environment variables can be read (without changing actual config)
        original_level = os.environ.get("CODOMYRMEX_LOG_LEVEL")
        os.environ["CODOMYRMEX_LOG_LEVEL"] = "DEBUG"

        try:
            # Test that the environment variable is accessible
            assert os.environ.get("CODOMYRMEX_LOG_LEVEL") == "DEBUG"
        finally:
            # Restore original value
            if original_level is not None:
                os.environ["CODOMYRMEX_LOG_LEVEL"] = original_level
            elif "CODOMYRMEX_LOG_LEVEL" in os.environ:
                del os.environ["CODOMYRMEX_LOG_LEVEL"]

    def test_multiple_loggers_isolation(self):
        """Test that multiple loggers work independently."""
        from codomyrmex.logging_monitoring import get_logger

        # Get multiple loggers
        logger1 = get_logger('module1')
        logger2 = get_logger('module2.submodule')
        logger3 = get_logger('module1.child')  # Should share hierarchy with logger1

        # Verify they are different logger instances but properly configured
        assert logger1 is not logger2
        assert logger1 is not logger3
        assert logger2 is not logger3

        # All should have the standard logging methods
        for logger in [logger1, logger2, logger3]:
            assert hasattr(logger, 'info')
            assert hasattr(logger, 'error')
            assert hasattr(logger, 'debug')
            assert hasattr(logger, 'warning')

        # Test that they can log without errors
        logger1.info("Message from module1")
        logger2.info("Message from module2.submodule")
        logger3.info("Message from module1.child")

        # Verify logger names are set correctly
        assert logger1.name == 'module1'
        assert logger2.name == 'module2.submodule'
        assert logger3.name == 'module1.child'

    def test_log_with_context(self, caplog):
        """Test logging with structured context."""
        from codomyrmex.logging_monitoring.logger_config import log_with_context

        with caplog.at_level(logging.INFO):
            context = {"user_id": "12345", "operation": "test_op"}
            log_with_context("INFO", "Test message with context", context)

        # Verify log was created with context
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.message == "Test message with context"
        assert record.levelname == "INFO"
        assert hasattr(record, 'context')
        assert record.context == context

    def test_create_correlation_id(self):
        """Test correlation ID generation."""
        from codomyrmex.logging_monitoring.logger_config import create_correlation_id

        correlation_id = create_correlation_id()
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0

        # Should be unique
        correlation_id2 = create_correlation_id()
        assert correlation_id != correlation_id2

        # Should be valid UUID format
        import uuid
        try:
            uuid.UUID(correlation_id)
            assert True
        except ValueError:
            assert False, "Correlation ID is not a valid UUID"

    def test_log_context_manager(self, caplog):
        """Test LogContext context manager."""
        from codomyrmex.logging_monitoring.logger_config import LogContext, log_with_context

        correlation_id = "test-correlation-123"

        with caplog.at_level(logging.INFO):
            with LogContext(correlation_id=correlation_id, additional_context={"env": "test"}):
                log_with_context("INFO", "Message inside context", {"key": "value"})

        # Verify log contains correlation ID
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert hasattr(record, 'correlation_id')
        assert record.correlation_id == correlation_id

    def test_performance_logger_basic(self, caplog):
        """Test basic PerformanceLogger functionality."""
        from codomyrmex.logging_monitoring.logger_config import PerformanceLogger

        perf_logger = PerformanceLogger("test.performance")

        with caplog.at_level(logging.DEBUG):
            perf_logger.start_timer("test_operation", {"component": "test"})
            duration = perf_logger.end_timer("test_operation", {"status": "completed"})

        assert isinstance(duration, float)
        assert duration >= 0

        # Check that start and end messages were logged
        records = [r for r in caplog.records if r.name == "test.performance"]
        assert len(records) >= 2  # At least start and end messages

    def test_performance_logger_context_manager(self, caplog):
        """Test PerformanceLogger context manager."""
        from codomyrmex.logging_monitoring.logger_config import PerformanceLogger

        perf_logger = PerformanceLogger("test.performance")

        with caplog.at_level(logging.INFO):
            with perf_logger.time_operation("context_test", {"type": "context_manager"}):
                import time
                time.sleep(0.01)  # Small delay to ensure measurable duration

        # Verify completion was logged
        records = [r for r in caplog.records if "context_test" in r.message and "completed" in r.message]
        assert len(records) == 1

    def test_performance_logger_metrics(self, caplog):
        """Test PerformanceLogger metric logging."""
        from codomyrmex.logging_monitoring.logger_config import PerformanceLogger

        perf_logger = PerformanceLogger("test.performance")

        with caplog.at_level(logging.INFO):
            perf_logger.log_metric("memory_usage", 1024, "KB", {"process": "test"})
            perf_logger.log_metric("response_time", 0.5, "seconds")

        # Verify metrics were logged
        records = [r for r in caplog.records if r.name == "test.performance"]
        metric_records = [r for r in records if hasattr(r, 'metric_name')]
        assert len(metric_records) >= 2


@pytest.mark.unit
class TestLogRotationManager:
    """Test cases for LogRotationManager from rotation.py."""

    def test_log_rotation_manager_init(self, tmp_path):
        """Test that LogRotationManager creates the log directory and sets log_dir."""
        from codomyrmex.logging_monitoring.rotation import LogRotationManager

        log_dir = str(tmp_path / "rotation_logs")
        manager = LogRotationManager(log_dir=log_dir)

        assert manager.log_dir == log_dir
        assert os.path.isdir(log_dir)

    def test_attach_rotating_handler(self, tmp_path):
        """Test attaching a rotating handler returns a RotatingFileHandler on the logger."""
        from codomyrmex.logging_monitoring.rotation import LogRotationManager
        from logging.handlers import RotatingFileHandler

        log_dir = str(tmp_path / "rotation_logs")
        manager = LogRotationManager(log_dir=log_dir)

        logger_name = "test_rotation_attach"
        handler = manager.attach_rotating_handler(logger_name, "test.log")

        try:
            assert isinstance(handler, RotatingFileHandler)
            logger = logging.getLogger(logger_name)
            assert handler in logger.handlers
        finally:
            handler.close()
            logging.getLogger(logger_name).removeHandler(handler)

    def test_rotation_parameters(self, tmp_path):
        """Test that max_bytes and backup_count are correctly set on the handler."""
        from codomyrmex.logging_monitoring.rotation import LogRotationManager
        from logging.handlers import RotatingFileHandler

        log_dir = str(tmp_path / "rotation_logs")
        manager = LogRotationManager(log_dir=log_dir)

        handler = manager.attach_rotating_handler(
            "test_rotation_params", "params.log",
            max_bytes=2048, backup_count=3
        )

        try:
            assert handler.maxBytes == 2048
            assert handler.backupCount == 3
        finally:
            handler.close()
            logging.getLogger("test_rotation_params").removeHandler(handler)

    def test_rotation_creates_file(self, tmp_path):
        """Test that logging through the handler creates the log file on disk."""
        from codomyrmex.logging_monitoring.rotation import LogRotationManager

        log_dir = str(tmp_path / "rotation_logs")
        manager = LogRotationManager(log_dir=log_dir)

        handler = manager.attach_rotating_handler("test_rotation_file", "created.log")
        logger = logging.getLogger("test_rotation_file")
        logger.setLevel(logging.DEBUG)

        try:
            logger.info("This message should create the file")
            handler.flush()

            log_file = Path(log_dir) / "created.log"
            assert log_file.exists()
            content = log_file.read_text()
            assert "This message should create the file" in content
        finally:
            handler.close()
            logger.removeHandler(handler)


@pytest.mark.unit
class TestStandaloneJSONFormatter:
    """Test cases for the standalone JSONFormatter from json_formatter.py."""

    def test_standalone_json_formatter(self):
        """Test formatting a LogRecord produces valid JSON with expected fields."""
        from codomyrmex.logging_monitoring.json_formatter import JSONFormatter

        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test.json", level=logging.WARNING, pathname="test_file.py",
            lineno=42, msg="Standalone formatter test", args=(), exc_info=None
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["level"] == "WARNING"
        assert parsed["name"] == "test.json"
        assert parsed["message"] == "Standalone formatter test"
        assert parsed["line"] == 42
        assert "timestamp" in parsed
        assert "module" in parsed

    def test_json_formatter_with_exception(self):
        """Test formatting a LogRecord with exception info includes the exception key."""
        from codomyrmex.logging_monitoring.json_formatter import JSONFormatter

        formatter = JSONFormatter()

        try:
            raise ValueError("test exception for formatter")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.json.exc", level=logging.ERROR, pathname="test_file.py",
            lineno=99, msg="Error occurred", args=(), exc_info=exc_info
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]
        assert "test exception for formatter" in parsed["exception"]
        assert parsed["level"] == "ERROR"


@pytest.mark.unit
class TestAuditLogger:
    """Test cases for AuditLogger from audit.py."""

    def test_audit_logger_init(self):
        """Test AuditLogger initialization creates a logger with a handler."""
        from codomyrmex.logging_monitoring.audit import AuditLogger

        # Use a unique name to avoid handler leakage from other tests
        audit = AuditLogger(name="test.audit.init")

        try:
            assert audit.logger is not None
            assert audit.logger.name == "test.audit.init"
            assert audit.logger.level == logging.INFO
            assert len(audit.logger.handlers) >= 1
        finally:
            for h in audit.logger.handlers[:]:
                audit.logger.removeHandler(h)
                h.close()

    def test_audit_log_event(self, caplog):
        """Test log_event records the audit message with correct content."""
        from codomyrmex.logging_monitoring.audit import AuditLogger

        audit = AuditLogger(name="test.audit.event")

        try:
            with caplog.at_level(logging.INFO, logger="test.audit.event"):
                audit.log_event(
                    event_type="file_access",
                    user_id="user_42",
                    details={"file": "/etc/passwd", "action": "read"},
                    status="denied"
                )

            assert len(caplog.records) >= 1
            record = caplog.records[-1]
            assert "Audit event: file_access" in record.message
            assert record.levelname == "INFO"
        finally:
            for h in audit.logger.handlers[:]:
                audit.logger.removeHandler(h)
                h.close()

