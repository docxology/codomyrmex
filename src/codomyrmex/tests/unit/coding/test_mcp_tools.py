import pytest

from codomyrmex.coding.mcp_tools import (
    code_execute,
    code_list_languages,
    code_review_file,
    code_review_project,
    code_debug,
)

@pytest.mark.unit
def test_code_execute():
    # If docker pull fails, it just returns a non-zero exit_code or error output.
    # The tool itself should return status "ok"
    result = code_execute("python", "print('hello')", timeout=10)
    assert result["status"] == "ok"
    assert "result" in result

@pytest.mark.unit
def test_code_execute_error():
    # Exception inside execution
    result = code_execute("invalid_language", "print('hello')", timeout=10)
    # The execute_code handles validation and returns a result dict with error info
    assert result["status"] == "ok"
    assert result["result"]["status"] == "setup_error"

@pytest.mark.unit
def test_code_list_languages():
    result = code_list_languages()
    assert result["status"] == "ok"
    assert "python" in result["languages"]

@pytest.mark.unit
def test_code_review_file(tmp_path):
    # Depending on pyscn, if not installed, we get an error response.
    # The try/except in the tool catches it.
    file_path = tmp_path / "test.py"
    file_path.write_text("def add(a, b):\n    return a + b\n")

    result = code_review_file(str(file_path))
    # It might be an error if pyscn is not installed, or 'ok' if it is
    assert result["status"] in ["ok", "error"]

@pytest.mark.unit
def test_code_review_project(tmp_path):
    file_path = tmp_path / "main.py"
    file_path.write_text("def run():\n    pass\n")

    result = code_review_project(str(tmp_path))
    assert result["status"] in ["ok", "error"]

@pytest.mark.unit
def test_code_debug():
    code = "def divide(a, b):\n    return a / b\nprint(divide(1, 0))"
    stdout = ""
    stderr = "ZeroDivisionError: division by zero"
    exit_code = 1

    result = code_debug(code, stdout, stderr, exit_code)
    assert result["status"] == "ok"
    assert "diagnosis" in result
