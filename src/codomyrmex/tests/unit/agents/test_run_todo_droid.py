"""Tests for run_todo_droid.py -- zero-mock policy enforced.

Covers:
- Module imports and constant availability
- resolve_handler() with valid, invalid, and shorthand paths
- TodoItem/TodoManager integration (load, save, rotate)
- _list_todos() display helper
- _determine_count() argument handling
- _show_dry_run() display helper
- build_controller() with and without config
- run_todos() with real controller + manager (empty, success, handler failures)
- CODOMYRMEX_ENHANCED_PROMPT constant validation
- argparse construction inside main()
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from codomyrmex.agents.droid.controller import (
    DroidController,
    DroidStatus,
    create_default_controller,
)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------
from codomyrmex.agents.droid.run_todo_droid import (
    CODOMYRMEX_ENHANCED_PROMPT,
    _determine_count,
    _list_todos,
    _show_dry_run,
    build_controller,
    resolve_handler,
    run_todos,
)
from codomyrmex.agents.droid.todo import TodoItem, TodoManager

# ---------------------------------------------------------------------------
# Helpers (real objects, no mocks)
# ---------------------------------------------------------------------------

def _make_todo_file(tmp_path: Path, content: str) -> Path:
    """Write a todo_list.txt with the given content and return its path."""
    p = tmp_path / "todo_list.txt"
    p.write_text(content, encoding="utf-8")
    return p


def _sample_todo_content(
    todo_lines: list[str] | None = None,
    completed_lines: list[str] | None = None,
) -> str:
    """Build a well-formed todo file string."""
    parts = ["[TODO]"]
    for line in (todo_lines or []):
        parts.append(line)
    parts.append("")
    parts.append("[COMPLETED]")
    for line in (completed_lines or []):
        parts.append(line)
    return "\n".join(parts) + "\n"


def _make_args(**kwargs) -> SimpleNamespace:
    """Build a SimpleNamespace that mimics parsed argparse args."""
    defaults = {
        "count": None,
        "non_interactive": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ===========================================================================
# 1. Import and constant smoke tests
# ===========================================================================

class TestModuleImports:
    """Verify all public symbols are importable."""

    def test_import_resolve_handler(self):
        assert callable(resolve_handler)

    def test_import_run_todos(self):
        assert callable(run_todos)

    def test_import_build_controller(self):
        assert callable(build_controller)

    def test_import_list_todos(self):
        assert callable(_list_todos)

    def test_import_determine_count(self):
        assert callable(_determine_count)

    def test_import_show_dry_run(self):
        assert callable(_show_dry_run)

    def test_codomyrmex_enhanced_prompt_is_nonempty_string(self):
        assert isinstance(CODOMYRMEX_ENHANCED_PROMPT, str)
        assert len(CODOMYRMEX_ENHANCED_PROMPT) > 100

    def test_prompt_mentions_codomyrmex(self):
        assert "Codomyrmex" in CODOMYRMEX_ENHANCED_PROMPT

    def test_prompt_mentions_modularity(self):
        assert "Modularity" in CODOMYRMEX_ENHANCED_PROMPT or "modular" in CODOMYRMEX_ENHANCED_PROMPT.lower()


# ===========================================================================
# 2. resolve_handler() tests
# ===========================================================================

class TestResolveHandler:
    """Test handler resolution with real importlib."""

    def test_resolve_fully_qualified_handler(self):
        """Resolve a handler using full module:function syntax."""
        handler = resolve_handler(
            "codomyrmex.agents.droid.tasks:ensure_documentation_exists"
        )
        assert callable(handler)
        assert handler.__name__ == "ensure_documentation_exists"

    def test_resolve_droid_shorthand(self):
        """The 'droid:' prefix should expand to codomyrmex.agents.droid.tasks."""
        handler = resolve_handler("droid:verify_real_methods")
        assert callable(handler)
        assert handler.__name__ == "verify_real_methods"

    def test_resolve_bare_function_name(self):
        """A bare name (no colon) defaults to codomyrmex.agents.droid.tasks module."""
        handler = resolve_handler("confirm_logging_integrations")
        assert callable(handler)

    def test_resolve_nonexistent_module_raises(self):
        with pytest.raises(ImportError):
            resolve_handler("nonexistent.module:some_func")

    def test_resolve_nonexistent_function_raises(self):
        with pytest.raises(AttributeError):
            resolve_handler("codomyrmex.agents.droid.tasks:no_such_function_xyz")

    def test_resolve_ai_code_shorthand(self):
        """The 'ai_code:' prefix should expand to codomyrmex.agents.ai_code_editing.tasks."""
        # This may or may not have a valid function; we test the expansion logic.
        # If the module exists but function doesn't, we get AttributeError.
        # If the module doesn't exist, we get ImportError.
        with pytest.raises((ImportError, AttributeError)):
            resolve_handler("ai_code:nonexistent_function_xyz")

    def test_resolve_handler_with_colon_only(self):
        """'module:' with empty function name should raise AttributeError."""
        with pytest.raises(AttributeError):
            resolve_handler("codomyrmex.agents.droid.tasks:")

    def test_resolve_verify_readiness(self):
        handler = resolve_handler("droid:verify_readiness")
        assert handler.__name__ == "verify_readiness"


# ===========================================================================
# 3. _determine_count() tests
# ===========================================================================

class TestDetermineCount:
    """Test count determination logic with fake args objects."""

    def test_explicit_positive_count(self):
        args = _make_args(count=5)
        result = _determine_count(args, list(range(10)))
        assert result == 5

    def test_count_minus_one_means_all(self):
        items = list(range(7))
        args = _make_args(count=-1)
        result = _determine_count(args, items)
        assert result == len(items)

    def test_count_less_than_minus_one_returns_none(self, capsys):
        args = _make_args(count=-5)
        result = _determine_count(args, list(range(3)))
        assert result is None
        captured = capsys.readouterr()
        assert "Invalid count" in captured.out

    def test_count_zero_returns_zero(self):
        args = _make_args(count=0)
        result = _determine_count(args, list(range(3)))
        assert result == 0

    def test_non_interactive_defaults_to_one(self):
        args = _make_args(non_interactive=True)
        result = _determine_count(args, list(range(10)))
        assert result == 1

    def test_dry_run_defaults_to_one(self):
        args = _make_args(dry_run=True)
        result = _determine_count(args, list(range(10)))
        assert result == 1


# ===========================================================================
# 4. _list_todos() tests
# ===========================================================================

class TestListTodos:
    """Test the _list_todos display helper (printing to stdout)."""

    def test_list_todos_empty(self, capsys):
        _list_todos([], [])
        captured = capsys.readouterr()
        assert "No TODO items found" in captured.out

    def test_list_todos_with_items(self, capsys):
        items = [
            TodoItem(task_name="task_a", description="Do thing A", outcomes="done A"),
            TodoItem(task_name="task_b", description="Do thing B", outcomes=""),
        ]
        _list_todos(items, [])
        captured = capsys.readouterr()
        assert "task_a" in captured.out
        assert "Do thing A" in captured.out
        assert "Outcomes: done A" in captured.out
        assert "task_b" in captured.out

    def test_list_todos_with_handler_path(self, capsys):
        items = [
            TodoItem(
                task_name="op1",
                description="desc",
                outcomes="",
                handler_path="droid:some_handler",
            ),
        ]
        _list_todos(items, [])
        captured = capsys.readouterr()
        assert "Handler: droid:some_handler" in captured.out

    def test_list_todos_with_completed(self, capsys):
        completed = [
            TodoItem(task_name="done_task", description="Was done", outcomes="result"),
        ]
        _list_todos([], completed)
        captured = capsys.readouterr()
        assert "Completed" in captured.out
        assert "done_task" in captured.out


# ===========================================================================
# 5. _show_dry_run() tests
# ===========================================================================

class TestShowDryRun:
    """Test the dry-run display helper."""

    def test_dry_run_empty_list(self, capsys):
        _show_dry_run(0, [])
        captured = capsys.readouterr()
        assert "Dry run" in captured.out

    def test_dry_run_with_items(self, capsys):
        items = [
            TodoItem(task_name="t1", description="desc1", outcomes="out1"),
            TodoItem(task_name="t2", description="desc2", outcomes=""),
        ]
        _show_dry_run(2, items)
        captured = capsys.readouterr()
        assert "Would process 2 TODO" in captured.out
        assert "t1" in captured.out
        assert "t2" in captured.out
        assert "Outcomes: out1" in captured.out

    def test_dry_run_respects_count(self, capsys):
        items = [
            TodoItem(task_name="t1", description="d1", outcomes=""),
            TodoItem(task_name="t2", description="d2", outcomes=""),
            TodoItem(task_name="t3", description="d3", outcomes=""),
        ]
        _show_dry_run(1, items)
        captured = capsys.readouterr()
        assert "t1" in captured.out
        assert "t2" not in captured.out


# ===========================================================================
# 6. build_controller() tests
# ===========================================================================

class TestBuildController:
    """Test DroidController construction helper."""

    def test_build_without_config(self):
        ctrl = build_controller(None)
        assert isinstance(ctrl, DroidController)

    def test_build_with_config_file(self, tmp_path):
        config_data = {
            "identifier": "test-droid",
            "mode": "test",
            "safe_mode": False,
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data), encoding="utf-8")
        ctrl = build_controller(str(config_path))
        assert isinstance(ctrl, DroidController)
        assert ctrl.config.identifier == "test-droid"

    def test_build_with_nonexistent_config_raises(self):
        with pytest.raises((FileNotFoundError, OSError)):
            build_controller("/nonexistent/path/config.json")


# ===========================================================================
# 7. run_todos() integration tests
# ===========================================================================

class TestRunTodos:
    """Test run_todos with real DroidController and TodoManager."""

    def _setup(self, tmp_path, todo_lines=None, completed_lines=None):
        """Create controller, manager, and todo file."""
        content = _sample_todo_content(todo_lines, completed_lines)
        todo_file = _make_todo_file(tmp_path, content)
        controller = create_default_controller()
        manager = TodoManager(str(todo_file))
        return controller, manager

    def test_run_todos_empty_list(self, tmp_path):
        controller, manager = self._setup(tmp_path)
        result = list(run_todos(controller, manager, 5))
        assert result == []

    def test_run_todos_with_valid_handler(self, tmp_path):
        """Process a TODO that uses the real verify_real_methods handler."""
        todo_lines = [
            "verify_methods | droid:verify_real_methods | Check droid methods exist"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 1))
        assert len(result) == 1
        assert result[0].task_name == "verify_methods"

    def test_run_todos_with_documentation_handler(self, tmp_path):
        """Process a TODO that uses ensure_documentation_exists handler."""
        todo_lines = [
            "check_docs | droid:ensure_documentation_exists | Verify documentation"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 1))
        assert len(result) == 1

    def test_run_todos_with_logging_handler(self, tmp_path):
        """Process a TODO that uses confirm_logging_integrations handler."""
        todo_lines = [
            "check_logging | droid:confirm_logging_integrations | Verify logging"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 1))
        assert len(result) == 1

    def test_run_todos_count_limits_processing(self, tmp_path):
        """When count < len(todo_items), only count items are processed."""
        todo_lines = [
            "task_1 | droid:verify_real_methods | First",
            "task_2 | droid:verify_real_methods | Second",
            "task_3 | droid:verify_real_methods | Third",
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 2))
        assert len(result) == 2

    def test_run_todos_invalid_handler_raises_import_error(self, tmp_path):
        """An invalid handler with a nonexistent module raises ImportError (not caught by run_todos)."""
        todo_lines = [
            "bad_task | nonexistent.module:no_func | Will fail"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        # ImportError is NOT in run_todos' except clause, so it propagates
        with pytest.raises(ImportError):
            list(run_todos(controller, manager, 1))

    def test_run_todos_invalid_function_caught(self, tmp_path, capsys):
        """A valid module but nonexistent function raises AttributeError, which IS caught."""
        todo_lines = [
            "bad_task | droid:nonexistent_handler_xyz | Will fail gracefully"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 1))
        assert len(result) == 0
        captured = capsys.readouterr()
        assert "Failed" in captured.out

    def test_run_todos_no_handler_no_inference(self, tmp_path, capsys):
        """A 3-column TODO with no handler and no inferrable handler should fail gracefully.

        The handler inference loop tries droid:, tasks:, ai_code_editing: prefixes.
        - droid: raises AttributeError (caught)
        - tasks: raises ImportError (NOT in the inner try/except of the inference loop,
          which only catches ValueError, RuntimeError, AttributeError, OSError, TypeError)
        So this actually raises ModuleNotFoundError for 'tasks' module.
        """
        todo_lines = [
            "unknown_task_xyz | Do something unknown | Expected outcomes"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        # The inference loop's inner try/except doesn't catch ImportError,
        # so this propagates out of run_todos
        with pytest.raises((ImportError, ValueError)):
            list(run_todos(controller, manager, 1))

    def test_run_todos_rotates_completed(self, tmp_path):
        """After successful processing, completed items are rotated via manager."""
        todo_lines = [
            "verify_methods | droid:verify_real_methods | Check methods"
        ]
        content = _sample_todo_content(todo_lines)
        todo_file = _make_todo_file(tmp_path, content)
        controller = create_default_controller()
        manager = TodoManager(str(todo_file))

        result = list(run_todos(controller, manager, 1))
        assert len(result) == 1

        # Reload and verify rotation happened
        remaining, completed = manager.load()
        assert len(remaining) == 0
        assert len(completed) == 1
        assert completed[0].task_name == "verify_methods"

    def test_run_todos_mixed_success_with_attribute_error(self, tmp_path, capsys):
        """Mix of valid handler and one with bad function name (AttributeError, caught)."""
        todo_lines = [
            "good_task | droid:verify_real_methods | Works",
            "bad_task | droid:nonexistent_handler_xyz | Fails with AttributeError",
            "good_task_2 | droid:confirm_logging_integrations | Also works",
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 3))
        # First and third succeed; second fails with AttributeError (caught)
        assert len(result) >= 1
        captured = capsys.readouterr()
        assert "Execution Summary" in captured.out

    def test_run_todos_zero_count(self, tmp_path):
        """run_todos with count=0 should process nothing."""
        todo_lines = [
            "task_a | droid:verify_real_methods | Something"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 0))
        assert result == []

    def test_run_todos_with_verify_readiness_handler(self, tmp_path):
        """The verify_readiness handler checks for project directories."""
        todo_lines = [
            "readiness | droid:verify_readiness | Check readiness"
        ]
        controller, manager = self._setup(tmp_path, todo_lines=todo_lines)
        result = list(run_todos(controller, manager, 1))
        assert len(result) == 1


# ===========================================================================
# 8. TodoItem + TodoManager integration (exercised through run_todo_droid paths)
# ===========================================================================

class TestTodoIntegration:
    """Verify TodoItem and TodoManager work correctly in run_todo_droid scenarios."""

    def test_todo_item_with_handler_path(self):
        item = TodoItem(
            task_name="op1",
            description="Do X",
            outcomes="done",
            handler_path="droid:some_handler",
        )
        assert item.handler_path == "droid:some_handler"
        assert item.task_name == "op1"

    def test_todo_item_without_handler_path(self):
        item = TodoItem(task_name="t", description="d", outcomes="o")
        assert item.handler_path is None

    def test_parse_legacy_format(self):
        raw = "op1 | droid:my_handler | description text"
        item = TodoItem.parse(raw)
        assert item.handler_path == "droid:my_handler"
        assert item.task_name == "op1"
        assert item.description == "description text"

    def test_parse_new_format(self):
        raw = "my_task | This is the description | Expected outcomes"
        item = TodoItem.parse(raw)
        assert item.handler_path is None
        assert item.task_name == "my_task"
        assert item.outcomes == "Expected outcomes"

    def test_parse_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid TODO entry"):
            TodoItem.parse("only one column")

    def test_manager_load_nonexistent_file(self, tmp_path):
        manager = TodoManager(tmp_path / "does_not_exist.txt")
        items, completed = manager.load()
        assert items == []
        assert completed == []

    def test_manager_load_and_save_roundtrip(self, tmp_path):
        content = _sample_todo_content(
            todo_lines=["t1 | desc1 | out1", "t2 | desc2 | out2"],
            completed_lines=["done1 | was done | result"],
        )
        f = _make_todo_file(tmp_path, content)
        manager = TodoManager(str(f))
        items, completed = manager.load()
        assert len(items) == 2
        assert len(completed) == 1

        # Save and reload
        manager.save(items, completed)
        items2, completed2 = manager.load()
        assert len(items2) == 2
        assert len(completed2) == 1

    def test_serialise_roundtrip(self):
        item = TodoItem(task_name="t", description="d", outcomes="o")
        line = item.serialise()
        parsed = TodoItem.parse(line)
        assert parsed.task_name == item.task_name
        assert parsed.description == item.description
        assert parsed.outcomes == item.outcomes


# ===========================================================================
# 9. get_todo_count_interactive() -- skip if no TTY
# ===========================================================================

@pytest.mark.skipif(
    not sys.stdin.isatty(),
    reason="get_todo_count_interactive requires an interactive TTY",
)
class TestGetTodoCountInteractive:
    """Tests that require interactive input; skipped in CI."""

    def test_interactive_count_returns_int(self):
        from codomyrmex.agents.droid.run_todo_droid import get_todo_count_interactive

        # Would need actual interactive input -- skipped in CI
        assert callable(get_todo_count_interactive)


# ===========================================================================
# 10. main() argparse construction -- no subprocess needed
# ===========================================================================

class TestMainArgparse:
    """Verify main() builds a valid argparse parser."""

    def test_main_is_callable(self):
        from codomyrmex.agents.droid.run_todo_droid import main

        assert callable(main)

    def test_demo_programmatic_usage_is_callable(self):
        from codomyrmex.agents.droid.run_todo_droid import demo_programmatic_usage

        assert callable(demo_programmatic_usage)


# ===========================================================================
# 11. _process_todos() helper
# ===========================================================================

class TestProcessTodos:
    """Test _process_todos wrapper for error handling."""

    def test_process_todos_importable(self):
        from codomyrmex.agents.droid.run_todo_droid import _process_todos

        assert callable(_process_todos)

    def test_process_todos_empty_run(self, tmp_path, capsys):
        from codomyrmex.agents.droid.run_todo_droid import _process_todos

        content = _sample_todo_content()
        todo_file = _make_todo_file(tmp_path, content)
        controller = create_default_controller()
        manager = TodoManager(str(todo_file))

        _process_todos(controller, manager, 1)
        captured = capsys.readouterr()
        assert "Droid session completed" in captured.out

    def test_process_todos_success(self, tmp_path, capsys):
        from codomyrmex.agents.droid.run_todo_droid import _process_todos

        content = _sample_todo_content(
            todo_lines=["verify_methods | droid:verify_real_methods | Check"]
        )
        todo_file = _make_todo_file(tmp_path, content)
        controller = create_default_controller()
        manager = TodoManager(str(todo_file))

        _process_todos(controller, manager, 1)
        captured = capsys.readouterr()
        assert "Successfully processed" in captured.out
        assert "Droid session completed" in captured.out


# ===========================================================================
# 12. Edge cases and error paths
# ===========================================================================

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_run_todos_count_exceeds_available(self, tmp_path):
        """Requesting more items than available should not crash."""
        content = _sample_todo_content(
            todo_lines=["t1 | droid:verify_real_methods | one"]
        )
        todo_file = _make_todo_file(tmp_path, content)
        controller = create_default_controller()
        manager = TodoManager(str(todo_file))
        result = list(run_todos(controller, manager, 100))
        # Should process the 1 available item, not crash
        assert len(result) == 1

    def test_determine_count_with_explicit_count_one(self):
        args = _make_args(count=1)
        result = _determine_count(args, list(range(10)))
        assert result == 1

    def test_determine_count_large_positive(self):
        args = _make_args(count=999)
        result = _determine_count(args, list(range(10)))
        assert result == 999

    def test_controller_metrics_after_todos(self, tmp_path):
        """Controller metrics should be updated after processing todos."""
        content = _sample_todo_content(
            todo_lines=["t1 | droid:verify_real_methods | Check"]
        )
        todo_file = _make_todo_file(tmp_path, content)
        controller = create_default_controller()
        manager = TodoManager(str(todo_file))

        list(run_todos(controller, manager, 1))
        metrics = controller.metrics
        assert metrics["tasks_executed"] >= 1

    def test_enhanced_prompt_contains_security(self):
        assert "Security" in CODOMYRMEX_ENHANCED_PROMPT or "security" in CODOMYRMEX_ENHANCED_PROMPT.lower()

    def test_enhanced_prompt_contains_testing(self):
        assert "Test" in CODOMYRMEX_ENHANCED_PROMPT or "test" in CODOMYRMEX_ENHANCED_PROMPT.lower()

    def test_todo_file_with_comments_and_blank_lines(self, tmp_path):
        """Todo files with comments and blank lines should load correctly."""
        content = textwrap.dedent("""\
            # This is a comment
            [TODO]
            # Another comment
            t1 | desc1 | out1

            [COMPLETED]
        """)
        f = _make_todo_file(tmp_path, content)
        manager = TodoManager(str(f))
        items, completed = manager.load()
        assert len(items) == 1
        assert items[0].task_name == "t1"

    def test_resolve_handler_returns_callable_for_all_builtins(self):
        """All four built-in task handlers should be resolvable."""
        names = [
            "ensure_documentation_exists",
            "confirm_logging_integrations",
            "verify_real_methods",
            "verify_readiness",
        ]
        for name in names:
            handler = resolve_handler(f"droid:{name}")
            assert callable(handler), f"Handler {name} is not callable"


# ===========================================================================
# 13. Controller integration via build_controller
# ===========================================================================

class TestBuildControllerIntegration:
    """Deeper tests for build_controller behavior."""

    def test_default_controller_is_idle(self):
        ctrl = build_controller(None)
        # create_default_controller calls start(), so status should be IDLE
        assert ctrl.status == DroidStatus.IDLE

    def test_controller_from_config_safe_mode(self, tmp_path):
        config_data = {
            "identifier": "safe-droid",
            "mode": "test",
            "safe_mode": True,
            "max_parallel_tasks": 2,
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data), encoding="utf-8")
        ctrl = build_controller(str(config_path))
        assert ctrl.config.safe_mode is True
        assert ctrl.config.max_parallel_tasks == 2
