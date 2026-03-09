"""Comprehensive tests for utils.cli_helpers — zero-mock.

Covers: ProgressReporter, format_table, format_output, validate_file_path,
load_json_file, print_with_color, setup_logging, add_common_arguments.
Uses real temp files for I/O tests.
"""

import argparse
import json
import tempfile

import pytest

from codomyrmex.utils.cli_helpers import (
    ProgressReporter,
    add_common_arguments,
    format_output,
    format_table,
    load_json_file,
    print_with_color,
    setup_logging,
    validate_file_path,
)


class TestProgressReporter:
    def test_init(self):
        pr = ProgressReporter(total=50, prefix="Testing")
        assert pr is not None

    def test_update(self):
        pr = ProgressReporter(total=10)
        pr.update(5)
        assert pr.current == 5

    def test_set_current(self):
        pr = ProgressReporter(total=10)
        pr.set_current(7)
        assert pr.current == 7

    def test_complete(self):
        pr = ProgressReporter(total=10)
        pr.complete()
        assert pr.current == pr.total


class TestFormatTable:
    def test_simple_table(self):
        data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        result = format_table(data, headers=["name", "age"])
        assert isinstance(result, str)
        assert "Alice" in result

    def test_empty_data(self):
        result = format_table([], headers=["col1"])
        assert isinstance(result, str)


class TestFormatOutput:
    def test_json_format(self):
        data = {"key": "value", "count": 42}
        result = format_output(data, format_type="json")
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_text_format(self):
        result = format_output({"key": "value"}, format_type="text")
        assert isinstance(result, str)


class TestValidateFilePath:
    def test_existing_file(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as f:
            path = validate_file_path(f.name, must_exist=True, must_be_file=True)
            assert path is not None

    def test_existing_dir(self):
        with tempfile.TemporaryDirectory() as d:
            path = validate_file_path(d, must_exist=True, must_be_dir=True)
            assert path is not None

    def test_nonexistent_raises(self):
        with pytest.raises((FileNotFoundError, ValueError)):
            validate_file_path("/nonexistent/path/xyz123.txt", must_exist=True)


class TestLoadJsonFile:
    def test_load_valid(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"hello": "world"}, f)
            f.flush()
            result = load_json_file(f.name)
            assert result["hello"] == "world"

    def test_load_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            load_json_file("/nonexistent/file.json")


class TestPrintWithColor:
    def test_default_color(self, capsys):
        print_with_color("Hello")
        captured = capsys.readouterr()
        assert "Hello" in captured.out


class TestSetupLogging:
    def test_default(self):
        setup_logging()

    def test_quiet_mode(self):
        setup_logging(quiet=True)


class TestAddCommonArguments:
    def test_adds_args(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args([])
        assert args is not None
