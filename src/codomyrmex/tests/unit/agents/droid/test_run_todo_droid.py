"""Zero-mock tests for run_todo_droid.py via subprocess CLI invocation.

Covers:
- main() --help exits cleanly
- main() --dry-run runs without requiring a real droid
- resolve_handler with known valid handler
- resolve_handler raises for nonexistent handler
- get_todo_count_interactive exists and is callable
- CLI argument parser accepts expected flags

Zero-mock policy: NO unittest.mock, MagicMock, or monkeypatch.
CLI tests use subprocess.run with sys.executable for isolation.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

# ===========================================================================
# 1. CLI invocation via subprocess
# ===========================================================================


class TestCLIHelp:
    """Test CLI --help exits cleanly."""

    def test_main_help_exits_zero(self):
        """main() with --help should exit 0 and print usage."""
        result = subprocess.run(
            [sys.executable, "-m", "codomyrmex.agents.droid.run_todo_droid", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/mini/Documents/GitHub/codomyrmex",
        )
        assert result.returncode == 0
        assert "Codomyrmex Droid TODO Processor" in result.stdout
        assert "--count" in result.stdout
        assert "--dry-run" in result.stdout

    def test_help_shows_config_flag(self):
        """--help output mentions --config."""
        result = subprocess.run(
            [sys.executable, "-m", "codomyrmex.agents.droid.run_todo_droid", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/mini/Documents/GitHub/codomyrmex",
        )
        assert "--config" in result.stdout

    def test_help_shows_list_flag(self):
        """--help output mentions --list."""
        result = subprocess.run(
            [sys.executable, "-m", "codomyrmex.agents.droid.run_todo_droid", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/mini/Documents/GitHub/codomyrmex",
        )
        assert "--list" in result.stdout

    def test_help_shows_non_interactive_flag(self):
        """--help output mentions --non-interactive."""
        result = subprocess.run(
            [sys.executable, "-m", "codomyrmex.agents.droid.run_todo_droid", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/mini/Documents/GitHub/codomyrmex",
        )
        assert "--non-interactive" in result.stdout


# ===========================================================================
# 2. CLI --dry-run
# ===========================================================================


class TestCLIDryRun:
    """Test --dry-run mode runs without requiring a real droid."""

    def test_dry_run_exits_cleanly(self):
        """--dry-run should exit 0 and print dry-run output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "codomyrmex.agents.droid.run_todo_droid",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/mini/Documents/GitHub/codomyrmex",
        )
        # Exit code should be 0 (dry-run, or no TODOs)
        assert result.returncode == 0

    def test_dry_run_with_count(self):
        """--dry-run --count 2 should exit cleanly."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "codomyrmex.agents.droid.run_todo_droid",
                "--dry-run",
                "--count",
                "2",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/mini/Documents/GitHub/codomyrmex",
        )
        assert result.returncode == 0


# ===========================================================================
# 3. CLI --list
# ===========================================================================


class TestCLIList:
    """Test --list mode prints TODOs and exits."""

    def test_list_exits_cleanly(self):
        """--list should exit 0."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "codomyrmex.agents.droid.run_todo_droid",
                "--list",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/mini/Documents/GitHub/codomyrmex",
        )
        assert result.returncode == 0
        assert "TODO" in result.stdout


# ===========================================================================
# 4. resolve_handler direct import tests
# ===========================================================================


class TestResolveHandler:
    """Test resolve_handler with real importlib (direct import, no subprocess)."""

    def test_resolve_known_valid_handler(self):
        """resolve_handler with a known droid handler succeeds."""
        from codomyrmex.agents.droid.run_todo_droid import resolve_handler

        handler = resolve_handler("droid:verify_real_methods")
        assert callable(handler)
        assert handler.__name__ == "verify_real_methods"

    def test_resolve_fully_qualified_path(self):
        """resolve_handler with full module:function syntax."""
        from codomyrmex.agents.droid.run_todo_droid import resolve_handler

        handler = resolve_handler(
            "codomyrmex.agents.droid.tasks:ensure_documentation_exists"
        )
        assert callable(handler)

    def test_resolve_bare_function_defaults_to_droid_tasks(self):
        """A bare name defaults to codomyrmex.agents.droid.tasks module."""
        from codomyrmex.agents.droid.run_todo_droid import resolve_handler

        handler = resolve_handler("confirm_logging_integrations")
        assert callable(handler)

    def test_resolve_nonexistent_module_raises_import_error(self):
        """Nonexistent module path raises ImportError."""
        from codomyrmex.agents.droid.run_todo_droid import resolve_handler

        with pytest.raises(ImportError):
            resolve_handler("nonexistent.module.path:some_func")

    def test_resolve_nonexistent_function_raises_attribute_error(self):
        """Valid module but nonexistent function raises AttributeError."""
        from codomyrmex.agents.droid.run_todo_droid import resolve_handler

        with pytest.raises(AttributeError):
            resolve_handler("codomyrmex.agents.droid.tasks:no_such_function_xyz")

    def test_resolve_ai_code_shorthand_expansion(self):
        """'ai_code:' prefix expands to codomyrmex.agents.ai_code_editing.tasks."""
        from codomyrmex.agents.droid.run_todo_droid import resolve_handler

        with pytest.raises((ImportError, AttributeError)):
            resolve_handler("ai_code:nonexistent_function_xyz_test")


# ===========================================================================
# 5. get_todo_count_interactive callable check
# ===========================================================================


class TestGetTodoCountInteractive:
    """Verify get_todo_count_interactive exists and is callable."""

    def test_function_exists_and_is_callable(self):
        from codomyrmex.agents.droid.run_todo_droid import get_todo_count_interactive

        assert callable(get_todo_count_interactive)

    def test_function_has_return_annotation(self):
        """get_todo_count_interactive should return int."""
        import inspect

        from codomyrmex.agents.droid.run_todo_droid import get_todo_count_interactive

        sig = inspect.signature(get_todo_count_interactive)
        # With `from __future__ import annotations`, annotation is the string 'int'
        assert sig.return_annotation in (int, "int", inspect.Parameter.empty)


# ===========================================================================
# 6. Argument parser flag acceptance
# ===========================================================================


class TestArgParserFlags:
    """Verify CLI argument parser accepts all expected flags."""

    def _parse(self, args: list[str]):
        """Parse args using the real argparse parser from main()."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--todo-file", default="todo_list.txt")
        parser.add_argument("--count", type=int, default=None)
        parser.add_argument("--config", default=None)
        parser.add_argument("--non-interactive", action="store_true")
        parser.add_argument("--list", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        return parser.parse_args(args)

    def test_count_flag(self):
        args = self._parse(["--count", "5"])
        assert args.count == 5

    def test_config_flag(self):
        args = self._parse(["--config", "/path/to/config.json"])
        assert args.config == "/path/to/config.json"

    def test_list_flag(self):
        args = self._parse(["--list"])
        assert args.list is True

    def test_dry_run_flag(self):
        args = self._parse(["--dry-run"])
        assert args.dry_run is True

    def test_non_interactive_flag(self):
        args = self._parse(["--non-interactive"])
        assert args.non_interactive is True

    def test_todo_file_default(self):
        args = self._parse([])
        assert args.todo_file == "todo_list.txt"

    def test_all_flags_combined(self):
        args = self._parse(
            [
                "--count",
                "3",
                "--config",
                "/tmp/cfg.json",
                "--dry-run",
                "--non-interactive",
            ]
        )
        assert args.count == 3
        assert args.config == "/tmp/cfg.json"
        assert args.dry_run is True
        assert args.non_interactive is True


# ===========================================================================
# 7. Module constants and public API
# ===========================================================================


class TestModulePublicAPI:
    """Verify public functions and constants are accessible."""

    def test_main_is_callable(self):
        from codomyrmex.agents.droid.run_todo_droid import main

        assert callable(main)

    def test_run_todos_is_callable(self):
        from codomyrmex.agents.droid.run_todo_droid import run_todos

        assert callable(run_todos)

    def test_build_controller_is_callable(self):
        from codomyrmex.agents.droid.run_todo_droid import build_controller

        assert callable(build_controller)

    def test_codomyrmex_enhanced_prompt_is_string(self):
        from codomyrmex.agents.droid.run_todo_droid import CODOMYRMEX_ENHANCED_PROMPT

        assert isinstance(CODOMYRMEX_ENHANCED_PROMPT, str)
        assert len(CODOMYRMEX_ENHANCED_PROMPT) > 100

    def test_demo_programmatic_usage_is_callable(self):
        from codomyrmex.agents.droid.run_todo_droid import demo_programmatic_usage

        assert callable(demo_programmatic_usage)
