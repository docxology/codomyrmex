"""Zero-mock tests for coding.mcp_tools module.

Covers: code_execute, code_list_languages, code_review_file,
code_review_project, code_debug — all MCP tool functions.

Tests the non-Docker execution paths (unsupported language, error paths)
and the metadata/language-listing functions which require no Docker.

No mocks. No MagicMock. No monkeypatch.
"""

from __future__ import annotations

import pytest

from codomyrmex.coding.mcp_tools import (
    code_debug,
    code_execute,
    code_list_languages,
    code_review_file,
    code_review_project,
)


@pytest.mark.unit
class TestCodeListLanguages:
    """Tests for code_list_languages MCP tool."""

    def test_returns_dict(self):
        """code_list_languages returns a dictionary."""
        result = code_list_languages()
        assert isinstance(result, dict)

    def test_status_is_success(self):
        """code_list_languages always returns success status."""
        result = code_list_languages()
        assert result["status"] == "success"

    def test_result_has_languages_key(self):
        """Result contains a 'languages' key."""
        result = code_list_languages()
        assert "languages" in result

    def test_languages_is_list(self):
        """The languages value is a list."""
        result = code_list_languages()
        assert isinstance(result["languages"], list)

    def test_languages_list_not_empty(self):
        """The languages list has at least one item."""
        result = code_list_languages()
        assert len(result["languages"]) > 0

    def test_python_in_languages(self):
        """Python is in the supported languages list."""
        result = code_list_languages()
        assert "python" in result["languages"]

    def test_javascript_in_languages(self):
        """JavaScript is in the supported languages list."""
        result = code_list_languages()
        assert "javascript" in result["languages"]

    def test_languages_are_sorted(self):
        """Languages list is sorted alphabetically."""
        result = code_list_languages()
        languages = result["languages"]
        assert languages == sorted(languages)

    def test_has_all_8_expected_languages(self):
        """Exactly 8 languages (python, js, java, cpp, c, go, rust, bash)."""
        result = code_list_languages()
        expected = {"python", "javascript", "java", "cpp", "c", "go", "rust", "bash"}
        assert expected == set(result["languages"])

    def test_mcp_tool_meta_attribute_present(self):
        """code_list_languages is decorated with @mcp_tool (has _mcp_tool_meta)."""
        assert hasattr(code_list_languages, "_mcp_tool_meta")

    def test_code_execute_has_mcp_tool_meta(self):
        """code_execute is decorated with @mcp_tool."""
        assert hasattr(code_execute, "_mcp_tool_meta")

    def test_code_review_file_has_mcp_tool_meta(self):
        """code_review_file is decorated with @mcp_tool."""
        assert hasattr(code_review_file, "_mcp_tool_meta")

    def test_code_review_project_has_mcp_tool_meta(self):
        """code_review_project is decorated with @mcp_tool."""
        assert hasattr(code_review_project, "_mcp_tool_meta")

    def test_code_debug_has_mcp_tool_meta(self):
        """code_debug is decorated with @mcp_tool."""
        assert hasattr(code_debug, "_mcp_tool_meta")


@pytest.mark.unit
class TestCodeExecuteUnsupportedLanguage:
    """Tests for code_execute with unsupported languages (no Docker needed).

    Note: code_execute MCP tool wraps execute_code. When execute_code returns
    a dict (even for unsupported language), code_execute returns:
        {"status": "success", "result": <execute_code result dict>}
    The inner result dict has status="setup_error" for unsupported languages.
    An exception in the outer wrapper would return {"status": "error", "message": ...}.
    """

    def test_unsupported_language_outer_status_success(self):
        """MCP wrapper returns outer status=success (no exception thrown)."""
        result = code_execute(language="cobol", code="DISPLAY 'Hello'.")
        assert result["status"] == "success"

    def test_unsupported_language_inner_status_setup_error(self):
        """Inner result status is setup_error for unsupported language."""
        result = code_execute(language="cobol", code="DISPLAY 'Hello'.")
        assert result["result"]["status"] == "setup_error"

    def test_unsupported_language_result_is_dict(self):
        """Result is always a dictionary."""
        result = code_execute(language="fortran", code="PRINT *, 'hi'")
        assert isinstance(result, dict)

    def test_unsupported_language_has_result_key(self):
        """Result dict contains a 'result' key with the inner execution result."""
        result = code_execute(language="ruby", code="puts 'hi'")
        assert "result" in result

    def test_unsupported_language_inner_has_error_message(self):
        """Inner result has an error_message field for unsupported language."""
        result = code_execute(language="php", code="<?php echo 'hi'; ?>")
        inner = result.get("result", {})
        assert "error_message" in inner
        assert isinstance(inner["error_message"], str)

    def test_unsupported_language_inner_exit_code_negative(self):
        """Inner result exit_code is -1 for unsupported language."""
        result = code_execute(language="cobol", code="code")
        inner = result.get("result", {})
        assert inner.get("exit_code") == -1

    def test_code_execute_returns_dict_type(self):
        """code_execute always returns a dict."""
        result = code_execute(language="python", code="")
        assert isinstance(result, dict)


@pytest.mark.unit
class TestCodeDebug:
    """Tests for code_debug MCP tool (no LLM, no Docker needed)."""

    def test_returns_dict(self):
        """code_debug always returns a dict."""
        result = code_debug(
            code="print(undefined_var)",
            stdout="",
            stderr="NameError: name 'undefined_var' is not defined",
            exit_code=1,
        )
        assert isinstance(result, dict)

    def test_result_has_status_key(self):
        """Result has a 'status' key."""
        result = code_debug(
            code="x = 1 / 0",
            stdout="",
            stderr="ZeroDivisionError: division by zero",
            exit_code=1,
        )
        assert "status" in result

    def test_success_path_has_diagnosis_key(self):
        """On success, result has a 'diagnosis' key."""
        result = code_debug(
            code="x = 1",
            stdout="",
            stderr="",
            exit_code=0,
        )
        # With exit_code=0, Debugger.debug returns None (no error) → success
        assert result["status"] == "success"
        assert "diagnosis" in result

    def test_with_name_error_in_stderr(self):
        """NameError in stderr is handled gracefully."""
        result = code_debug(
            code="print(foo)",
            stdout="",
            stderr="NameError: name 'foo' is not defined",
            exit_code=1,
        )
        assert isinstance(result, dict)
        assert "status" in result

    def test_with_syntax_error(self):
        """SyntaxError in stderr is handled gracefully."""
        result = code_debug(
            code="def bad(:\n    pass",
            stdout="",
            stderr='File "test.py", line 1\n    def bad(:\nSyntaxError: invalid syntax',
            exit_code=1,
        )
        assert isinstance(result, dict)

    def test_default_parameters_work(self):
        """code_debug has default values for stdout, stderr, exit_code."""
        result = code_debug(code="print('hello')")
        assert isinstance(result, dict)

    def test_timeout_exit_code_handled(self):
        """Exit code 124 (timeout) is handled by the debugger."""
        result = code_debug(
            code="import time; time.sleep(9999)",
            stdout="",
            stderr="Terminated",
            exit_code=124,
        )
        assert isinstance(result, dict)
        assert result.get("status") in ("success", "error")


@pytest.mark.unit
class TestCodeReviewFile:
    """Tests for code_review_file MCP tool with real files."""

    def test_nonexistent_file_returns_error(self):
        """Reviewing a file that doesn't exist returns error status."""
        result = code_review_file(path="/nonexistent/path/to/file.py")
        assert result["status"] == "error"

    def test_nonexistent_file_has_message(self):
        """Error result for nonexistent file includes message."""
        result = code_review_file(path="/nonexistent/path.py")
        assert "message" in result
        assert isinstance(result["message"], str)

    def test_valid_python_file_returns_dict(self, tmp_path):
        """A valid Python file returns a dict result."""
        py_file = tmp_path / "sample.py"
        py_file.write_text("def hello():\n    return 'world'\n")
        result = code_review_file(path=str(py_file))
        assert isinstance(result, dict)

    def test_valid_python_file_has_status(self, tmp_path):
        """Result for a valid file always has a status key."""
        py_file = tmp_path / "sample.py"
        py_file.write_text("x = 1\n")
        result = code_review_file(path=str(py_file))
        assert "status" in result

    def test_empty_python_file_does_not_crash(self, tmp_path):
        """An empty Python file doesn't crash the reviewer."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        result = code_review_file(path=str(empty_file))
        assert isinstance(result, dict)


@pytest.mark.unit
class TestCodeReviewProject:
    """Tests for code_review_project MCP tool."""

    def test_nonexistent_path_returns_error(self):
        """Reviewing a nonexistent project path returns error status."""
        result = code_review_project(path="/nonexistent/project/path")
        assert result["status"] == "error"

    def test_nonexistent_path_has_message(self):
        """Error result has a message."""
        result = code_review_project(path="/nonexistent/project")
        assert "message" in result

    def test_empty_dir_returns_dict(self, tmp_path):
        """An empty directory returns a dict result."""
        result = code_review_project(path=str(tmp_path))
        assert isinstance(result, dict)

    def test_empty_dir_has_status(self, tmp_path):
        """Result for an empty directory has a status key."""
        result = code_review_project(path=str(tmp_path))
        assert "status" in result

    def test_project_with_python_file_does_not_crash(self, tmp_path):
        """Project dir with Python files doesn't crash."""
        py_file = tmp_path / "main.py"
        py_file.write_text("def main():\n    pass\n")
        result = code_review_project(path=str(tmp_path))
        assert isinstance(result, dict)
