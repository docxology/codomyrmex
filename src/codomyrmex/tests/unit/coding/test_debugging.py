"""Zero-Mock tests for debugging module.

Uses real ErrorAnalyzer, PatchGenerator, and Debugger with real internal
components instead of mocking them.
"""

import pytest

from codomyrmex.coding.debugging import (
    Debugger,
    ErrorAnalyzer,
    ErrorDiagnosis,
    Patch,
    PatchGenerator,
)


@pytest.mark.unit
class TestErrorAnalyzer:
    def setup_method(self):
        self.analyzer = ErrorAnalyzer()

    def test_parse_python_syntax_error(self):
        stderr = 'File "test.py", line 1\n    if True\n          ^\nSyntaxError: invalid syntax'
        diagnosis = self.analyzer.analyze("", stderr, 1)
        assert diagnosis is not None
        assert diagnosis.error_type == "SyntaxError"
        assert diagnosis.line_number == 1
        assert diagnosis.file_path == "test.py"

    def test_parse_python_runtime_error(self):
        stderr = 'Traceback (most recent call last):\n  File "main.py", line 10, in <module>\n    print(1/0)\nZeroDivisionError: division by zero'
        diagnosis = self.analyzer.analyze("", stderr, 1)
        assert diagnosis is not None
        assert diagnosis.error_type == "ZeroDivisionError"
        assert diagnosis.line_number == 10
        assert diagnosis.message == "division by zero"

    def test_timeout_error(self):
        diagnosis = self.analyzer.analyze("", "Terminated", 124)
        assert diagnosis is not None
        assert diagnosis.error_type == "TimeoutError"
        assert diagnosis.is_timeout


@pytest.mark.unit
class TestPatchGenerator:
    def setup_method(self):
        self.generator = PatchGenerator(llm_client=None)

    def test_generate_no_file_path(self):
        diagnosis = ErrorDiagnosis("Error", "msg")
        patches = self.generator.generate("code", diagnosis)
        assert patches == []

    def test_generate_returns_list(self):
        diagnosis = ErrorDiagnosis("Error", "msg", "file.py", 10, "trace")
        patches = self.generator.generate("code", diagnosis)
        assert isinstance(patches, list)


@pytest.mark.unit
class TestDebugger:
    def setup_method(self):
        self.debugger = Debugger()

    def test_debug_flow_with_real_components(self):
        """Test the full debug flow with real analyzer, patcher, verifier."""
        # Use a real Python error that the analyzer can parse
        source = 'print(1/0)\n'
        stderr = 'Traceback (most recent call last):\n  File "test.py", line 1, in <module>\n    print(1/0)\nZeroDivisionError: division by zero'

        result = self.debugger.debug(source, "", stderr, 1)
        # The debugger may or may not produce a fix (depends on LLM availability),
        # but it should not crash and should return a result or None
        # With no LLM client, patcher returns empty patches, so result may be None
        assert result is None or isinstance(result, dict)

    def test_debug_flow_no_error(self):
        """Test debug flow when exit code is 0 (no error)."""
        result = self.debugger.debug("print('ok')", "ok", "", 0)
        # Should handle gracefully when there is no error to debug
        assert result is None or isinstance(result, dict)
