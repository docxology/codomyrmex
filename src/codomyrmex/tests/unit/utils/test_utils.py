"""Unit tests for the Codomyrmex utilities module.

Tests for ensure_directory, safe_json_loads, safe_json_dumps, hash_content,
hash_file, timing_decorator, retry, get_timestamp, truncate_string, get_env,
flatten_dict, deep_merge, and RefinedUtilities.
"""

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from codomyrmex.utils import RefinedUtilities


class TestRefinedUtilities(unittest.TestCase):
    """Tests for RefinedUtilities class."""

    def test_deep_merge(self):
        """Test deep merging of dictionaries."""
        dict1 = {"a": {"b": 1}}
        dict2 = {"a": {"c": 2}, "d": 3}
        expected = {"a": {"b": 1, "c": 2}, "d": 3}
        result = RefinedUtilities.deep_merge(dict1, dict2)
        self.assertEqual(result, expected)

    def test_retry(self):
        """Test retry decorator."""
        self.count = 0

        @RefinedUtilities.retry(retries=3, backoff_factor=0.1)
        def failing_func():
            self.count += 1
            if self.count < 2:
                raise ValueError("Fail")
            return "success"

        result = failing_func()
        self.assertEqual(result, "success")
        self.assertEqual(self.count, 2)


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_create_new_directory(self, tmp_path):
        """Test creating a new directory."""
        from codomyrmex.utils import ensure_directory

        new_dir = tmp_path / "new_directory"
        result = ensure_directory(new_dir)

        assert result.exists()
        assert result.is_dir()

    def test_create_nested_directory(self, tmp_path):
        """Test creating nested directories."""
        from codomyrmex.utils import ensure_directory

        nested_dir = tmp_path / "level1" / "level2" / "level3"
        result = ensure_directory(nested_dir)

        assert result.exists()
        assert result.is_dir()

    def test_existing_directory(self, tmp_path):
        """Test with existing directory."""
        from codomyrmex.utils import ensure_directory

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = ensure_directory(existing_dir)

        assert result.exists()

    def test_string_path(self, tmp_path):
        """Test with string path."""
        from codomyrmex.utils import ensure_directory

        new_dir = str(tmp_path / "string_path_dir")
        result = ensure_directory(new_dir)

        assert result.exists()


class TestSafeJsonLoads:
    """Tests for safe_json_loads function."""

    def test_valid_json(self):
        """Test parsing valid JSON."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads('{"key": "value"}')

        assert result == {"key": "value"}

    def test_invalid_json_returns_default(self):
        """Test invalid JSON returns default."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads("not valid json")

        assert result is None

    def test_custom_default(self):
        """Test custom default value."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads("invalid", default=[])

        assert result == []

    def test_none_input(self):
        """Test None input returns default."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads(None, default={})

        assert result == {}


class TestSafeJsonDumps:
    """Tests for safe_json_dumps function."""

    def test_valid_object(self):
        """Test serializing valid object."""
        from codomyrmex.utils import safe_json_dumps

        result = safe_json_dumps({"key": "value"})

        assert '"key"' in result
        assert '"value"' in result

    def test_with_indent(self):
        """Test serialization with indent."""
        from codomyrmex.utils import safe_json_dumps

        result = safe_json_dumps({"a": 1}, indent=4)

        assert "    " in result

    def test_custom_default_on_failure(self):
        """Test custom default on serialization failure."""
        from codomyrmex.utils import safe_json_dumps

        class NonSerializable:
            pass

        result = safe_json_dumps(NonSerializable(), default="[]")

        # Should convert using str() function, not return the default
        assert result is not None


class TestHashContent:
    """Tests for hash_content function."""

    def test_hash_string(self):
        """Test hashing a string."""
        from codomyrmex.utils import hash_content

        result = hash_content("test content")

        assert len(result) == 64  # SHA256 hex length
        assert result.isalnum()

    def test_hash_bytes(self):
        """Test hashing bytes."""
        from codomyrmex.utils import hash_content

        result = hash_content(b"test content")

        assert len(result) == 64

    def test_different_algorithms(self):
        """Test different hash algorithms."""
        from codomyrmex.utils import hash_content

        sha256 = hash_content("test", algorithm="sha256")
        sha512 = hash_content("test", algorithm="sha512")
        md5 = hash_content("test", algorithm="md5")

        assert len(sha256) == 64
        assert len(sha512) == 128
        assert len(md5) == 32

    def test_same_input_same_hash(self):
        """Test same input produces same hash."""
        from codomyrmex.utils import hash_content

        hash1 = hash_content("identical")
        hash2 = hash_content("identical")

        assert hash1 == hash2

    def test_different_input_different_hash(self):
        """Test different input produces different hash."""
        from codomyrmex.utils import hash_content

        hash1 = hash_content("content1")
        hash2 = hash_content("content2")

        assert hash1 != hash2


class TestHashFile:
    """Tests for hash_file function."""

    def test_hash_existing_file(self, tmp_path):
        """Test hashing an existing file."""
        from codomyrmex.utils import hash_file

        test_file = tmp_path / "test.txt"
        test_file.write_text("file content")

        result = hash_file(test_file)

        assert result is not None
        assert len(result) == 64

    def test_hash_nonexistent_file(self):
        """Test hashing non-existent file returns None."""
        from codomyrmex.utils import hash_file

        result = hash_file("/nonexistent/file.txt")

        assert result is None

    def test_hash_file_string_path(self, tmp_path):
        """Test hashing with string path."""
        from codomyrmex.utils import hash_file

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = hash_file(str(test_file))

        assert result is not None


class TestTimingDecorator:
    """Tests for timing_decorator."""

    def test_timing_with_dict_result(self):
        """Test timing decorator adds execution_time_ms to dict result."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def func_returning_dict():
            return {"status": "ok"}

        result = func_returning_dict()

        assert "execution_time_ms" in result
        assert result["status"] == "ok"

    def test_timing_with_non_dict_result(self):
        """Test timing decorator with non-dict result."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def func_returning_string():
            return "result"

        result = func_returning_string()

        assert result == "result"


class TestRetryDecorator:
    """Tests for retry decorator."""

    def test_retry_success_first_try(self):
        """Test function succeeding on first try."""
        from codomyrmex.utils import retry

        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def always_succeeds():
            nonlocal call_count
            call_count += 1
            return "success"

        result = always_succeeds()

        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test function succeeding after failures."""
        from codomyrmex.utils import retry

        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = fails_twice()

        assert result == "success"
        assert call_count == 3

    def test_retry_all_attempts_fail(self):
        """Test function failing all attempts."""
        from codomyrmex.utils import retry

        @retry(max_attempts=2, delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

    def test_retry_specific_exceptions(self):
        """Test retry with specific exception types."""
        from codomyrmex.utils import retry

        @retry(max_attempts=2, delay=0.01, exceptions=(ValueError,))
        def raises_type_error():
            raise TypeError("Not caught")

        with pytest.raises(TypeError):
            raises_type_error()


class TestGetTimestamp:
    """Tests for get_timestamp function."""

    def test_default_format(self):
        """Test default timestamp format."""
        from codomyrmex.utils import get_timestamp

        result = get_timestamp()

        # Format: YYYY-MM-DD_HH-MM-SS
        assert len(result) == 19
        assert "_" in result
        assert "-" in result

    def test_custom_format(self):
        """Test custom timestamp format."""
        from codomyrmex.utils import get_timestamp

        result = get_timestamp(fmt="%Y%m%d")

        assert len(result) == 8
        assert result.isdigit()


class TestTruncateString:
    """Tests for truncate_string function."""

    def test_string_under_limit(self):
        """Test string under maximum length."""
        from codomyrmex.utils import truncate_string

        result = truncate_string("short", max_length=100)

        assert result == "short"

    def test_string_over_limit(self):
        """Test string over maximum length."""
        from codomyrmex.utils import truncate_string

        result = truncate_string("this is a very long string", max_length=10)

        assert len(result) == 10
        assert result.endswith("...")

    def test_custom_suffix(self):
        """Test custom truncation suffix."""
        from codomyrmex.utils import truncate_string

        result = truncate_string("long string here", max_length=10, suffix=">>")

        assert result.endswith(">>")

    def test_exact_length(self):
        """Test string exactly at maximum length."""
        from codomyrmex.utils import truncate_string

        result = truncate_string("exact", max_length=5)

        assert result == "exact"


class TestGetEnv:
    """Tests for get_env function."""

    def test_existing_env_var(self):
        """Test getting existing environment variable."""
        from codomyrmex.utils import get_env

        os.environ["TEST_VAR"] = "test_value"
        try:
            result = get_env("TEST_VAR")
            assert result == "test_value"
        finally:
            del os.environ["TEST_VAR"]

    def test_missing_env_var_with_default(self):
        """Test missing env var with default."""
        from codomyrmex.utils import get_env

        result = get_env("NONEXISTENT_VAR", default="default_value")

        assert result == "default_value"

    def test_missing_required_env_var(self):
        """Test missing required env var raises error."""
        from codomyrmex.utils import get_env

        with pytest.raises(ValueError):
            get_env("NONEXISTENT_VAR", required=True)


class TestFlattenDict:
    """Tests for flatten_dict function."""

    def test_flat_dict(self):
        """Test flattening already flat dictionary."""
        from codomyrmex.utils import flatten_dict

        result = flatten_dict({"a": 1, "b": 2})

        assert result == {"a": 1, "b": 2}

    def test_nested_dict(self):
        """Test flattening nested dictionary."""
        from codomyrmex.utils import flatten_dict

        result = flatten_dict({"a": {"b": {"c": 1}}})

        assert result == {"a.b.c": 1}

    def test_custom_separator(self):
        """Test flattening with custom separator."""
        from codomyrmex.utils import flatten_dict

        result = flatten_dict({"a": {"b": 1}}, sep="/")

        assert result == {"a/b": 1}

    def test_mixed_nested_dict(self):
        """Test flattening mixed nested dictionary."""
        from codomyrmex.utils import flatten_dict

        result = flatten_dict({"a": 1, "b": {"c": 2, "d": {"e": 3}}})

        assert result == {"a": 1, "b.c": 2, "b.d.e": 3}


class TestDeepMerge:
    """Tests for deep_merge function."""

    def test_simple_merge(self):
        """Test simple dictionary merge."""
        from codomyrmex.utils import deep_merge

        result = deep_merge({"a": 1}, {"b": 2})

        assert result == {"a": 1, "b": 2}

    def test_nested_merge(self):
        """Test nested dictionary merge."""
        from codomyrmex.utils import deep_merge

        base = {"a": {"x": 1}}
        override = {"a": {"y": 2}}

        result = deep_merge(base, override)

        assert result == {"a": {"x": 1, "y": 2}}

    def test_override_value(self):
        """Test value override in merge."""
        from codomyrmex.utils import deep_merge

        base = {"a": {"x": 1}}
        override = {"a": {"x": 2}}

        result = deep_merge(base, override)

        assert result == {"a": {"x": 2}}

    def test_original_unchanged(self):
        """Test original dictionaries unchanged."""
        from codomyrmex.utils import deep_merge

        base = {"a": 1}
        override = {"b": 2}

        deep_merge(base, override)

        assert base == {"a": 1}
        assert override == {"b": 2}


if __name__ == "__main__":
    unittest.main()
