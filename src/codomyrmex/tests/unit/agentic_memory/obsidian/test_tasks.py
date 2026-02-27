"""Tests for task CLI commands."""

import shutil

import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.tasks import (
    TaskItem,
    _parse_tasks,
    get_task,
    list_tasks,
    set_task_status,
    toggle_task,
)

_CLI_AVAILABLE = shutil.which("obsidian") is not None
skip_no_cli = pytest.mark.skipif(
    not _CLI_AVAILABLE,
    reason="Obsidian CLI not available on PATH",
)


class TestTaskItem:
    def test_is_done(self):
        t = TaskItem(text="Buy milk", status="x")
        assert t.is_done is True
        assert t.is_todo is False

    def test_is_todo(self):
        t = TaskItem(text="Review PR", status=" ")
        assert t.is_todo is True
        assert t.is_done is False

    def test_custom_status(self):
        t = TaskItem(text="In progress", status="/")
        assert t.is_done is False
        assert t.is_todo is False

    def test_case_insensitive_done(self):
        t = TaskItem(text="Done", status="X")
        assert t.is_done is True


class TestParseTasks:
    def test_parse_simple_checkbox(self):
        lines = [
            "- [ ] Todo item",
            "- [x] Done item",
            "- [/] In progress",
        ]
        tasks = _parse_tasks(lines)
        assert len(tasks) == 3
        assert tasks[0].text == "Todo item"
        assert tasks[0].status == " "
        assert tasks[1].status == "x"
        assert tasks[2].status == "/"

    def test_parse_with_file_and_line(self):
        lines = [
            "notes/todo.md:5: - [ ] Buy groceries",
            "notes/work.md:12: - [x] Send email",
        ]
        tasks = _parse_tasks(lines)
        assert len(tasks) == 2
        assert tasks[0].file == "notes/todo.md"
        assert tasks[0].line == 5
        assert tasks[0].text == "Buy groceries"
        assert tasks[1].status == "x"

    def test_parse_empty_lines(self):
        assert _parse_tasks(["", "   ", "\n"]) == []

    def test_parse_non_task_lines(self):
        lines = ["# Heading", "Regular paragraph", "- Just a bullet"]
        assert _parse_tasks(lines) == []


class TestTaskUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_tasks(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_tasks(self._cli())

    def test_list_tasks_all_filters(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_tasks(
                self._cli(), file="note",
                status="x", format="json",
                done=True, todo=True, daily=True,
                active=True, verbose=True, total=True,
            )

    def test_get_task(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_task(self._cli(), ref="note.md:5")

    def test_get_task_with_line(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_task(self._cli(), file="note", line=5, daily=True)

    def test_toggle_task(self):
        with pytest.raises(ObsidianCLINotAvailable):
            toggle_task(self._cli(), file="note", line=5)

    def test_toggle_task_by_ref(self):
        with pytest.raises(ObsidianCLINotAvailable):
            toggle_task(self._cli(), ref="note.md:5")

    def test_set_task_status(self):
        with pytest.raises(ObsidianCLINotAvailable):
            set_task_status(self._cli(), "x", file="note", line=5)

    def test_set_task_status_daily(self):
        with pytest.raises(ObsidianCLINotAvailable):
            set_task_status(self._cli(), "/", daily=True)
