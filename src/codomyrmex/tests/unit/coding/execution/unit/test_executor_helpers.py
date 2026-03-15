"""Unit tests for executor helper functions: _compress_trace, _paginate_output, validate_session_id."""

import os
import tempfile

import pytest

from codomyrmex.coding.execution.executor import (
    DEFAULT_TIMEOUT,
    MAX_TIMEOUT,
    MIN_TIMEOUT,
    _compress_trace,
    _paginate_output,
    validate_timeout,
)
from codomyrmex.coding.execution.session_manager import validate_session_id


@pytest.mark.unit
class TestCompressTrace:
    """Tests for _compress_trace function."""

    def test_empty_string(self):
        assert _compress_trace("") == ""

    def test_none_passthrough(self):
        # _compress_trace checks `if not text` and returns text as-is
        assert _compress_trace(None) is None

    def test_short_output_unchanged(self):
        text = "\n".join([f"line {i}" for i in range(5)])
        assert _compress_trace(text) == text

    def test_fewer_than_10_lines_unchanged(self):
        text = "\n".join([f"line {i}" for i in range(9)])
        assert _compress_trace(text) == text

    def test_single_line_repetition_compressed(self):
        repeated = "ValueError: invalid input"
        lines = [f"frame {i}" for i in range(3)] + [repeated] * 10 + ["after"]
        text = "\n".join(lines)
        result = _compress_trace(text)
        assert "Line repeated 9 more times" in result
        assert result.count(repeated) == 1

    def test_block_repetition_compressed(self):
        # Repeated 3-line block, repeated 4 times total
        block = ["Error in module A", "  at line 42", "  called from B"]
        lines = ["header"] + block * 4 + ["footer"]
        text = "\n".join(lines)
        result = _compress_trace(text)
        assert "Above block of" in result
        assert "repeated" in result
        assert "header" in result
        assert "footer" in result

    def test_no_repetition_unchanged(self):
        lines = [f"unique line {i}" for i in range(20)]
        text = "\n".join(lines)
        assert _compress_trace(text) == text

    def test_mixed_compression(self):
        lines = (
            ["preamble"]
            + ["dup_line"] * 8
            + ["unique"] * 5
        )
        text = "\n".join(lines)
        result = _compress_trace(text)
        assert "Line repeated 7 more times" in result
        assert "preamble" in result


@pytest.mark.unit
class TestPaginateOutput:
    """Tests for _paginate_output function."""

    def test_empty_string(self):
        assert _paginate_output("") == ""

    def test_none_passthrough(self):
        assert _paginate_output(None) is None

    def test_short_output_unchanged(self):
        text = "\n".join([f"line {i}" for i in range(100)])
        assert _paginate_output(text) == text

    def test_exactly_5000_lines_unchanged(self):
        text = "\n".join([f"line {i}" for i in range(5000)])
        assert _paginate_output(text) == text

    def test_over_5000_lines_truncated(self):
        text = "\n".join([f"line {i}" for i in range(6000)])
        result = _paginate_output(text)
        assert "[Output truncated" in result
        assert "6000 lines total" in result
        # First 500 lines should be in preview
        assert "line 0" in result
        assert "line 499" in result

    def test_cached_file_is_created(self):
        text = "\n".join([f"line {i}" for i in range(6000)])
        result = _paginate_output(text)
        # Extract file path from result
        assert "File cached at" in result
        # Find the path
        start = result.find("File cached at ") + len("File cached at ")
        end = result.find(".", start) + len(".log")
        file_path = result[start:end]
        assert os.path.exists(file_path)
        # Cleanup
        os.unlink(file_path)

    def test_cached_file_contains_full_output(self):
        text = "\n".join([f"line {i}" for i in range(6000)])
        result = _paginate_output(text)
        start = result.find("file_path='") + len("file_path='")
        end = result.find("'", start)
        file_path = result[start:end]
        with open(file_path) as f:
            cached = f.read()
        assert cached == text
        os.unlink(file_path)


@pytest.mark.unit
class TestValidateSessionId:
    """Tests for validate_session_id function."""

    def test_none_returns_none(self):
        assert validate_session_id(None) is None

    def test_valid_alphanumeric(self):
        assert validate_session_id("abc123") == "abc123"

    def test_valid_with_underscores(self):
        assert validate_session_id("user_123_session") == "user_123_session"

    def test_valid_with_hyphens(self):
        assert validate_session_id("session-abc-def") == "session-abc-def"

    def test_valid_mixed(self):
        assert validate_session_id("my-session_123") == "my-session_123"

    def test_invalid_special_chars(self):
        assert validate_session_id("invalid@session!") is None

    def test_invalid_spaces(self):
        assert validate_session_id("has spaces") is None

    def test_invalid_dots(self):
        assert validate_session_id("has.dots") is None

    def test_too_long(self):
        assert validate_session_id("a" * 100) is None

    def test_exactly_64_chars_valid(self):
        sid = "a" * 64
        assert validate_session_id(sid) == sid

    def test_65_chars_invalid(self):
        assert validate_session_id("a" * 65) is None

    def test_empty_string(self):
        # Empty string is technically valid (all chars are alnum-like, length <= 64)
        assert validate_session_id("") == ""

    def test_non_string_type(self):
        assert validate_session_id(123) is None


@pytest.mark.unit
class TestValidateTimeout:
    """Additional tests for validate_timeout function."""

    def test_none_returns_default(self):
        assert validate_timeout(None) == DEFAULT_TIMEOUT

    def test_boundary_min(self):
        assert validate_timeout(MIN_TIMEOUT) == MIN_TIMEOUT

    def test_boundary_max(self):
        assert validate_timeout(MAX_TIMEOUT) == MAX_TIMEOUT

    def test_below_min_clamped(self):
        assert validate_timeout(-10) == MIN_TIMEOUT

    def test_above_max_clamped(self):
        assert validate_timeout(999) == MAX_TIMEOUT

    def test_zero_clamped_to_min(self):
        assert validate_timeout(0) == MIN_TIMEOUT
