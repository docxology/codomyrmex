"""Tests for coding.exceptions module."""

import pytest

from codomyrmex.coding.exceptions import (
    BreakpointError,
    CodeReviewError,
    DebuggerError,
    ExecutionTimeoutError,
    MemoryLimitError,
    MonitoringError,
    ProfilingError,
    ReviewCommentError,
    RuntimeError,
    SandboxResourceError,
    SandboxSecurityError,
    TracingError,
)
from codomyrmex.exceptions import CodeExecutionError, CodomyrmexError


class TestExecutionTimeoutError:
    def test_with_timeout_and_pid(self):
        e = ExecutionTimeoutError("timed out", timeout_seconds=30.0, process_id=1234)
        assert e.context["timeout_seconds"] == 30.0
        assert e.context["process_id"] == 1234

    def test_without_optional_fields(self):
        e = ExecutionTimeoutError("timed out")
        assert "timeout_seconds" not in e.context
        assert "process_id" not in e.context

    def test_inherits_code_execution_error(self):
        assert issubclass(ExecutionTimeoutError, CodeExecutionError)


class TestMemoryLimitError:
    def test_with_limits(self):
        e = MemoryLimitError("OOM", limit_bytes=1024*1024, used_bytes=2*1024*1024)
        assert e.context["limit_bytes"] == 1024*1024
        assert e.context["used_bytes"] == 2*1024*1024

    def test_message_stored(self):
        e = MemoryLimitError("out of memory")
        assert "out of memory" in str(e)


class TestSandboxErrors:
    def test_security_error(self):
        e = SandboxSecurityError("policy violation", violation_type="network_access",
                                 attempted_action="socket.connect")
        assert e.context["violation_type"] == "network_access"
        assert e.context["attempted_action"] == "socket.connect"

    def test_resource_error(self):
        e = SandboxResourceError("no resources", resource_type="memory")
        assert e.context["resource_type"] == "memory"

    def test_resource_error_without_type(self):
        e = SandboxResourceError("no resources")
        assert "resource_type" not in e.context


class TestDebuggerError:
    def test_with_all_fields(self):
        e = DebuggerError("debug fail", debugger="pdb", target_process=9999)
        assert e.context["debugger"] == "pdb"
        assert e.context["target_process"] == 9999

    def test_inherits_codomyrmex_error(self):
        assert issubclass(DebuggerError, CodomyrmexError)


class TestBreakpointError:
    def test_with_location(self):
        e = BreakpointError("bp fail", file_path="/app/main.py", line=42)
        assert e.context["file_path"] == "/app/main.py"
        assert e.context["line"] == 42

    def test_inherits_debugger_error(self):
        assert issubclass(BreakpointError, DebuggerError)


class TestCodeReviewErrors:
    def test_code_review_error(self):
        e = CodeReviewError("review failed")
        assert isinstance(e, CodomyrmexError)

    def test_review_comment_error(self):
        e = ReviewCommentError("comment failed")
        assert issubclass(ReviewCommentError, CodeReviewError)


class TestMonitoringErrors:
    def test_monitoring_error(self):
        e = MonitoringError("monitoring fail", metric="cpu_usage", source="prometheus")
        assert e.context["metric"] == "cpu_usage"
        assert e.context["source"] == "prometheus"

    def test_profiling_error_inherits(self):
        assert issubclass(ProfilingError, MonitoringError)
        e = ProfilingError("profile fail")
        assert isinstance(e, MonitoringError)

    def test_tracing_error_inherits(self):
        assert issubclass(TracingError, MonitoringError)


class TestRuntimeError:
    def test_with_context(self):
        e = RuntimeError("runtime fail", error_type="ZeroDivisionError",
                        traceback="File x.py line 1")
        assert e.context["error_type"] == "ZeroDivisionError"
        assert e.context["traceback"] == "File x.py line 1"

    def test_inherits_code_execution_error(self):
        assert issubclass(RuntimeError, CodeExecutionError)
