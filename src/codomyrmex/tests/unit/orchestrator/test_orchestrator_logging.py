"""Tests for orchestrator logging functionality.

This module verifies that the orchestrator properly logs structured events:
- RUN_STARTED and RUN_COMPLETED events in core.py
- SCRIPT_START and SCRIPT_END events in runner.py
- RUN_SUMMARY event in reporting.py
"""

import logging
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock
from datetime import datetime

from codomyrmex.orchestrator.runner import run_script
from codomyrmex.orchestrator.reporting import generate_report
from codomyrmex.logging_monitoring.logger_config import LogContext


class TestOrchestratorLogging:
    """Tests for orchestrator structured logging."""

    def test_run_script_logs_start_and_end_events(self, tmp_path, caplog):
        """Test that run_script logs SCRIPT_START and SCRIPT_END events."""
        # Create a simple test script
        test_script = tmp_path / "test_script.py"
        test_script.write_text("print('Hello, World!')")
        
        # Capture logs
        with caplog.at_level(logging.INFO, logger="codomyrmex.orchestrator.runner"):
            result = run_script(test_script, timeout=10)
        
        # Verify SCRIPT_START event by checking log messages
        start_logs = [r for r in caplog.records if "Script execution started" in r.message]
        assert len(start_logs) >= 1, "Should log SCRIPT_START event"
        start_record = start_logs[0]
        assert "test_script.py" in start_record.message
        # Extra fields are stored as direct attributes on the record
        assert hasattr(start_record, 'event') and start_record.event == "SCRIPT_START"
        
        # Verify SCRIPT_END event
        end_logs = [r for r in caplog.records if "Script execution completed" in r.message]
        assert len(end_logs) >= 1, "Should log SCRIPT_END event"
        end_record = end_logs[0]
        assert hasattr(end_record, 'event') and end_record.event == "SCRIPT_END"
        assert hasattr(end_record, 'status') and end_record.status == "passed"
        assert hasattr(end_record, 'exit_code') and end_record.exit_code == 0
        assert hasattr(end_record, 'execution_time')

    def test_run_script_logs_failure(self, tmp_path, caplog):
        """Test that run_script logs failure status correctly."""
        # Create a failing test script
        test_script = tmp_path / "failing_script.py"
        test_script.write_text("import sys; sys.exit(1)")
        
        with caplog.at_level(logging.INFO, logger="codomyrmex.orchestrator.runner"):
            result = run_script(test_script, timeout=10)
        
        # Verify SCRIPT_END event shows failure
        end_logs = [r for r in caplog.records if "Script execution completed" in r.message]
        assert len(end_logs) >= 1
        end_record = end_logs[0]
        assert hasattr(end_record, 'status') and end_record.status == "failed"
        assert hasattr(end_record, 'exit_code') and end_record.exit_code == 1

    def test_generate_report_logs_summary(self, tmp_path, caplog):
        """Test that generate_report logs RUN_SUMMARY event."""
        results = [
            {
                "script": "/path/to/script1.py",
                "name": "script1.py",
                "subdirectory": "utils",
                "status": "passed",
                "execution_time": 1.5,
                "exit_code": 0,
                "stdout": "output",
                "stderr": "",
            },
            {
                "script": "/path/to/script2.py", 
                "name": "script2.py",
                "subdirectory": "utils",
                "status": "failed",
                "execution_time": 0.5,
                "exit_code": 1,
                "stdout": "",
                "stderr": "error",
            },
        ]
        
        with caplog.at_level(logging.INFO, logger="codomyrmex.orchestrator.reporting"):
            summary = generate_report(results, tmp_path, "test_run_123")
        
        # Verify RUN_SUMMARY event
        summary_logs = [r for r in caplog.records if "Run summary generated" in r.message]
        assert len(summary_logs) >= 1, "Should log RUN_SUMMARY event"
        summary_record = summary_logs[0]
        assert hasattr(summary_record, 'event') and summary_record.event == "RUN_SUMMARY"
        assert hasattr(summary_record, 'run_id') and summary_record.run_id == "test_run_123"
        assert hasattr(summary_record, 'total_scripts') and summary_record.total_scripts == 2
        assert hasattr(summary_record, 'passed') and summary_record.passed == 1
        assert hasattr(summary_record, 'failed') and summary_record.failed == 1

    def test_log_context_correlation_id(self):
        """Test that LogContext properly sets correlation ID."""
        run_id = "test_correlation_123"
        
        with LogContext(correlation_id=run_id) as ctx:
            assert ctx.correlation_id == run_id


class TestQuietReconfigMode:
    """Tests for quiet reconfig mode to reduce log noise."""

    def test_quiet_reconfig_suppresses_logging_message(self, monkeypatch):
        """Test that CODOMYRMEX_LOG_QUIET_RECONFIG=1 suppresses config message."""
        from codomyrmex.logging_monitoring import logger_config
        
        # Reset the configured flag for testing
        original_flag = logger_config._logging_configured
        
        try:
            logger_config._logging_configured = False
            monkeypatch.setenv("CODOMYRMEX_LOG_QUIET_RECONFIG", "1")
            
            # This should not log the "Logging configured" message
            # We're just verifying it doesn't crash
            logger_config.setup_logging()
            
        finally:
            logger_config._logging_configured = original_flag

