"""Unit tests for core utility functions -- deep merge, retry, path resolution, directory creation, timestamps, and string truncation."""

import argparse
import os
import time
import unittest
from pathlib import Path

import pytest

from codomyrmex.utils import RefinedUtilities


@pytest.mark.unit
class TestRefinedUtilities:
    """Tests for RefinedUtilities class."""

    def test_deep_merge(self):
        """Test deep merging of dictionaries."""
        dict1 = {"a": {"b": 1}}
        dict2 = {"a": {"c": 2}, "d": 3}
        expected = {"a": {"b": 1, "c": 2}, "d": 3}
        result = RefinedUtilities.deep_merge(dict1, dict2)
        assert result == expected

    def test_retry(self):
        """Test retry decorator."""
        count = [0]

        @RefinedUtilities.retry(retries=3, backoff_factor=0.1)
        def failing_func():
            count[0] += 1
            if count[0] < 2:
                raise ValueError("Fail")
            return "success"

        result = failing_func()
        assert result == "success"
        assert count[0] == 2

    def test_resolve_path_absolute(self):
        """Test resolving an absolute path."""
        abs_path = "/tmp/test/path"
        result = RefinedUtilities.resolve_path(abs_path)
        assert result == Path(abs_path)

    def test_resolve_path_relative(self):
        """Test resolving a relative path."""
        rel_path = "relative/path"
        result = RefinedUtilities.resolve_path(rel_path)
        assert result.is_absolute()

    def test_resolve_path_with_base_dir(self):
        """Test resolving a relative path with base directory."""
        rel_path = "subdir/file.txt"
        base_dir = "/base/path"
        result = RefinedUtilities.resolve_path(rel_path, base_dir)
        assert result == Path("/base/path/subdir/file.txt").resolve()


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
