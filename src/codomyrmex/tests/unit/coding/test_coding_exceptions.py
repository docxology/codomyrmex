"""Zero-mock tests for coding.exceptions module.

Covers all 10 custom exception classes. Tests construction, attribute storage,
inheritance hierarchy, and exception raising.

No mocks. No MagicMock. No monkeypatch.
"""
from __future__ import annotations

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
    SandboxResourceError,
    SandboxSecurityError,
    TracingError,
)
from codomyrmex.coding.exceptions import (
    RuntimeError as CodingRuntimeError,
)
from codomyrmex.exceptions import (
    CodeExecutionError,
    CodomyrmexError,
    SandboxError,
)


@pytest.mark.unit
class TestExecutionTimeoutError:
    """Tests for ExecutionTimeoutError exception."""

    def test_inherits_from_code_execution_error(self):
        """ExecutionTimeoutError is a subclass of CodeExecutionError."""
        assert issubclass(ExecutionTimeoutError, CodeExecutionError)

    def test_inherits_from_codomyrmex_error(self):
        """ExecutionTimeoutError inherits CodomyrmexError (transitive)."""
        assert issubclass(ExecutionTimeoutError, CodomyrmexError)

    def test_basic_construction(self):
        """ExecutionTimeoutError can be constructed with just a message."""
        exc = ExecutionTimeoutError("Execution timed out")
        assert exc.message == "Execution timed out"

    def test_timeout_seconds_stored_in_context(self):
        """timeout_seconds is stored in exception context."""
        exc = ExecutionTimeoutError("Timed out", timeout_seconds=30.0)
        assert exc.context["timeout_seconds"] == 30.0

    def test_process_id_stored_in_context(self):
        """process_id is stored in exception context."""
        exc = ExecutionTimeoutError("Timed out", process_id=12345)
        assert exc.context["process_id"] == 12345

    def test_no_optional_fields_no_context_keys(self):
        """Without optional args, context doesn't have those keys."""
        exc = ExecutionTimeoutError("Timed out")
        assert "timeout_seconds" not in exc.context
        assert "process_id" not in exc.context

    def test_can_be_raised_and_caught(self):
        """ExecutionTimeoutError can be raised and caught."""
        with pytest.raises(ExecutionTimeoutError) as exc_info:
            raise ExecutionTimeoutError("Timeout after 30s", timeout_seconds=30)
        assert exc_info.value.context["timeout_seconds"] == 30

    def test_can_be_caught_as_code_execution_error(self):
        """ExecutionTimeoutError caught by parent CodeExecutionError handler."""
        with pytest.raises(CodeExecutionError):
            raise ExecutionTimeoutError("Timed out")


@pytest.mark.unit
class TestMemoryLimitError:
    """Tests for MemoryLimitError exception."""

    def test_inherits_from_code_execution_error(self):
        assert issubclass(MemoryLimitError, CodeExecutionError)

    def test_basic_construction(self):
        exc = MemoryLimitError("Memory exceeded")
        assert exc.message == "Memory exceeded"

    def test_limit_bytes_stored(self):
        exc = MemoryLimitError("OOM", limit_bytes=268435456)
        assert exc.context["limit_bytes"] == 268435456

    def test_used_bytes_stored(self):
        exc = MemoryLimitError("OOM", used_bytes=300000000)
        assert exc.context["used_bytes"] == 300000000

    def test_both_fields_stored(self):
        exc = MemoryLimitError("OOM", limit_bytes=256 * 1024 * 1024, used_bytes=300 * 1024 * 1024)
        assert "limit_bytes" in exc.context
        assert "used_bytes" in exc.context

    def test_can_be_raised(self):
        with pytest.raises(MemoryLimitError):
            raise MemoryLimitError("Memory limit exceeded")


@pytest.mark.unit
class TestSandboxSecurityError:
    """Tests for SandboxSecurityError exception."""

    def test_inherits_from_sandbox_error(self):
        assert issubclass(SandboxSecurityError, SandboxError)

    def test_inherits_from_codomyrmex_error(self):
        assert issubclass(SandboxSecurityError, CodomyrmexError)

    def test_basic_construction(self):
        exc = SandboxSecurityError("Security violation")
        assert exc.message == "Security violation"

    def test_violation_type_stored(self):
        exc = SandboxSecurityError("Violation", violation_type="network_access")
        assert exc.context["violation_type"] == "network_access"

    def test_attempted_action_stored(self):
        exc = SandboxSecurityError("Violation", attempted_action="open_socket")
        assert exc.context["attempted_action"] == "open_socket"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(SandboxSecurityError):
            raise SandboxSecurityError("Network access denied", violation_type="network")


@pytest.mark.unit
class TestSandboxResourceError:
    """Tests for SandboxResourceError exception."""

    def test_inherits_from_sandbox_error(self):
        assert issubclass(SandboxResourceError, SandboxError)

    def test_basic_construction(self):
        exc = SandboxResourceError("Resource allocation failed")
        assert exc.message == "Resource allocation failed"

    def test_resource_type_stored(self):
        exc = SandboxResourceError("Failed", resource_type="cpu")
        assert exc.context["resource_type"] == "cpu"

    def test_can_be_raised(self):
        with pytest.raises(SandboxResourceError):
            raise SandboxResourceError("Cannot allocate")


@pytest.mark.unit
class TestDebuggerError:
    """Tests for DebuggerError exception."""

    def test_inherits_from_codomyrmex_error(self):
        assert issubclass(DebuggerError, CodomyrmexError)

    def test_basic_construction(self):
        exc = DebuggerError("Debugger failed")
        assert exc.message == "Debugger failed"

    def test_debugger_stored_in_context(self):
        exc = DebuggerError("Failed", debugger="pdb")
        assert exc.context["debugger"] == "pdb"

    def test_target_process_stored_in_context(self):
        exc = DebuggerError("Failed", target_process=9876)
        assert exc.context["target_process"] == 9876

    def test_none_process_id_not_stored(self):
        """target_process=None (default) should not add key to context."""
        exc = DebuggerError("Failed")
        assert "target_process" not in exc.context


@pytest.mark.unit
class TestBreakpointError:
    """Tests for BreakpointError exception."""

    def test_inherits_from_debugger_error(self):
        assert issubclass(BreakpointError, DebuggerError)

    def test_inherits_from_codomyrmex_error(self):
        assert issubclass(BreakpointError, CodomyrmexError)

    def test_basic_construction(self):
        exc = BreakpointError("Breakpoint failed")
        assert exc.message == "Breakpoint failed"

    def test_file_path_stored(self):
        exc = BreakpointError("Failed", file_path="/tmp/test.py")
        assert exc.context["file_path"] == "/tmp/test.py"

    def test_line_stored(self):
        exc = BreakpointError("Failed", line=42)
        assert exc.context["line"] == 42

    def test_can_be_caught_as_debugger_error(self):
        with pytest.raises(DebuggerError):
            raise BreakpointError("Breakpoint at line 10")


@pytest.mark.unit
class TestCodeReviewError:
    """Tests for CodeReviewError and ReviewCommentError exceptions."""

    def test_code_review_error_inherits_codomyrmex(self):
        assert issubclass(CodeReviewError, CodomyrmexError)

    def test_review_comment_error_inherits_code_review_error(self):
        assert issubclass(ReviewCommentError, CodeReviewError)

    def test_code_review_error_basic(self):
        exc = CodeReviewError("Review failed")
        assert exc.message == "Review failed"

    def test_review_comment_error_basic(self):
        exc = ReviewCommentError("Comment processing failed")
        assert exc.message == "Comment processing failed"

    def test_review_comment_caught_as_code_review_error(self):
        with pytest.raises(CodeReviewError):
            raise ReviewCommentError("Bad comment")


@pytest.mark.unit
class TestMonitoringErrors:
    """Tests for MonitoringError, ProfilingError, TracingError exceptions."""

    def test_monitoring_error_inherits_codomyrmex(self):
        assert issubclass(MonitoringError, CodomyrmexError)

    def test_profiling_error_inherits_monitoring(self):
        assert issubclass(ProfilingError, MonitoringError)

    def test_tracing_error_inherits_monitoring(self):
        assert issubclass(TracingError, MonitoringError)

    def test_monitoring_error_basic(self):
        exc = MonitoringError("Monitoring failed")
        assert exc.message == "Monitoring failed"

    def test_monitoring_error_metric_stored(self):
        exc = MonitoringError("Failed", metric="cpu_usage")
        assert exc.context["metric"] == "cpu_usage"

    def test_monitoring_error_source_stored(self):
        exc = MonitoringError("Failed", source="profiler")
        assert exc.context["source"] == "profiler"

    def test_profiling_error_basic(self):
        exc = ProfilingError("Profiling failed")
        assert exc.message == "Profiling failed"

    def test_tracing_error_basic(self):
        exc = TracingError("Tracing failed")
        assert exc.message == "Tracing failed"

    def test_profiling_caught_as_monitoring(self):
        with pytest.raises(MonitoringError):
            raise ProfilingError("Profile error")

    def test_tracing_caught_as_monitoring(self):
        with pytest.raises(MonitoringError):
            raise TracingError("Trace error")


@pytest.mark.unit
class TestCodingRuntimeError:
    """Tests for coding.exceptions.RuntimeError (not builtin)."""

    def test_inherits_from_code_execution_error(self):
        assert issubclass(CodingRuntimeError, CodeExecutionError)

    def test_basic_construction(self):
        exc = CodingRuntimeError("Runtime error occurred")
        assert exc.message == "Runtime error occurred"

    def test_error_type_stored(self):
        exc = CodingRuntimeError("Error", error_type="ZeroDivisionError")
        assert exc.context["error_type"] == "ZeroDivisionError"

    def test_traceback_stored(self):
        exc = CodingRuntimeError("Error", traceback="Traceback (most recent call last):\n...")
        assert "traceback" in exc.context

    def test_can_be_raised(self):
        with pytest.raises(CodingRuntimeError):
            raise CodingRuntimeError("Division by zero", error_type="ZeroDivisionError")

    def test_can_be_caught_as_code_execution_error(self):
        with pytest.raises(CodeExecutionError):
            raise CodingRuntimeError("Runtime error")
