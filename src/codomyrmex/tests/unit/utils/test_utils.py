import hashlib
import tempfile

"""Unit tests for the Codomyrmex utilities module.

Tests for ensure_directory, safe_json_loads, safe_json_dumps, hash_content,
hash_file, timing_decorator, retry, get_timestamp, truncate_string, get_env,
flatten_dict, deep_merge, RefinedUtilities, CLI helpers, and script base classes.
"""

import argparse
import asyncio
import os
import time
import unittest
from pathlib import Path

import pytest

from codomyrmex.utils import RefinedUtilities


@pytest.mark.unit
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

    def test_resolve_path_absolute(self):
        """Test resolving an absolute path."""
        abs_path = "/tmp/test/path"
        result = RefinedUtilities.resolve_path(abs_path)
        self.assertEqual(result, Path(abs_path))

    def test_resolve_path_relative(self):
        """Test resolving a relative path."""
        rel_path = "relative/path"
        result = RefinedUtilities.resolve_path(rel_path)
        self.assertTrue(result.is_absolute())

    def test_resolve_path_with_base_dir(self):
        """Test resolving a relative path with base directory."""
        rel_path = "subdir/file.txt"
        base_dir = "/base/path"
        result = RefinedUtilities.resolve_path(rel_path, base_dir)
        self.assertEqual(result, Path("/base/path/subdir/file.txt").resolve())


@pytest.mark.unit
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

    def test_returns_path_object(self, tmp_path):
        """Test that ensure_directory returns Path object."""
        from codomyrmex.utils import ensure_directory

        new_dir = tmp_path / "test_dir"
        result = ensure_directory(new_dir)

        assert isinstance(result, Path)


@pytest.mark.unit
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

    def test_empty_string(self):
        """Test empty string returns default."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads("", default={"empty": True})

        assert result == {"empty": True}

    def test_valid_json_array(self):
        """Test parsing valid JSON array."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads('[1, 2, 3]')

        assert result == [1, 2, 3]

    def test_valid_json_number(self):
        """Test parsing valid JSON number."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads('42')

        assert result == 42


@pytest.mark.unit
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

    def test_serializes_list(self):
        """Test serializing a list."""
        from codomyrmex.utils import safe_json_dumps

        result = safe_json_dumps([1, 2, 3])

        assert "[" in result
        assert "1" in result

    def test_serializes_nested_object(self):
        """Test serializing nested object."""
        from codomyrmex.utils import safe_json_dumps

        data = {"level1": {"level2": {"value": 42}}}
        result = safe_json_dumps(data)

        assert "level1" in result
        assert "level2" in result
        assert "42" in result


@pytest.mark.unit
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

    def test_hash_empty_string(self):
        """Test hashing empty string."""
        from codomyrmex.utils import hash_content

        result = hash_content("")

        assert len(result) == 64  # SHA256 always produces 64 char hex


@pytest.mark.unit
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

    def test_hash_file_different_algorithms(self, tmp_path):
        """Test hashing file with different algorithms."""
        from codomyrmex.utils import hash_file

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        sha256 = hash_file(test_file, algorithm="sha256")
        md5 = hash_file(test_file, algorithm="md5")

        assert len(sha256) == 64
        assert len(md5) == 32

    def test_hash_file_same_content_same_hash(self, tmp_path):
        """Test same file content produces same hash."""
        from codomyrmex.utils import hash_file

        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("identical content")
        file2.write_text("identical content")

        hash1 = hash_file(file1)
        hash2 = hash_file(file2)

        assert hash1 == hash2


@pytest.mark.unit
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

    def test_timing_preserves_function_name(self):
        """Test timing decorator preserves function name."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def my_function():
            return {}

        assert my_function.__name__ == "my_function"

    def test_timing_measures_actual_time(self):
        """Test timing decorator measures actual execution time."""
        from codomyrmex.utils import timing_decorator

        @timing_decorator
        def slow_function():
            time.sleep(0.1)
            return {}

        result = slow_function()

        assert result["execution_time_ms"] >= 100


@pytest.mark.unit
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

    def test_retry_with_backoff(self):
        """Test retry with exponential backoff."""
        from codomyrmex.utils import retry

        call_times = []

        @retry(max_attempts=3, delay=0.05, backoff=2.0)
        def track_calls():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Fail")
            return "success"

        result = track_calls()

        assert result == "success"
        # Check delays increase
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            assert delay2 > delay1


@pytest.mark.unit
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

    def test_timestamp_changes_over_time(self):
        """Test that timestamp changes over time."""
        from codomyrmex.utils import get_timestamp

        ts1 = get_timestamp(fmt="%Y%m%d%H%M%S%f")
        time.sleep(0.001)
        ts2 = get_timestamp(fmt="%Y%m%d%H%M%S%f")

        assert ts1 != ts2


@pytest.mark.unit
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

    def test_empty_string(self):
        """Test empty string."""
        from codomyrmex.utils import truncate_string

        result = truncate_string("", max_length=10)

        assert result == ""

    def test_empty_suffix(self):
        """Test truncation with empty suffix."""
        from codomyrmex.utils import truncate_string

        result = truncate_string("long string", max_length=5, suffix="")

        assert len(result) == 5
        assert result == "long "


@pytest.mark.unit
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

    def test_existing_required_env_var(self):
        """Test existing required env var succeeds."""
        from codomyrmex.utils import get_env

        os.environ["REQUIRED_VAR"] = "value"
        try:
            result = get_env("REQUIRED_VAR", required=True)
            assert result == "value"
        finally:
            del os.environ["REQUIRED_VAR"]

    def test_env_var_with_empty_value(self):
        """Test env var with empty value."""
        from codomyrmex.utils import get_env

        os.environ["EMPTY_VAR"] = ""
        try:
            result = get_env("EMPTY_VAR", default="default")
            assert result == ""  # Empty string is valid
        finally:
            del os.environ["EMPTY_VAR"]


@pytest.mark.unit
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

    def test_empty_dict(self):
        """Test flattening empty dictionary."""
        from codomyrmex.utils import flatten_dict

        result = flatten_dict({})

        assert result == {}

    def test_dict_with_list_values(self):
        """Test flattening dict with list values."""
        from codomyrmex.utils import flatten_dict

        result = flatten_dict({"a": [1, 2, 3]})

        assert result == {"a": [1, 2, 3]}


@pytest.mark.unit
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

    def test_deep_merge_multiple_levels(self):
        """Test deep merge with multiple nesting levels."""
        from codomyrmex.utils import deep_merge

        base = {"a": {"b": {"c": 1}}}
        override = {"a": {"b": {"d": 2}, "e": 3}}

        result = deep_merge(base, override)

        assert result == {"a": {"b": {"c": 1, "d": 2}, "e": 3}}

    def test_merge_with_non_dict_override(self):
        """Test merge when override replaces dict with non-dict."""
        from codomyrmex.utils import deep_merge

        base = {"a": {"nested": "value"}}
        override = {"a": "simple"}

        result = deep_merge(base, override)

        assert result == {"a": "simple"}


@pytest.mark.unit
class TestCliHelpers:
    """Tests for CLI helper functions."""

    def test_format_table_empty(self):
        """Test format_table with empty data."""
        from codomyrmex.utils.cli_helpers import format_table

        result = format_table([], ["col1", "col2"])

        assert "No data" in result

    def test_format_table_with_data(self):
        """Test format_table with data."""
        from codomyrmex.utils.cli_helpers import format_table

        data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        headers = ["name", "age"]

        result = format_table(data, headers)

        assert "Alice" in result
        assert "Bob" in result
        assert "name" in result
        assert "age" in result

    def test_format_output_json(self):
        """Test format_output with JSON format."""
        from codomyrmex.utils.cli_helpers import format_output

        data = {"key": "value"}
        result = format_output(data, format_type="json")

        assert '"key"' in result
        assert '"value"' in result

    def test_format_output_text(self):
        """Test format_output with text format."""
        from codomyrmex.utils.cli_helpers import format_output

        data = {"key": "value"}
        result = format_output(data, format_type="text")

        assert result == str(data)

    def test_validate_file_path_exists(self, tmp_path):
        """Test validate_file_path with existing file."""
        from codomyrmex.utils.cli_helpers import validate_file_path

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = validate_file_path(test_file, must_exist=True, must_be_file=True)

        assert result == test_file.resolve()

    def test_validate_file_path_not_exists(self, tmp_path):
        """Test validate_file_path with non-existent file."""
        from codomyrmex.utils.cli_helpers import validate_file_path

        missing_file = tmp_path / "missing.txt"

        with pytest.raises(FileNotFoundError):
            validate_file_path(missing_file, must_exist=True)

    def test_validate_file_path_must_be_dir(self, tmp_path):
        """Test validate_file_path with must_be_dir."""
        from codomyrmex.utils.cli_helpers import validate_file_path

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError):
            validate_file_path(test_file, must_exist=True, must_be_dir=True)

    def test_determine_language_python(self):
        """Test determine_language_from_file for Python."""
        from codomyrmex.utils.cli_helpers import determine_language_from_file

        result = determine_language_from_file("test.py")

        assert result == "python"

    def test_determine_language_javascript(self):
        """Test determine_language_from_file for JavaScript."""
        from codomyrmex.utils.cli_helpers import determine_language_from_file

        result = determine_language_from_file("test.js")

        assert result == "javascript"

    def test_determine_language_unknown(self):
        """Test determine_language_from_file for unknown extension."""
        from codomyrmex.utils.cli_helpers import determine_language_from_file

        result = determine_language_from_file("test.unknown")

        assert result == "python"  # Default

    def test_ensure_output_directory(self, tmp_path):
        """Test ensure_output_directory creates parent directories."""
        from codomyrmex.utils.cli_helpers import ensure_output_directory

        output_file = tmp_path / "nested" / "dir" / "output.txt"

        result = ensure_output_directory(output_file)

        assert result.parent.exists()


@pytest.mark.unit
class TestProgressReporter:
    """Tests for ProgressReporter class."""

    def test_progress_reporter_init(self):
        """Test ProgressReporter initialization."""
        from codomyrmex.utils.cli_helpers import ProgressReporter

        reporter = ProgressReporter(total=100, prefix="Test")

        assert reporter.total == 100
        assert reporter.prefix == "Test"
        assert reporter.current == 0

    def test_progress_reporter_update(self):
        """Test ProgressReporter update."""
        from codomyrmex.utils.cli_helpers import ProgressReporter

        reporter = ProgressReporter(total=100)
        reporter.update(10)

        assert reporter.current == 10

    def test_progress_reporter_set_current(self):
        """Test ProgressReporter set_current."""
        from codomyrmex.utils.cli_helpers import ProgressReporter

        reporter = ProgressReporter(total=100)
        reporter.set_current(50)

        assert reporter.current == 50

    def test_progress_reporter_complete(self):
        """Test ProgressReporter complete."""
        from codomyrmex.utils.cli_helpers import ProgressReporter

        reporter = ProgressReporter(total=100)
        reporter.complete()

        assert reporter.current == reporter.total

    def test_progress_reporter_cap_at_total(self):
        """Test ProgressReporter caps at total."""
        from codomyrmex.utils.cli_helpers import ProgressReporter

        reporter = ProgressReporter(total=100)
        reporter.update(150)

        assert reporter.current == 100


@pytest.mark.unit
class TestScriptBase:
    """Tests for ScriptBase and related classes."""

    def test_script_config_defaults(self):
        """Test ScriptConfig default values."""
        from codomyrmex.utils.process.script_base import ScriptConfig

        config = ScriptConfig()

        assert config.dry_run is False
        assert config.verbose is False
        assert config.quiet is False
        assert config.output_format == "json"
        assert config.save_output is True
        assert config.log_level == "INFO"
        assert config.timeout == 300

    def test_script_config_from_dict(self):
        """Test ScriptConfig.from_dict."""
        from codomyrmex.utils.process.script_base import ScriptConfig

        data = {"dry_run": True, "verbose": True, "custom_key": "value"}
        config = ScriptConfig.from_dict(data)

        assert config.dry_run is True
        assert config.verbose is True
        assert config.custom.get("custom_key") == "value"

    def test_script_config_to_dict(self):
        """Test ScriptConfig.to_dict."""
        from codomyrmex.utils.process.script_base import ScriptConfig

        config = ScriptConfig(dry_run=True, verbose=True)
        result = config.to_dict()

        assert result["dry_run"] is True
        assert result["verbose"] is True

    def test_script_result_to_dict(self):
        """Test ScriptResult.to_dict."""
        from codomyrmex.utils.process.script_base import ScriptResult

        result = ScriptResult(
            script_name="test",
            status="success",
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T00:00:01",
            duration_seconds=1.0,
            exit_code=0
        )

        d = result.to_dict()

        assert d["script_name"] == "test"
        assert d["status"] == "success"
        assert d["exit_code"] == 0

    def test_script_result_to_json(self):
        """Test ScriptResult.to_json."""
        from codomyrmex.utils.process.script_base import ScriptResult

        result = ScriptResult(
            script_name="test",
            status="success",
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T00:00:01",
            duration_seconds=1.0,
            exit_code=0
        )

        json_str = result.to_json()

        assert '"script_name"' in json_str
        assert '"test"' in json_str


@pytest.mark.unit
class TestAddCommonArguments:
    """Tests for add_common_arguments function."""

    def test_adds_dry_run(self):
        """Test add_common_arguments adds dry-run."""
        from codomyrmex.utils.cli_helpers import add_common_arguments

        parser = argparse.ArgumentParser()
        add_common_arguments(parser)

        args = parser.parse_args(["--dry-run"])

        assert args.dry_run is True

    def test_adds_format(self):
        """Test add_common_arguments adds format."""
        from codomyrmex.utils.cli_helpers import add_common_arguments

        parser = argparse.ArgumentParser()
        add_common_arguments(parser)

        args = parser.parse_args(["--format", "json"])

        assert args.format == "json"

    def test_adds_verbose(self):
        """Test add_common_arguments adds verbose."""
        from codomyrmex.utils.cli_helpers import add_common_arguments

        parser = argparse.ArgumentParser()
        add_common_arguments(parser)

        args = parser.parse_args(["-v"])

        assert args.verbose is True

    def test_adds_quiet(self):
        """Test add_common_arguments adds quiet."""
        from codomyrmex.utils.cli_helpers import add_common_arguments

        parser = argparse.ArgumentParser()
        add_common_arguments(parser)

        args = parser.parse_args(["-q"])

        assert args.quiet is True


@pytest.mark.unit
class TestFormatResult:
    """Tests for format_result function."""

    def test_format_result_dict_success(self):
        """Test format_result with dict containing success."""
        from codomyrmex.utils.cli_helpers import format_result

        result = {"success": True, "output": "test output"}
        success, message = format_result(result, output_key="output")

        assert success is True
        assert message == "test output"

    def test_format_result_dict_failure(self):
        """Test format_result with dict containing failure."""
        from codomyrmex.utils.cli_helpers import format_result

        result = {"success": False}
        success, message = format_result(result)

        assert success is False
        assert message is None

    def test_format_result_bool(self):
        """Test format_result with bool."""
        from codomyrmex.utils.cli_helpers import format_result

        success, message = format_result(True)

        assert success is True
        assert message is None

    def test_format_result_other(self):
        """Test format_result with other type."""
        from codomyrmex.utils.cli_helpers import format_result

        success, message = format_result("result string")

        assert success is True
        assert message == "result string"


@pytest.mark.unit
class TestPrintFunctions:
    """Tests for print helper functions."""

    def test_print_with_color_default(self, capsys):
        """Test print_with_color with default color."""
        from codomyrmex.utils.cli_helpers import print_with_color

        print_with_color("test message")
        captured = capsys.readouterr()

        assert "test message" in captured.out

    def test_print_section(self, capsys):
        """Test print_section."""
        from codomyrmex.utils.cli_helpers import print_section

        print_section("Test Title", separator="=", width=20)
        captured = capsys.readouterr()

        assert "Test Title" in captured.out
        assert "=" in captured.out


if __name__ == "__main__":
    unittest.main()


# From test_coverage_boost.py
class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_defaults(self):
        from codomyrmex.utils.retry import RetryConfig

        cfg = RetryConfig()
        assert cfg.max_attempts == 3
        assert cfg.base_delay == 1.0
        assert cfg.max_delay == 60.0
        assert cfg.jitter is True

    def test_custom_values(self):
        from codomyrmex.utils.retry import RetryConfig

        cfg = RetryConfig(max_attempts=5, base_delay=0.1, jitter=False)
        assert cfg.max_attempts == 5
        assert cfg.jitter is False


# From test_coverage_boost.py
class TestComputeDelay:
    """Tests for _compute_delay helper."""

    def test_exponential_growth(self):
        from codomyrmex.utils.retry import RetryConfig, _compute_delay

        cfg = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)
        assert _compute_delay(0, cfg) == 1.0
        assert _compute_delay(1, cfg) == 2.0
        assert _compute_delay(2, cfg) == 4.0

    def test_max_delay_cap(self):
        from codomyrmex.utils.retry import RetryConfig, _compute_delay

        cfg = RetryConfig(base_delay=1.0, max_delay=5.0, jitter=False)
        assert _compute_delay(10, cfg) == 5.0  # Capped at max_delay

    def test_jitter_varies_output(self):
        from codomyrmex.utils.retry import RetryConfig, _compute_delay

        cfg = RetryConfig(base_delay=1.0, jitter=True)
        delays = {_compute_delay(1, cfg) for _ in range(20)}
        assert len(delays) > 1  # Jitter should produce different values


# From test_coverage_boost.py
class TestAsyncRetry:
    """Tests for the async retry decorator."""

    def test_async_succeeds(self):
        from codomyrmex.utils.retry import async_retry

        @async_retry(max_attempts=2, base_delay=0.001)
        async def succeed():
            return "async_ok"

        result = asyncio.new_event_loop().run_until_complete(succeed())
        assert result == "async_ok"

    def test_async_retries_then_succeeds(self):
        from codomyrmex.utils.retry import async_retry

        call_count = 0

        @async_retry(max_attempts=3, base_delay=0.001, jitter=False)
        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("retry me")
            return "recovered"

        result = asyncio.new_event_loop().run_until_complete(flaky())
        assert result == "recovered"
        assert call_count == 2

    def test_async_raises_after_exhaustion(self):
        from codomyrmex.utils.retry import async_retry

        @async_retry(max_attempts=2, base_delay=0.001, jitter=False)
        async def always_fail():
            raise OSError("async boom")

        with pytest.raises(OSError, match="async boom"):
            asyncio.new_event_loop().run_until_complete(always_fail())


# From test_coverage_boost.py
class TestContentHash:
    """Tests for content_hash function."""

    def test_sha256_default(self):
        from codomyrmex.utils.hashing import content_hash

        expected = hashlib.sha256(b"hello").hexdigest()
        assert content_hash("hello") == expected

    def test_md5_algorithm(self):
        from codomyrmex.utils.hashing import content_hash

        expected = hashlib.md5(b"hello").hexdigest()
        assert content_hash("hello", "md5") == expected

    def test_bytes_input(self):
        from codomyrmex.utils.hashing import content_hash

        expected = hashlib.sha256(b"\x00\x01\x02").hexdigest()
        assert content_hash(b"\x00\x01\x02") == expected


# From test_coverage_boost.py
class TestFileHash:
    """Tests for file_hash function."""

    def test_file_hash_matches_content_hash(self):
        from codomyrmex.utils.hashing import content_hash, file_hash

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            f.flush()
            path = Path(f.name)

        expected = content_hash("test content")
        assert file_hash(path) == expected
        path.unlink()


# From test_coverage_boost.py
class TestDictHash:
    """Tests for dict_hash function."""

    def test_deterministic(self):
        from codomyrmex.utils.hashing import dict_hash

        d = {"b": 2, "a": 1}
        assert dict_hash(d) == dict_hash({"a": 1, "b": 2})

    def test_different_dicts_differ(self):
        from codomyrmex.utils.hashing import dict_hash

        assert dict_hash({"a": 1}) != dict_hash({"a": 2})


# From test_coverage_boost.py
class TestConsistentHash:
    """Tests for ConsistentHash ring."""

    def test_single_node(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["node-a"])
        assert ring.get_node("any-key") == "node-a"

    def test_multiple_nodes(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["a", "b", "c"])
        assert ring.nodes == {"a", "b", "c"}
        node = ring.get_node("test-key")
        assert node in {"a", "b", "c"}

    def test_consistency(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["a", "b", "c"])
        results = [ring.get_node("stable-key") for _ in range(100)]
        assert len(set(results)) == 1  # Same key → same node

    def test_add_remove_node(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash(["a", "b"])
        ring.add_node("c")
        assert "c" in ring.nodes
        ring.remove_node("a")
        assert "a" not in ring.nodes

    def test_empty_ring_raises(self):
        from codomyrmex.utils.hashing import ConsistentHash

        ring = ConsistentHash()
        with pytest.raises(ValueError, match="No nodes"):
            ring.get_node("key")


# From test_coverage_boost.py
class TestFingerprint:
    """Tests for fingerprint function."""

    def test_stable(self):
        from codomyrmex.utils.hashing import fingerprint

        fp1 = fingerprint("a", 1, True)
        fp2 = fingerprint("a", 1, True)
        assert fp1 == fp2

    def test_different_args_differ(self):
        from codomyrmex.utils.hashing import fingerprint

        assert fingerprint("a", 1) != fingerprint("a", 2)
