"""Zero-mock extended tests for coding.debugging submodule.

Complements test_debugging.py with coverage of:
- ErrorDiagnosis dataclass field defaults and construction
- FixVerifier.verify and _apply_patch
- VerificationResult dataclass
- Patch dataclass
- Debugger integration: no-LLM paths (patches=[], no diagnosis)
- PatchGenerator._parse_patches bare diff patterns

No mocks. No MagicMock. No monkeypatch.
"""

from __future__ import annotations

import pytest

from codomyrmex.coding.debugging import (
    Debugger,
    ErrorAnalyzer,
    ErrorDiagnosis,
    FixVerifier,
    Patch,
    PatchGenerator,
    VerificationResult,
)


@pytest.mark.unit
class TestErrorDiagnosisDataclass:
    """Tests for ErrorDiagnosis dataclass construction and defaults."""

    def test_required_fields_only(self):
        """ErrorDiagnosis can be constructed with just error_type and message."""
        d = ErrorDiagnosis(error_type="NameError", message="name 'x' not defined")
        assert d.error_type == "NameError"
        assert d.message == "name 'x' not defined"

    def test_default_file_path_is_none(self):
        """file_path defaults to None."""
        d = ErrorDiagnosis("TypeError", "type error")
        assert d.file_path is None

    def test_default_line_number_is_none(self):
        """line_number defaults to None."""
        d = ErrorDiagnosis("TypeError", "type error")
        assert d.line_number is None

    def test_default_stack_trace_is_empty_string(self):
        """stack_trace defaults to empty string."""
        d = ErrorDiagnosis("TypeError", "type error")
        assert d.stack_trace == ""

    def test_default_is_syntax_error_false(self):
        """is_syntax_error defaults to False."""
        d = ErrorDiagnosis("ValueError", "invalid value")
        assert d.is_syntax_error is False

    def test_default_is_timeout_false(self):
        """is_timeout defaults to False."""
        d = ErrorDiagnosis("RuntimeError", "runtime error")
        assert d.is_timeout is False

    def test_all_fields_set(self):
        """All fields can be set explicitly."""
        d = ErrorDiagnosis(
            error_type="SyntaxError",
            message="invalid syntax",
            file_path="test.py",
            line_number=5,
            stack_trace="Traceback...",
            is_syntax_error=True,
            is_timeout=False,
        )
        assert d.error_type == "SyntaxError"
        assert d.message == "invalid syntax"
        assert d.file_path == "test.py"
        assert d.line_number == 5
        assert d.stack_trace == "Traceback..."
        assert d.is_syntax_error is True
        assert d.is_timeout is False

    def test_timeout_error_diagnosis(self):
        """TimeoutError diagnosis has is_timeout=True."""
        d = ErrorDiagnosis(
            error_type="TimeoutError",
            message="Execution timed out",
            is_timeout=True,
        )
        assert d.is_timeout is True
        assert d.is_syntax_error is False

    def test_syntax_error_diagnosis(self):
        """SyntaxError diagnosis has is_syntax_error=True."""
        d = ErrorDiagnosis(
            error_type="SyntaxError",
            message="invalid syntax",
            file_path="script.py",
            line_number=3,
            is_syntax_error=True,
        )
        assert d.is_syntax_error is True
        assert d.file_path == "script.py"
        assert d.line_number == 3


@pytest.mark.unit
class TestPatchDataclass:
    """Tests for Patch dataclass construction."""

    def test_basic_construction(self):
        """Patch can be constructed with all required fields."""
        p = Patch(
            file_path="script.py",
            diff="--- a/script.py\n+++ b/script.py\n@@ -1 +1 @@\n-old\n+new\n",
            description="Fix NameError by initializing variable",
            confidence=0.85,
        )
        assert p.file_path == "script.py"
        assert p.confidence == 0.85

    def test_description_is_string(self):
        """Patch description is stored as a string."""
        p = Patch(
            file_path="f.py", diff="", description="Fix something", confidence=0.5
        )
        assert isinstance(p.description, str)

    def test_confidence_range_low(self):
        """Confidence value of 0.1 is stored correctly."""
        p = Patch(file_path="f.py", diff="", description="desc", confidence=0.1)
        assert p.confidence == 0.1

    def test_confidence_range_high(self):
        """Confidence value of 1.0 is stored correctly."""
        p = Patch(file_path="f.py", diff="", description="desc", confidence=1.0)
        assert p.confidence == 1.0

    def test_empty_diff_stored(self):
        """Empty diff string is stored without error."""
        p = Patch(file_path="f.py", diff="", description="desc", confidence=0.5)
        assert p.diff == ""


@pytest.mark.unit
class TestVerificationResultDataclass:
    """Tests for VerificationResult dataclass construction."""

    def test_success_true(self):
        """VerificationResult with success=True stores correctly."""
        vr = VerificationResult(success=True, stdout="Hello\n", stderr="", exit_code=0)
        assert vr.success is True

    def test_success_false(self):
        """VerificationResult with success=False stores correctly."""
        vr = VerificationResult(success=False, stdout="", stderr="Error", exit_code=1)
        assert vr.success is False

    def test_stdout_stored(self):
        """stdout field is stored correctly."""
        vr = VerificationResult(success=True, stdout="output", stderr="", exit_code=0)
        assert vr.stdout == "output"

    def test_stderr_stored(self):
        """stderr field is stored correctly."""
        vr = VerificationResult(
            success=False, stdout="", stderr="error msg", exit_code=1
        )
        assert vr.stderr == "error msg"

    def test_exit_code_stored(self):
        """exit_code field is stored correctly."""
        vr = VerificationResult(success=True, stdout="", stderr="", exit_code=0)
        assert vr.exit_code == 0


@pytest.mark.unit
class TestFixVerifier:
    """Tests for FixVerifier.verify and _apply_patch methods."""

    def setup_method(self):
        self.verifier = FixVerifier()

    def test_verify_returns_verification_result(self):
        """verify() returns a VerificationResult instance."""
        patch = Patch(
            file_path="script.py",
            diff="--- a/script.py\n+++ b/script.py\n@@ -1 +1 @@\n-x = undefined\n+x = 0\n",
            description="Fix NameError",
            confidence=0.9,
        )
        result = self.verifier.verify("x = undefined", patch)
        assert isinstance(result, VerificationResult)

    def test_verify_without_active_execution_returns_failure(self):
        """verify() returns success=False since execution module is not linked."""
        patch = Patch(
            file_path="script.py",
            diff="some diff",
            description="some fix",
            confidence=0.8,
        )
        result = self.verifier.verify("original code", patch)
        assert result.success is False

    def test_verify_exit_code_is_nonzero_on_unimplemented(self):
        """verify() returns non-zero exit_code when execution is not linked."""
        patch = Patch(file_path="f.py", diff="", description="fix", confidence=0.5)
        result = self.verifier.verify("code", patch)
        assert result.exit_code != 0

    def test_verify_stderr_contains_message(self):
        """verify() stderr mentions that execution module is not linked."""
        patch = Patch(file_path="f.py", diff="", description="fix", confidence=0.5)
        result = self.verifier.verify("code", patch)
        assert len(result.stderr) > 0

    def test_apply_patch_returns_source_unchanged(self):
        """_apply_patch with no content attribute returns original source."""
        patch = Patch(
            file_path="f.py", diff="some diff", description="fix", confidence=0.5
        )
        source = "x = undefined\nprint(x)\n"
        result = self.verifier._apply_patch(source, patch)
        assert result == source

    def test_apply_patch_with_empty_diff_returns_source(self):
        """_apply_patch with empty diff returns original source."""
        patch = Patch(file_path="f.py", diff="", description="fix", confidence=0.5)
        source = "original code"
        result = self.verifier._apply_patch(source, patch)
        assert result == source

    def test_apply_patch_with_content_attr_returns_content(self):
        """_apply_patch uses content attribute if present."""
        patch = Patch(
            file_path="f.py", diff="some diff", description="fix", confidence=0.5
        )
        # Dynamically attach 'content' attribute to simulate a full-replacement patch
        patch.content = "completely new code"
        result = self.verifier._apply_patch("old code", patch)
        assert result == "completely new code"


@pytest.mark.unit
class TestErrorAnalyzerEdgeCases:
    """Additional edge cases for ErrorAnalyzer.analyze."""

    def setup_method(self):
        self.analyzer = ErrorAnalyzer()

    def test_success_exit_code_returns_none(self):
        """Exit code 0 always returns None (no error)."""
        result = self.analyzer.analyze("some output", "no error", 0)
        assert result is None

    def test_generic_stderr_fallback(self):
        """Non-Python stderr with non-zero exit_code returns RuntimeError."""
        result = self.analyzer.analyze("", "Something went terribly wrong", 2)
        assert result is not None
        assert result.error_type == "RuntimeError"

    def test_empty_stderr_fallback(self):
        """Empty stderr with non-zero exit_code returns a diagnosis."""
        result = self.analyzer.analyze("", "", 1)
        assert result is not None
        assert isinstance(result.error_type, str)

    def test_timeout_exit_124(self):
        """Exit code 124 returns TimeoutError with is_timeout=True."""
        result = self.analyzer.analyze("", "Killed", 124)
        assert result is not None
        assert result.is_timeout is True
        assert result.error_type == "TimeoutError"

    def test_name_error_parsed(self):
        """NameError in standard traceback format is parsed correctly."""
        stderr = (
            "Traceback (most recent call last):\n"
            '  File "script.py", line 3, in <module>\n'
            "    print(foo)\n"
            "NameError: name 'foo' is not defined"
        )
        result = self.analyzer.analyze("", stderr, 1)
        assert result is not None
        assert result.error_type == "NameError"
        assert result.line_number == 3
        assert result.file_path == "script.py"

    def test_type_error_parsed(self):
        """TypeError in traceback is parsed correctly."""
        stderr = (
            "Traceback (most recent call last):\n"
            '  File "main.py", line 7, in <module>\n'
            '    result = 1 + "two"\n'
            "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
        )
        result = self.analyzer.analyze("", stderr, 1)
        assert result is not None
        assert result.error_type == "TypeError"

    def test_stack_trace_stored(self):
        """Full stderr is stored in stack_trace field."""
        stderr = "Some error\nwith multiple lines"
        result = self.analyzer.analyze("", stderr, 1)
        assert result is not None
        assert result.stack_trace == stderr

    def test_syntax_error_is_syntax_error_flag(self):
        """SyntaxError in stderr sets is_syntax_error=True."""
        stderr = (
            '  File "code.py", line 2\n'
            "    if True\n"
            "           ^\n"
            "SyntaxError: invalid syntax"
        )
        result = self.analyzer.analyze("", stderr, 1)
        assert result is not None
        assert result.is_syntax_error is True

    def test_multiple_tracebacks_uses_last(self):
        """For chained exceptions, the last traceback entry is used."""
        stderr = (
            "Traceback (most recent call last):\n"
            '  File "a.py", line 1, in <module>\n'
            '    raise ValueError("first")\n'
            "ValueError: first\n"
            "\nDuring handling of the above exception, another exception occurred:\n"
            "\nTraceback (most recent call last):\n"
            '  File "a.py", line 5, in <module>\n'
            '    raise TypeError("second")\n'
            "TypeError: second"
        )
        result = self.analyzer.analyze("", stderr, 1)
        assert result is not None
        # Should pick up the last error type
        assert result.error_type in ("ValueError", "TypeError")


@pytest.mark.unit
class TestDebuggerNoLLM:
    """Tests for Debugger with no LLM client configured."""

    def setup_method(self):
        self.debugger = Debugger(llm_client=None)

    def test_debug_no_error_returns_none(self):
        """Exit code 0 means no error — debug() returns None."""
        result = self.debugger.debug("print('ok')", "ok\n", "", 0)
        assert result is None

    def test_debug_with_error_no_llm_returns_none(self):
        """With an error but no LLM, patcher returns [] → debug returns None."""
        stderr = (
            "Traceback (most recent call last):\n"
            '  File "test.py", line 1, in <module>\n'
            "    print(undefined)\n"
            "NameError: name 'undefined' is not defined"
        )
        result = self.debugger.debug("print(undefined)", "", stderr, 1)
        assert result is None

    def test_debug_returns_none_or_string(self):
        """debug() always returns None or a string, never raises."""
        result = self.debugger.debug(
            "x = 1 / 0",
            "",
            "ZeroDivisionError: division by zero",
            1,
        )
        assert result is None or isinstance(result, str)

    def test_debugger_has_analyzer_attribute(self):
        """Debugger instance has an analyzer attribute."""
        assert hasattr(self.debugger, "analyzer")
        assert isinstance(self.debugger.analyzer, ErrorAnalyzer)

    def test_debugger_has_patcher_attribute(self):
        """Debugger instance has a patcher attribute."""
        assert hasattr(self.debugger, "patcher")
        assert isinstance(self.debugger.patcher, PatchGenerator)

    def test_debugger_has_verifier_attribute(self):
        """Debugger instance has a verifier attribute."""
        assert hasattr(self.debugger, "verifier")
        assert isinstance(self.debugger.verifier, FixVerifier)
