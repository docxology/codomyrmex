"""Comprehensive tests for coding.exceptions — zero-mock.

Covers: ExecutionTimeoutError, MemoryLimitError, SandboxSecurityError,
SandboxResourceError, DebuggerError, BreakpointError, CodeReviewError,
ReviewCommentError, MonitoringError, ProfilingError, TracingError, RuntimeError.
"""

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
from codomyrmex.coding.exceptions import RuntimeError as CodingRuntimeError
from codomyrmex.exceptions import CodeExecutionError, CodomyrmexError, SandboxError


class TestExecutionTimeoutError:
    def test_create(self):
        e = ExecutionTimeoutError("Timed out after 30s")
        assert "Timed out" in str(e)

    def test_with_context(self):
        e = ExecutionTimeoutError("timeout", timeout_seconds=30.0, process_id=1234)
        assert e.context.get("timeout_seconds") == 30.0
        assert e.context.get("process_id") == 1234

    def test_inherits_code_execution_error(self):
        e = ExecutionTimeoutError("test")
        assert isinstance(e, CodeExecutionError)


class TestMemoryLimitError:
    def test_create(self):
        e = MemoryLimitError("Memory exceeded")
        assert "Memory" in str(e)

    def test_with_context(self):
        e = MemoryLimitError("OOM", limit_bytes=1048576, used_bytes=2097152)
        assert e.context.get("limit_bytes") == 1048576


class TestSandboxSecurityError:
    def test_create(self):
        e = SandboxSecurityError("Security violation")
        assert isinstance(e, SandboxError)

    def test_with_context(self):
        e = SandboxSecurityError(
            "Forbidden",
            violation_type="file_access",
            attempted_action="read /etc/passwd",
        )
        assert e.context.get("violation_type") == "file_access"


class TestSandboxResourceError:
    def test_create(self):
        e = SandboxResourceError("Resource unavailable")
        assert isinstance(e, SandboxError)

    def test_with_resource_type(self):
        e = SandboxResourceError("No GPU", resource_type="gpu")
        assert e.context.get("resource_type") == "gpu"


class TestDebuggerError:
    def test_create(self):
        e = DebuggerError("Debugger crashed")
        assert isinstance(e, CodomyrmexError)

    def test_with_context(self):
        e = DebuggerError("Failed", debugger="gdb", target_process=5678)
        assert e.context.get("debugger") == "gdb"


class TestBreakpointError:
    def test_create(self):
        e = BreakpointError("Cannot set breakpoint")
        assert isinstance(e, DebuggerError)

    def test_with_context(self):
        e = BreakpointError("Invalid line", file_path="main.py", line=42)
        assert e.context.get("line") == 42


class TestCodeReviewError:
    def test_create(self):
        e = CodeReviewError("Review failed")
        assert isinstance(e, CodomyrmexError)


class TestReviewCommentError:
    def test_inherits(self):
        e = ReviewCommentError("Comment parse error")
        assert isinstance(e, CodeReviewError)


class TestMonitoringError:
    def test_create(self):
        e = MonitoringError("Monitoring down")
        assert isinstance(e, CodomyrmexError)

    def test_with_context(self):
        e = MonitoringError("Metric fail", metric="cpu_usage", source="prometheus")
        assert e.context.get("metric") == "cpu_usage"


class TestProfilingError:
    def test_inherits(self):
        assert issubclass(ProfilingError, MonitoringError)


class TestTracingError:
    def test_inherits(self):
        assert issubclass(TracingError, MonitoringError)


class TestCodingRuntimeError:
    def test_create(self):
        e = CodingRuntimeError("Segfault")
        assert isinstance(e, CodeExecutionError)

    def test_with_context(self):
        e = CodingRuntimeError(
            "Error", error_type="NameError", traceback="Traceback..."
        )
        assert e.context.get("error_type") == "NameError"


class TestExceptionHierarchy:
    def test_all_inherit_codomyrmex_error(self):
        for cls in [
            ExecutionTimeoutError,
            MemoryLimitError,
            SandboxSecurityError,
            SandboxResourceError,
            DebuggerError,
            BreakpointError,
            CodeReviewError,
            ReviewCommentError,
            MonitoringError,
            ProfilingError,
            TracingError,
            CodingRuntimeError,
        ]:
            assert issubclass(cls, CodomyrmexError)
