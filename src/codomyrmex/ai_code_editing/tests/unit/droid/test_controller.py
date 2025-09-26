"""Unit tests for the droid package."""

import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

TEST_DIR = os.path.dirname(__file__)
PACKAGE_ROOT = os.path.abspath(os.path.join(TEST_DIR, "../../.."))
MODULE_ROOT = os.path.abspath(os.path.join(TEST_DIR, "../../../.."))
for path in (MODULE_ROOT, PACKAGE_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from ai_code_editing.droid import (  # noqa: E402
    DroidConfig,
    DroidController,
    DroidMode,
    DroidStatus,
    TodoManager,
    TodoItem,
    create_default_controller,
    load_config_from_file,
    save_config_to_file,
)

from ai_code_editing.droid.run_todo_droid import run_todos, CODOMYRMEX_ENHANCED_PROMPT  # noqa: E402
from ai_code_editing.droid.tasks import (  # noqa: E402
    confirm_logging_integrations,
    ensure_documentation_exists,
    verify_real_methods,
)


class TestDroidConfig(unittest.TestCase):
    def test_from_env(self) -> None:
        with mock.patch.dict(os.environ, {
            "DROID_IDENTIFIER": "factory-droid",
            "DROID_MODE": "production",
            "DROID_MAX_PARALLEL_TASKS": "2",
            "DROID_ALLOWED_OPERATIONS": "op1,op2",
        }, clear=True):
            config = DroidConfig.from_env()
        self.assertEqual(config.identifier, "factory-droid")
        self.assertEqual(config.mode, DroidMode.PRODUCTION)
        self.assertEqual(config.max_parallel_tasks, 2)
        self.assertEqual(config.allowed, frozenset({"op1", "op2"}))

    def test_save_and_load_roundtrip(self) -> None:
        config = DroidConfig(identifier="demo", max_parallel_tasks=3)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            save_config_to_file(config, path)
            loaded = load_config_from_file(path)
        self.assertEqual(loaded.identifier, "demo")
        self.assertEqual(loaded.max_parallel_tasks, 3)


class TestDroidController(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = create_default_controller()

    def tearDown(self) -> None:
        self.controller.stop()

    def test_status_transitions(self) -> None:
        self.assertEqual(self.controller.status, DroidStatus.IDLE)
        self.controller.stop()
        self.assertEqual(self.controller.status, DroidStatus.STOPPED)
        self.controller.start()
        self.assertEqual(self.controller.status, DroidStatus.IDLE)

    def test_execute_task_success(self) -> None:
        result = self.controller.execute_task(
            "doc_check",
            ensure_documentation_exists,
            prompt=CODOMYRMEX_ENHANCED_PROMPT,
            description="Ensure docs",
        )
        self.assertEqual(result, "documentation verified")
        metrics = self.controller.metrics
        self.assertEqual(metrics["tasks_executed"], 1)
        self.assertEqual(metrics["tasks_failed"], 0)

    def test_execute_task_failure(self) -> None:
        def failing_handler(**_kwargs):
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            self.controller.execute_task("explode", failing_handler)
        metrics = self.controller.metrics
        self.assertEqual(metrics["tasks_failed"], 1)
        self.assertEqual(self.controller.status, DroidStatus.ERROR)


class TestTodoManager(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.todo_path = Path(self.tempdir.name) / "todo.txt"
        content = "\n".join([
            "[TODO]",
            "task1 | module:callable | First task",
            "task2 | module:callable | Second task",
            "",
            "[COMPLETED]",
            "task0 | module:callable | Completed task",
            "",
        ])
        self.todo_path.write_text(content, encoding="utf-8")
        self.manager = TodoManager(self.todo_path)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_load_parses_sections(self) -> None:
        todo_items, completed_items = self.manager.load()
        self.assertEqual(len(todo_items), 2)
        self.assertEqual(len(completed_items), 1)
        self.assertIsInstance(todo_items[0], TodoItem)

    def test_rotate_moves_processed(self) -> None:
        todo_items, completed_items = self.manager.load()
        processed = [todo_items[0]]
        remaining = todo_items[1:]
        self.manager.rotate(processed, remaining, completed_items)
        new_todo, new_completed = self.manager.load()
        self.assertEqual(len(new_todo), 1)
        self.assertEqual(len(new_completed), 2)


class TestRunTodos(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.todo_path = Path(self.tempdir.name) / "todo.txt"
        self.todo_path.write_text("\n".join([
            "[TODO]",
            "op_doc | codomyrmex.ai_code_editing.droid.tasks:ensure_documentation_exists | docs",
            "op_log | codomyrmex.ai_code_editing.droid.tasks:confirm_logging_integrations | logs",
            "",
            "[COMPLETED]",
            "",
        ]), encoding="utf-8")
        self.controller = create_default_controller()
        self.manager = TodoManager(self.todo_path)

    def tearDown(self) -> None:
        self.controller.stop()
        self.tempdir.cleanup()

    def test_run_todos_processes_configured_count(self) -> None:
        processed = list(run_todos(self.controller, self.manager, 1))
        self.assertEqual(len(processed), 1)
        todo_items, completed_items = self.manager.load()
        self.assertEqual(len(todo_items), 1)
        self.assertEqual(len(completed_items), 1)

    def test_run_todos_runs_remaining(self) -> None:
        run_todos(self.controller, self.manager, 2)
        todo_items, completed_items = self.manager.load()
        self.assertEqual(len(todo_items), 0)
        self.assertEqual(len(completed_items), 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
