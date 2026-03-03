import io
import json
import os
import sys
from pathlib import Path

import pytest

from codomyrmex.agents.droid.controller import DroidController
from codomyrmex.agents.droid.run_todo_droid import (
    _determine_count,
    _list_todos,
    _process_todos,
    _show_dry_run,
    build_controller,
    demo_programmatic_usage,
    get_todo_count_interactive,
    main,
    resolve_handler,
    run_todos,
)
from codomyrmex.agents.droid.todo import TodoItem, TodoManager


def dummy_handler():
    """A dummy handler for testing."""
    return "success"


def unsafe_dummy_handler():
    """A dummy unsafe handler for testing."""
    return "unsafe"


def dummy_error_handler():
    """A dummy handler that raises an error."""
    raise ValueError("dummy error")


def test_resolve_handler_invalid_module():
    with pytest.raises(ImportError):
        resolve_handler("invalid_module_that_does_not_exist:invalid_function")


def test_resolve_handler_missing_attr():
    with pytest.raises(AttributeError):
        resolve_handler("codomyrmex.agents.droid.run_todo_droid:non_existent_function")


def test_resolve_handler_valid():
    handler = resolve_handler("codomyrmex.agents.droid.run_todo_droid:resolve_handler")
    assert handler is resolve_handler


def test_resolve_handler_fallback(tmp_path):
    # This tests the expansion logic. We can't easily mock the import so we'll test the error handling.
    # When no module specified, it defaults to droid.tasks
    with pytest.raises(AttributeError):
        resolve_handler("some_function_without_colon")

    with pytest.raises(AttributeError):
        resolve_handler("droid:some_function")

    with pytest.raises(ImportError):
        resolve_handler("ai_code:some_function")


def test_get_todo_count_interactive(monkeypatch, tmp_path):
    # Setup a temporary todo_list.txt in the expected location
    Path(__file__).parent.parent.parent.parent.parent / "agents" / "droid"
    # To test get_todo_count_interactive without modifying source dir, we patch os.path.dirname
    monkeypatch.setattr(os.path, "dirname", lambda p: str(tmp_path))

    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text(
        "[TODO]\nTask1 | Desc1 | Out1\nTask2 | Desc2 | Out2\n[COMPLETED]\n",
        encoding="utf-8",
    )

    # Test 'all'
    monkeypatch.setattr(sys, "stdin", io.StringIO("all\n"))
    assert get_todo_count_interactive() == 2

    # Test valid number
    monkeypatch.setattr(sys, "stdin", io.StringIO("1\n"))
    assert get_todo_count_interactive() == 1

    # Test invalid number then valid
    monkeypatch.setattr(sys, "stdin", io.StringIO("5\n-1\ninvalid\n2\n"))
    assert get_todo_count_interactive() == 2

    # Test KeyboardInterrupt
    def mock_input(prompt):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    with pytest.raises(SystemExit):
        get_todo_count_interactive()


def test_get_todo_count_interactive_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(os.path, "dirname", lambda p: str(tmp_path))
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text("[TODO]\n[COMPLETED]\n", encoding="utf-8")
    assert get_todo_count_interactive() == 0


def test_run_todos_empty(tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text("[TODO]\n[COMPLETED]\n", encoding="utf-8")
    manager = TodoManager(str(todo_file))
    controller = DroidController(
        config=build_controller(None).config.with_overrides(
            allowed_operations=["TestTask"]
        )
    )
    processed = list(run_todos(controller, manager, 1))
    assert processed == []


def dummy_handler_with_kwargs(*args, **kwargs):
    return "success"


def test_run_todos_success(tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    # Legacy format is operation_id | handler_path | description
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))

    controller = DroidController(
        config=build_controller(None).config.with_overrides(
            allowed_operations=["TestTask"]
        )
    )
    controller.start()
    processed = list(run_todos(controller, manager, 1))
    assert len(processed) == 1
    assert processed[0].task_name == "TestTask"

    # Check if rotated
    todos, completed = manager.load()
    assert len(todos) == 0
    assert len(completed) == 1
    assert completed[0].task_name == "TestTask"


def test_run_todos_failure(tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    # Using an existing module but raising an error
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_error_handler | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))

    controller = DroidController(
        config=build_controller(None).config.with_overrides(
            allowed_operations=["TestTask"]
        )
    )
    controller.start()
    processed = list(run_todos(controller, manager, 1))

    assert len(processed) == 0
    # Not rotated
    todos, completed = manager.load()
    assert len(todos) == 1
    assert len(completed) == 0


def test_run_todos_no_handler(tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    # No handler provided, and inference will fail. Using new format: task_name | description | outcomes
    todo_file.write_text(
        "[TODO]\nimplement_nothing | Desc | Out\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))

    controller = DroidController(
        config=build_controller(None).config.with_overrides(
            allowed_operations=["implement_nothing"]
        )
    )
    controller.start()

    # run_todos catches the error inside, and just continues but logs it as failed
    processed = list(run_todos(controller, manager, 1))

    assert len(processed) == 0
    todos, completed = manager.load()
    assert len(todos) == 1


def test_build_controller(tmp_path, monkeypatch):
    # Without config
    controller = build_controller(None)
    assert isinstance(controller, DroidController)

    # Without config and create_default_controller missing (fallback to DroidController())
    import codomyrmex.agents.droid.run_todo_droid as module_to_patch

    monkeypatch.delattr(module_to_patch, "create_default_controller")
    controller_fallback = module_to_patch.build_controller(None)
    assert isinstance(controller_fallback, DroidController)

    # With config
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"identifier": "test_droid", "mode": "test"}), encoding="utf-8"
    )
    controller2 = build_controller(str(config_file))
    assert isinstance(controller2, DroidController)
    assert controller2.config.identifier == "test_droid"


def test_list_todos(capsys):
    item1 = TodoItem("Task1", "Desc1", "Out1", "path1")
    item2 = TodoItem("Task2", "Desc2", "Out2", None)

    _list_todos([], [])
    captured = capsys.readouterr()
    assert "No TODO items found" in captured.out

    _list_todos([item1], [item2])
    captured = capsys.readouterr()
    assert "[Task1]" in captured.out
    assert "path1" in captured.out
    assert "Completed (1 items)" in captured.out
    assert "[Task2]" in captured.out


def test_determine_count():
    class Args:
        def __init__(self, count, non_interactive, dry_run):
            self.count = count
            self.non_interactive = non_interactive
            self.dry_run = dry_run

    # Also we need to test processing all with 'all'

    todos = [1, 2, 3]

    assert _determine_count(Args(-1, False, False), todos) == 3
    assert _determine_count(Args(2, False, False), todos) == 2

    # capturing stdout for the invalid print
    import io
    import sys

    stdout = io.StringIO()
    sys.stdout = stdout
    assert _determine_count(Args(-2, False, False), todos) is None
    sys.stdout = sys.__stdout__

    assert _determine_count(Args(None, True, False), todos) == 1
    assert _determine_count(Args(None, False, True), todos) == 1


def test_show_dry_run(capsys):
    item = TodoItem("Task1", "Desc1", "Out1", "path1")
    _show_dry_run(1, [item])
    captured = capsys.readouterr()
    assert "Dry run: Would process 1 TODO(s)" in captured.out
    assert "[Task1] Desc1" in captured.out
    assert "Outcomes: Out1" in captured.out


def test_process_todos(capsys, tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    # Legacy format: operation_id | handler_path | description
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))
    controller = DroidController(
        config=build_controller(None).config.with_overrides(
            allowed_operations=["TestTask"]
        )
    )
    controller.start()

    _process_todos(controller, manager, 1)
    captured = capsys.readouterr()
    assert "Successfully processed: 1 TODO(s)" in captured.out

    # Test error fallback (keyboard interrupt isn't easily testable without mock, but we can try erroring handler)
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_error_handler | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))
    _process_todos(controller, manager, 1)
    captured = capsys.readouterr()
    assert "No TODO items were processed" in captured.out


def test_main(monkeypatch, tmp_path, capsys):
    todo_file = tmp_path / "todo_list.txt"
    # Legacy format
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys, "argv", ["run_todo_droid.py", "--todo-file", str(todo_file), "--list"]
    )
    main()
    captured = capsys.readouterr()
    assert "TODO List:" in captured.out

    monkeypatch.setattr(
        sys, "argv", ["run_todo_droid.py", "--todo-file", str(todo_file), "--dry-run"]
    )
    main()
    captured = capsys.readouterr()
    assert "Dry run" in captured.out

    monkeypatch.setattr(
        sys,
        "argv",
        ["run_todo_droid.py", "--todo-file", str(todo_file), "--count", "1"],
    )
    main()
    captured = capsys.readouterr()
    assert "Execution Summary" in captured.out

    # Test invalid count
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_todo_droid.py", "--todo-file", str(todo_file), "--count", "-2"],
    )
    main()

    # Test no todos
    empty_todo = tmp_path / "empty.txt"
    empty_todo.write_text("[TODO]\n[COMPLETED]\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_todo_droid.py", "--todo-file", str(empty_todo), "--count", "1"],
    )
    main()
    captured = capsys.readouterr()
    assert "No TODOs to process. Exiting." in captured.out


def test_process_todos_controller_metrics_fallback(capsys, tmp_path, monkeypatch):
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))
    controller = DroidController(
        config=build_controller(None).config.with_overrides(
            allowed_operations=["TestTask"]
        )
    )
    controller.start()

    # We need to simulate controller metrics raising AttributeError
    def mock_metrics(self):
        raise AttributeError("mocked error")

    monkeypatch.setattr(DroidController, "metrics", property(mock_metrics))

    _process_todos(controller, manager, 1)
    captured = capsys.readouterr()
    assert "Droid session completed" in captured.out


def test_main_invalid_count_type(monkeypatch, tmp_path, capsys):
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )
    # The count arg handles this via argparse type=int.
    # But wait, what if determine_count is None due to something else?
    # We already test _determine_count. Let's cover the `if count is None:` path in main.
    # To hit this, count is None if _determine_count returns None.
    # _determine_count returns None if args.count < -1. We test that.
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_todo_droid.py", "--todo-file", str(todo_file), "--count", "-2"],
    )
    main()
    captured = capsys.readouterr()
    assert "Invalid count: -2" in captured.out


def test_main_keyboard_interrupt(monkeypatch, tmp_path, capsys):
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )

    TodoManager(str(todo_file))

    def mock_run_todos(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(
        "codomyrmex.agents.droid.run_todo_droid.run_todos", mock_run_todos
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_todo_droid.py", "--todo-file", str(todo_file), "--count", "1"],
    )
    main()
    captured = capsys.readouterr()
    assert "Operation interrupted by user" in captured.out


def test_main_metrics_exception(monkeypatch, tmp_path, capsys):
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )

    # We want to trigger the finally block exception `if controller: print(controller.metrics)` in `_process_todos`
    # Let's mock DroidController.metrics property
    def mock_metrics(self):
        raise TypeError("forced exception for coverage")

    monkeypatch.setattr(DroidController, "metrics", property(mock_metrics))
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_todo_droid.py", "--todo-file", str(todo_file), "--count", "1"],
    )
    main()
    captured = capsys.readouterr()
    assert "Droid session completed." in captured.out


def test_run_todos_multiple_tasks_with_metrics(tmp_path, capsys):
    todo_file = tmp_path / "todo_list.txt"
    # Create two items to cover the summary loop and multiple task logging
    todo_file.write_text(
        "[TODO]\nTestTask1 | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc1\nTestTask2 | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc2\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))

    controller = DroidController(
        config=build_controller(None).config.with_overrides(
            allowed_operations=["TestTask1", "TestTask2"]
        )
    )
    controller.start()

    processed = list(run_todos(controller, manager, 2))
    assert len(processed) == 2

    captured = capsys.readouterr()
    assert "Execution Summary:" in captured.out
    assert "Task Performance:" in captured.out
    assert "Average task time:" in captured.out
    assert "Fastest task:" in captured.out


def test_run_todos_no_items(tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text("[TODO]\n[COMPLETED]\n", encoding="utf-8")
    manager = TodoManager(str(todo_file))

    controller = DroidController(config=build_controller(None).config)
    processed = list(run_todos(controller, manager, 1))

    assert len(processed) == 0


def test_process_todos_controller_none(capsys, tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )
    manager = TodoManager(str(todo_file))

    # Passing None as controller to test `if controller:` exception block coverage
    _process_todos(None, manager, 1)
    captured = capsys.readouterr()
    assert "Droid session completed." in captured.out


def test_demo_programmatic_usage(monkeypatch, tmp_path):
    todo_file = tmp_path / "todo_list.txt"
    # Legacy format
    todo_file.write_text(
        "[TODO]\nTestTask | codomyrmex.tests.unit.agents.droid.test_run_todo_droid:dummy_handler_with_kwargs | Desc\n[COMPLETED]\n",
        encoding="utf-8",
    )

    # We patch os.path.dirname because demo_programmatic_usage expects todo_list.txt in the same dir as the module
    monkeypatch.setattr(os.path, "dirname", lambda p: str(tmp_path))

    processed = demo_programmatic_usage()
    assert len(processed) == 1
    assert processed[0].task_name == "TestTask"
