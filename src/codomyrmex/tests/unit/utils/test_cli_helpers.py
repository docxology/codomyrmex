"""Comprehensive tests for codomyrmex.utils.cli_helpers module.

Tests cover: format_table, format_output, validate_file_path, determine_language_from_file,
ensure_output_directory, ProgressReporter, print_progress_bar, add_common_arguments,
print_section, print_success, print_error, print_warning, print_info, print_with_color,
setup_logging, validate_dry_run, create_dry_run_plan, enhanced_error_context,
handle_common_exceptions, format_result, parse_common_args, load_json_file,
save_json_file, OUTPUT_WIDTH.
"""

import argparse
import json
import time
from pathlib import Path

import pytest

from codomyrmex.utils.cli_helpers import (
    OUTPUT_WIDTH,
    ProgressReporter,
    add_common_arguments,
    create_dry_run_plan,
    determine_language_from_file,
    enhanced_error_context,
    ensure_output_directory,
    format_output,
    format_result,
    format_table,
    handle_common_exceptions,
    load_json_file,
    parse_common_args,
    print_error,
    print_info,
    print_progress_bar,
    print_section,
    print_success,
    print_warning,
    print_with_color,
    save_json_file,
    setup_logging,
    validate_dry_run,
    validate_file_path,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestOutputWidth:
    """Tests for the OUTPUT_WIDTH module-level constant."""

    def test_output_width_is_int(self):
        assert isinstance(OUTPUT_WIDTH, int)

    def test_output_width_value(self):
        assert OUTPUT_WIDTH == 80


# ---------------------------------------------------------------------------
# format_table
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFormatTable:
    """Comprehensive tests for format_table."""

    def test_empty_data_returns_no_data_message(self):
        result = format_table([], ["a", "b"])
        assert result == "No data to display"

    def test_single_row_single_column(self):
        data = [{"name": "Alice"}]
        result = format_table(data, ["name"])
        lines = result.split("\n")
        assert len(lines) == 3  # header, separator, 1 row
        assert "Alice" in lines[2]
        assert "name" in lines[0]

    def test_multiple_rows_column_alignment(self):
        data = [
            {"name": "Al", "score": "100"},
            {"name": "Elizabeth", "score": "5"},
        ]
        result = format_table(data, ["name", "score"])
        lines = result.split("\n")
        # All data lines should have same length as header
        assert len(lines[0]) == len(lines[2])
        assert len(lines[0]) == len(lines[3])

    def test_separator_line_matches_header_width(self):
        data = [{"x": "1"}]
        result = format_table(data, ["x"])
        lines = result.split("\n")
        assert len(lines[1]) == len(lines[0])
        assert set(lines[1]) == {"-"}

    def test_missing_key_in_row_renders_empty(self):
        data = [{"a": "hello"}]
        result = format_table(data, ["a", "b"])
        lines = result.split("\n")
        # The data row should still contain the "a" value
        assert "hello" in lines[2]

    def test_column_width_determined_by_longest_value(self):
        data = [
            {"col": "short"},
            {"col": "a very long value here"},
        ]
        result = format_table(data, ["col"])
        lines = result.split("\n")
        # The header line length (with ljust padding) should accommodate the longest value
        # ljust pads the header "col" to match the longest data value width
        assert len(lines[0]) >= len("a very long value here")

    @pytest.mark.parametrize("headers", [
        ["single"],
        ["a", "b", "c", "d", "e"],
    ])
    def test_varying_header_counts(self, headers):
        data = [{h: f"val_{h}" for h in headers}]
        result = format_table(data, headers)
        for h in headers:
            assert h in result
            assert f"val_{h}" in result

    def test_pipe_separators_between_columns(self):
        data = [{"a": "1", "b": "2"}]
        result = format_table(data, ["a", "b"])
        assert " | " in result.split("\n")[0]


# ---------------------------------------------------------------------------
# format_output
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFormatOutput:
    """Comprehensive tests for format_output."""

    def test_json_dict(self):
        data = {"key": "value"}
        result = format_output(data, format_type="json")
        parsed = json.loads(result)
        assert parsed == data

    def test_json_list(self):
        data = [1, 2, 3]
        result = format_output(data, format_type="json")
        parsed = json.loads(result)
        assert parsed == data

    def test_json_non_dict_non_list_wraps_in_result(self):
        result = format_output(42, format_type="json")
        parsed = json.loads(result)
        assert parsed == {"result": "42"}

    def test_json_string_wraps_in_result(self):
        result = format_output("hello", format_type="json")
        parsed = json.loads(result)
        assert parsed == {"result": "hello"}

    def test_text_format_returns_str(self):
        data = {"key": "value"}
        result = format_output(data, format_type="text")
        assert result == str(data)

    def test_json_indent_parameter(self):
        data = {"a": 1}
        result_2 = format_output(data, format_type="json", indent=2)
        result_4 = format_output(data, format_type="json", indent=4)
        # 4-indent should be longer due to more whitespace
        assert len(result_4) > len(result_2)

    def test_json_nested_dict(self):
        data = {"outer": {"inner": "value"}}
        result = format_output(data, format_type="json")
        parsed = json.loads(result)
        assert parsed["outer"]["inner"] == "value"


# ---------------------------------------------------------------------------
# validate_file_path
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestValidateFilePath:
    """Comprehensive tests for validate_file_path."""

    def test_existing_file(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("content")
        result = validate_file_path(f, must_exist=True, must_be_file=True)
        assert result == f.resolve()

    def test_existing_directory(self, tmp_path):
        result = validate_file_path(tmp_path, must_exist=True, must_be_dir=True)
        assert result == tmp_path.resolve()

    def test_must_exist_raises_file_not_found(self, tmp_path):
        missing = tmp_path / "nope.txt"
        with pytest.raises(FileNotFoundError):
            validate_file_path(missing, must_exist=True)

    def test_must_be_file_raises_for_directory(self, tmp_path):
        with pytest.raises(ValueError, match="not a file"):
            validate_file_path(tmp_path, must_exist=True, must_be_file=True)

    def test_must_be_dir_raises_for_file(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        with pytest.raises(ValueError, match="not a directory"):
            validate_file_path(f, must_exist=True, must_be_dir=True)

    def test_must_exist_false_returns_resolved_path(self, tmp_path):
        nonexistent = tmp_path / "future.txt"
        result = validate_file_path(nonexistent, must_exist=False)
        assert result == nonexistent.resolve()

    def test_string_path_input(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = validate_file_path(str(f), must_exist=True)
        assert isinstance(result, Path)


# ---------------------------------------------------------------------------
# determine_language_from_file
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDetermineLanguageFromFile:
    """Comprehensive tests for determine_language_from_file."""

    @pytest.mark.parametrize("filename,expected", [
        ("main.py", "python"),
        ("app.js", "javascript"),
        ("index.ts", "typescript"),
        ("server.go", "go"),
        ("lib.rs", "rust"),
        ("App.java", "java"),
        ("solver.cpp", "cpp"),
        ("utils.c", "c"),
        ("script.rb", "ruby"),
        ("handler.php", "php"),
        ("ViewController.swift", "swift"),
        ("Main.kt", "kotlin"),
        ("Service.scala", "scala"),
    ])
    def test_known_extensions(self, filename, expected):
        assert determine_language_from_file(filename) == expected

    def test_unknown_extension_defaults_to_python(self):
        assert determine_language_from_file("data.xyz") == "python"

    def test_no_extension_defaults_to_python(self):
        assert determine_language_from_file("Makefile") == "python"

    def test_path_object_input(self):
        result = determine_language_from_file(Path("src/main.rs"))
        assert result == "rust"

    def test_deeply_nested_path(self):
        result = determine_language_from_file("/a/b/c/d/test.ts")
        assert result == "typescript"


# ---------------------------------------------------------------------------
# ensure_output_directory
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEnsureOutputDirectory:
    """Tests for ensure_output_directory."""

    def test_creates_parent_directories(self, tmp_path):
        target = tmp_path / "a" / "b" / "c" / "output.json"
        result = ensure_output_directory(target)
        assert result.parent.exists()
        assert result == target.resolve()

    def test_existing_directory_is_fine(self, tmp_path):
        target = tmp_path / "output.txt"
        result = ensure_output_directory(target)
        assert result.parent.exists()

    def test_returns_resolved_path(self, tmp_path):
        target = tmp_path / "file.txt"
        result = ensure_output_directory(target)
        assert result.is_absolute()


# ---------------------------------------------------------------------------
# ProgressReporter
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestProgressReporter:
    """Comprehensive tests for ProgressReporter."""

    def test_init_defaults(self):
        pr = ProgressReporter()
        assert pr.total == 100
        assert pr.prefix == "Progress"
        assert pr.suffix == "Complete"
        assert pr.current == 0

    def test_init_custom_values(self):
        pr = ProgressReporter(total=50, prefix="Loading", suffix="Done")
        assert pr.total == 50
        assert pr.prefix == "Loading"
        assert pr.suffix == "Done"

    def test_update_increments_current(self):
        pr = ProgressReporter(total=100)
        pr.update(10)
        assert pr.current == 10

    def test_update_caps_at_total(self):
        pr = ProgressReporter(total=10)
        pr.update(20)
        assert pr.current == 10

    def test_set_current_sets_value(self):
        pr = ProgressReporter(total=100)
        pr.set_current(42)
        assert pr.current == 42

    def test_complete_sets_current_to_total(self):
        pr = ProgressReporter(total=200)
        pr.complete()
        assert pr.current == 200

    def test_start_time_is_set(self):
        before = time.time()
        pr = ProgressReporter()
        after = time.time()
        assert before <= pr.start_time <= after

    def test_multiple_updates_accumulate(self):
        pr = ProgressReporter(total=100)
        # Force last_update to 0 so throttle doesn't eat updates
        pr.update(5)
        pr.update(5)
        pr.update(5)
        assert pr.current == 15


# ---------------------------------------------------------------------------
# print_progress_bar
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPrintProgressBar:
    """Tests for the standalone print_progress_bar function."""

    def test_zero_progress(self, capsys):
        print_progress_bar(0, 100, prefix="Test")
        captured = capsys.readouterr()
        assert "Test" in captured.out
        assert "0%" in captured.out

    def test_complete_progress(self, capsys):
        print_progress_bar(100, 100, prefix="Done")
        captured = capsys.readouterr()
        assert "100%" in captured.out

    def test_partial_progress(self, capsys):
        print_progress_bar(50, 100)
        captured = capsys.readouterr()
        assert "50%" in captured.out

    def test_zero_total_does_not_raise(self):
        """print_progress_bar handles total=0 without ZeroDivisionError."""
        print_progress_bar(0, 0)


# ---------------------------------------------------------------------------
# add_common_arguments
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddCommonArguments:
    """Comprehensive tests for add_common_arguments."""

    def test_dry_run_flag(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_dry_run_default_false(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args([])
        assert args.dry_run is False

    def test_format_json(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["--format", "json"])
        assert args.format == "json"

    def test_format_text(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["--format", "text"])
        assert args.format == "text"

    def test_format_default_is_text(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args([])
        assert args.format == "text"

    def test_format_invalid_choice_raises(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        with pytest.raises(SystemExit):
            parser.parse_args(["--format", "xml"])

    def test_verbose_short_flag(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["-v"])
        assert args.verbose is True

    def test_verbose_long_flag(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["--verbose"])
        assert args.verbose is True

    def test_quiet_short_flag(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["-q"])
        assert args.quiet is True

    def test_quiet_long_flag(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["--quiet"])
        assert args.quiet is True

    def test_all_flags_combined(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["--dry-run", "--format", "json", "-v", "-q"])
        assert args.dry_run is True
        assert args.format == "json"
        assert args.verbose is True
        assert args.quiet is True


# ---------------------------------------------------------------------------
# print_section
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPrintSection:
    """Tests for print_section."""

    def test_basic_section(self, capsys):
        print_section("Title")
        out = capsys.readouterr().out
        assert "Title" in out
        # Default separator is '-' repeated OUTPUT_WIDTH times
        assert "-" * OUTPUT_WIDTH in out

    def test_custom_separator(self, capsys):
        print_section("Header", separator="=", width=20)
        out = capsys.readouterr().out
        assert "=" * 20 in out

    def test_with_prefix(self, capsys):
        print_section("Section", prefix=">>")
        out = capsys.readouterr().out
        assert ">> Section" in out

    def test_without_prefix(self, capsys):
        print_section("Section")
        out = capsys.readouterr().out
        lines = out.strip().split("\n")
        assert lines[0] == "Section"


# ---------------------------------------------------------------------------
# print_success, print_error, print_warning, print_info
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPrintSuccessErrorWarningInfo:
    """Tests for print_success, print_error, print_warning, print_info."""

    def test_print_success_basic(self, capsys):
        print_success("Done")
        out = capsys.readouterr().out
        assert "Done" in out

    def test_print_success_with_context(self, capsys):
        print_success("Done", context="step 3")
        out = capsys.readouterr().out
        assert "Done" in out
        assert "step 3" in out

    def test_print_error_basic(self, capsys):
        print_error("Oops")
        out = capsys.readouterr().out
        assert "Oops" in out

    def test_print_error_with_context(self, capsys):
        print_error("Oops", context="db connection")
        out = capsys.readouterr().out
        assert "Oops" in out
        assert "db connection" in out

    def test_print_error_with_exception(self, capsys):
        exc = ValueError("bad value")
        print_error("Failed", exception=exc)
        out = capsys.readouterr().out
        assert "Failed" in out
        assert "bad value" in out

    def test_print_error_with_all_params(self, capsys):
        exc = RuntimeError("timeout")
        print_error("Request failed", context="API call", exception=exc)
        out = capsys.readouterr().out
        assert "Request failed" in out
        assert "API call" in out
        assert "timeout" in out

    def test_print_warning_basic(self, capsys):
        print_warning("Watch out")
        out = capsys.readouterr().out
        assert "Watch out" in out

    def test_print_warning_with_context(self, capsys):
        print_warning("Slow", context="query time")
        out = capsys.readouterr().out
        assert "Slow" in out
        assert "query time" in out

    def test_print_info_basic(self, capsys):
        print_info("FYI something happened")
        out = capsys.readouterr().out
        assert "FYI something happened" in out


# ---------------------------------------------------------------------------
# print_with_color
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPrintWithColor:
    """Tests for print_with_color (non-TTY path -- pytest captures stdout)."""

    def test_default_color_outputs_plain_text(self, capsys):
        # In pytest, stdout is not a TTY, so color codes are NOT added
        print_with_color("hello world")
        out = capsys.readouterr().out
        assert "hello world" in out
        # No ANSI escape codes in non-TTY
        assert "\033[" not in out

    def test_red_color_non_tty_outputs_plain(self, capsys):
        print_with_color("error msg", color="red")
        out = capsys.readouterr().out
        assert "error msg" in out
        assert "\033[" not in out

    @pytest.mark.parametrize("color", ["red", "green", "yellow", "blue", "default"])
    def test_all_color_names_non_tty(self, capsys, color):
        print_with_color(f"msg_{color}", color=color)
        out = capsys.readouterr().out
        assert f"msg_{color}" in out


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSetupLogging:
    """Tests for setup_logging."""

    def test_setup_logging_default(self):
        import logging
        setup_logging()
        assert len(logging.getLogger().handlers) > 0

    def test_setup_logging_quiet(self):
        import logging
        setup_logging(quiet=True)
        assert len(logging.getLogger().handlers) > 0

    def test_setup_logging_debug_level(self):
        import logging
        setup_logging(level="DEBUG")
        assert len(logging.getLogger().handlers) > 0

    def test_setup_logging_case_insensitive(self):
        import logging
        # The code calls level.upper(), so lowercase should work
        setup_logging(level="warning")
        assert len(logging.getLogger().handlers) > 0


# ---------------------------------------------------------------------------
# validate_dry_run
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestValidateDryRun:
    """Tests for validate_dry_run."""

    def test_returns_true_when_no_dry_run_attr(self):
        args = argparse.Namespace()
        assert validate_dry_run(args) is True

    def test_returns_true_when_dry_run_false(self):
        args = argparse.Namespace(dry_run=False)
        assert validate_dry_run(args) is True

    def test_returns_true_when_dry_run_true(self, capsys):
        args = argparse.Namespace(dry_run=True)
        result = validate_dry_run(args)
        assert result is True
        out = capsys.readouterr().out
        assert "DRY RUN MODE" in out


# ---------------------------------------------------------------------------
# create_dry_run_plan
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCreateDryRunPlan:
    """Tests for create_dry_run_plan."""

    def test_empty_operations(self):
        args = argparse.Namespace()
        result = create_dry_run_plan(args, [])
        assert "EXECUTION PLAN (DRY RUN)" in result
        assert "No actual changes" in result

    def test_single_operation_with_description(self):
        args = argparse.Namespace()
        ops = [{"description": "Install package"}]
        result = create_dry_run_plan(args, ops)
        assert "1. Install package" in result

    def test_operation_with_details_and_target(self):
        args = argparse.Namespace()
        ops = [
            {
                "description": "Deploy service",
                "details": "Blue-green deployment",
                "target": "production",
            }
        ]
        result = create_dry_run_plan(args, ops)
        assert "Deploy service" in result
        assert "Blue-green deployment" in result
        assert "production" in result

    def test_multiple_operations_numbered(self):
        args = argparse.Namespace()
        ops = [
            {"description": "Step one"},
            {"description": "Step two"},
            {"description": "Step three"},
        ]
        result = create_dry_run_plan(args, ops)
        assert "1. Step one" in result
        assert "2. Step two" in result
        assert "3. Step three" in result

    def test_operation_missing_description_uses_unknown(self):
        args = argparse.Namespace()
        ops = [{"target": "/tmp"}]
        result = create_dry_run_plan(args, ops)
        assert "Unknown operation" in result


# ---------------------------------------------------------------------------
# enhanced_error_context
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEnhancedErrorContext:
    """Tests for enhanced_error_context context manager.

    Verifies that enhanced_error_context wraps LogContext correctly
    and enhances exceptions with operation and correlation ID metadata.
    """

    def test_no_exception_completes_cleanly(self):
        """Context manager does not raise when body succeeds."""
        with enhanced_error_context("test_op"):
            pass  # Should complete without error

    def test_exception_is_enhanced_with_operation_and_correlation(self):
        """Exceptions raised inside are enhanced with operation context."""
        with pytest.raises(ValueError) as exc_info:
            with enhanced_error_context("db_query"):
                raise ValueError("connection lost")
        msg = str(exc_info.value)
        assert "Operation: db_query" in msg
        assert "Correlation ID: op_" in msg

    def test_exception_chain_preserved(self):
        """Original exception is preserved as __cause__."""
        with pytest.raises(RuntimeError) as exc_info:
            with enhanced_error_context("parse"):
                raise RuntimeError("bad input")
        assert exc_info.value.__cause__ is not None

    def test_additional_context_completes_cleanly(self):
        """Context with extra dict does not raise when body succeeds."""
        with enhanced_error_context("op", context={"user": "admin"}):
            pass  # Should complete without error


# ---------------------------------------------------------------------------
# handle_common_exceptions
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleCommonExceptions:
    """Tests for handle_common_exceptions decorator."""

    def test_successful_function_returns_result(self):
        @handle_common_exceptions("test_op")
        def good_fn():
            return 42

        assert good_fn() == 42

    def test_file_not_found_returns_false(self):
        @handle_common_exceptions("file_op")
        def bad_fn():
            raise FileNotFoundError("missing.txt")

        assert bad_fn() is False

    def test_permission_error_returns_false(self):
        @handle_common_exceptions("perm_op")
        def bad_fn():
            raise PermissionError("access denied")

        assert bad_fn() is False

    def test_json_decode_error_returns_false(self):
        @handle_common_exceptions("json_op")
        def bad_fn():
            raise json.JSONDecodeError("bad json", "", 0)

        assert bad_fn() is False

    def test_generic_exception_returns_false(self):
        @handle_common_exceptions("generic_op")
        def bad_fn():
            raise RuntimeError("something broke")

        assert bad_fn() is False

    def test_context_parameter(self, capsys):
        @handle_common_exceptions("ctx_op", context="module_x")
        def bad_fn():
            raise FileNotFoundError("gone")

        bad_fn()
        out = capsys.readouterr().out
        assert "module_x" in out

    def test_verbose_mode(self):
        @handle_common_exceptions("verbose_op", verbose=True)
        def bad_fn():
            raise ValueError("detailed error")

        # Should not raise, returns False
        assert bad_fn() is False

    def test_passes_arguments_through(self):
        @handle_common_exceptions("arg_op")
        def add_fn(a, b):
            return a + b

        assert add_fn(3, 4) == 7

    def test_passes_kwargs_through(self):
        @handle_common_exceptions("kwarg_op")
        def greet(name="World"):
            return f"Hello {name}"

        assert greet(name="Alice") == "Hello Alice"


# ---------------------------------------------------------------------------
# format_result
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFormatResult:
    """Comprehensive tests for format_result."""

    def test_dict_success_true(self):
        success, msg = format_result({"success": True})
        assert success is True
        assert msg is None

    def test_dict_success_false(self):
        success, msg = format_result({"success": False})
        assert success is False

    def test_dict_with_output_key(self):
        success, msg = format_result(
            {"success": True, "output": "data here"},
            output_key="output",
        )
        assert success is True
        assert msg == "data here"

    def test_dict_custom_success_key(self):
        success, msg = format_result({"ok": True}, success_key="ok")
        assert success is True

    def test_dict_missing_success_key_defaults_false(self):
        success, msg = format_result({"data": "x"})
        assert success is False

    def test_bool_true(self):
        success, msg = format_result(True)
        assert success is True
        assert msg is None

    def test_bool_false(self):
        success, msg = format_result(False)
        assert success is False
        assert msg is None

    def test_truthy_non_dict_non_bool(self):
        success, msg = format_result("nonempty")
        assert success is True
        assert msg == "nonempty"

    def test_falsy_non_dict_non_bool(self):
        success, msg = format_result(0)
        assert success is False
        assert msg is None

    def test_none_value(self):
        success, msg = format_result(None)
        assert success is False
        assert msg is None


# ---------------------------------------------------------------------------
# parse_common_args
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParseCommonArgs:
    """Tests for parse_common_args."""

    def test_extracts_verbose(self):
        args = argparse.Namespace(verbose=True)
        result = parse_common_args(args)
        assert result["verbose"] is True

    def test_extracts_output(self):
        args = argparse.Namespace(output="/tmp/out.json")
        result = parse_common_args(args)
        assert result["output"] == "/tmp/out.json"

    def test_extracts_dry_run(self):
        args = argparse.Namespace(dry_run=True)
        result = parse_common_args(args)
        assert result["dry_run"] is True

    def test_missing_attrs_excluded(self):
        args = argparse.Namespace()
        result = parse_common_args(args)
        assert result == {}

    def test_all_common_attrs(self):
        args = argparse.Namespace(verbose=False, output="out.txt", dry_run=True)
        result = parse_common_args(args)
        assert len(result) == 3
        assert result["verbose"] is False
        assert result["output"] == "out.txt"
        assert result["dry_run"] is True


# ---------------------------------------------------------------------------
# load_json_file / save_json_file
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLoadSaveJsonFile:
    """Tests for load_json_file and save_json_file."""

    def test_save_and_load_roundtrip(self, tmp_path):
        data = {"name": "test", "values": [1, 2, 3]}
        out = tmp_path / "data.json"
        save_json_file(data, out)
        loaded = load_json_file(out)
        assert loaded == data

    def test_save_creates_parent_dirs(self, tmp_path):
        data = {"x": 1}
        out = tmp_path / "a" / "b" / "c.json"
        save_json_file(data, out, create_parents=True)
        assert out.exists()

    def test_load_nonexistent_file_raises(self, tmp_path):
        missing = tmp_path / "nope.json"
        with pytest.raises(FileNotFoundError):
            load_json_file(missing)

    def test_load_invalid_json_raises(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not valid json {{{")
        with pytest.raises(json.JSONDecodeError):
            load_json_file(bad)

    def test_save_returns_path(self, tmp_path):
        out = tmp_path / "result.json"
        returned = save_json_file({"a": 1}, out)
        assert returned == out.resolve()

    def test_save_custom_indent(self, tmp_path):
        out = tmp_path / "indented.json"
        save_json_file({"a": 1}, out, indent=4)
        content = out.read_text()
        # 4-space indent should have "    " before "a"
        assert '    "a"' in content

    def test_save_unicode_data(self, tmp_path):
        data = {"greeting": "Bonjour le monde"}
        out = tmp_path / "unicode.json"
        save_json_file(data, out)
        loaded = load_json_file(out)
        assert loaded["greeting"] == "Bonjour le monde"


# ---------------------------------------------------------------------------
# Integration-style: combinations
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCLIHelpersIntegration:
    """Integration-style tests combining multiple cli_helpers functions."""

    def test_format_table_then_format_output_json(self):
        data = [{"module": "agents", "status": "ok"}]
        table_str = format_table(data, ["module", "status"])
        result = format_output({"table": table_str}, format_type="json")
        parsed = json.loads(result)
        assert "agents" in parsed["table"]

    def test_add_args_then_parse_common(self):
        parser = argparse.ArgumentParser()
        add_common_arguments(parser)
        args = parser.parse_args(["--dry-run", "-v", "--format", "json"])
        common = parse_common_args(args)
        assert common["verbose"] is True
        assert common["dry_run"] is True

    def test_save_load_then_format(self, tmp_path):
        data = {"status": "healthy", "modules": 89}
        path = tmp_path / "status.json"
        save_json_file(data, path)
        loaded = load_json_file(path)
        formatted = format_output(loaded, format_type="json")
        parsed = json.loads(formatted)
        assert parsed["modules"] == 89
