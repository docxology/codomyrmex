"""Unit tests for codomyrmex.agents.ai_code_editing.droid_manager.

Covers DroidSystemManager, DroidController (re-exported), and the
convenience functions get_droid_manager / show_droid_status.
Zero-mock policy: all objects are real instances; filesystem interaction
uses tmp_path fixtures.
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from codomyrmex.agents.ai_code_editing.droid_manager import (
    DroidSystemManager,
    get_droid_manager,
    show_droid_status,
)
from codomyrmex.agents.droid.controller import (
    DroidConfig,
    DroidController,
    DroidMode,
)
from codomyrmex.agents.droid.todo import TodoManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_todo_file(path: Path, todos: list[str] | None = None, completed: list[str] | None = None) -> None:
    """Write a well-formed todo_list.txt file."""
    lines = ["[TODO]"]
    for t in (todos or []):
        lines.append(t)
    lines.append("")
    lines.append("[COMPLETED]")
    for c in (completed or []):
        lines.append(c)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_manager(tmp_path: Path, todos: list[str] | None = None, completed: list[str] | None = None) -> DroidSystemManager:
    """Create a DroidSystemManager pointing at a temp droid dir."""
    droid_dir = tmp_path / "droid"
    droid_dir.mkdir(parents=True, exist_ok=True)
    todo_file = droid_dir / "todo_list.txt"
    _write_todo_file(todo_file, todos=todos, completed=completed)
    return DroidSystemManager(droid_dir=droid_dir)


# ---------------------------------------------------------------------------
# DroidSystemManager tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDroidSystemManagerInit:
    """Initialization behaviour of DroidSystemManager."""

    def test_init_with_explicit_dir(self, tmp_path: Path) -> None:
        droid_dir = tmp_path / "custom_droid"
        droid_dir.mkdir()
        (droid_dir / "todo_list.txt").write_text("[TODO]\n[COMPLETED]\n")
        mgr = DroidSystemManager(droid_dir=droid_dir)
        assert mgr.droid_dir == droid_dir
        assert mgr.todo_file == droid_dir / "todo_list.txt"
        assert mgr.config_file == droid_dir / "droid_config.json"

    def test_init_with_string_path(self, tmp_path: Path) -> None:
        droid_dir = tmp_path / "str_droid"
        droid_dir.mkdir()
        (droid_dir / "todo_list.txt").write_text("[TODO]\n[COMPLETED]\n")
        mgr = DroidSystemManager(droid_dir=str(droid_dir))
        assert isinstance(mgr.droid_dir, Path)
        assert mgr.droid_dir == droid_dir

    def test_init_default_dir(self) -> None:
        """When droid_dir is None the manager falls back to a sibling 'droid' directory."""
        mgr = DroidSystemManager(droid_dir=None)
        # Should be <module_dir>/droid
        expected_parent = Path(__file__).parent  # test dir
        # The default is relative to droid_manager.py, not us
        assert mgr.droid_dir.name == "droid"

    def test_session_stats_initial_values(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        stats = mgr.session_stats
        assert stats["total_sessions"] == 0
        assert stats["total_tasks_executed"] == 0
        assert stats["total_tasks_failed"] == 0
        assert stats["last_execution_time"] is None
        assert stats["uptime_seconds"] == 0

    def test_controller_initially_none(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        assert mgr.controller is None

    def test_todo_manager_is_real_instance(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        assert isinstance(mgr.todo_manager, TodoManager)


@pytest.mark.unit
class TestDroidSystemManagerStatus:
    """get_system_status / display_system_status coverage."""

    def test_status_empty_todo_file(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        status = mgr.get_system_status()
        assert "system" in status
        assert "todo_stats" in status
        assert "session_stats" in status
        assert "controller_metrics" in status

    def test_status_system_section(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        system = mgr.get_system_status()["system"]
        assert system["controller_active"] is False
        assert isinstance(system["uptime_seconds"], float)
        assert system["uptime_seconds"] >= 0

    def test_status_config_loaded_flag(self, tmp_path: Path) -> None:
        """config_loaded should reflect whether droid_config.json exists."""
        mgr = _make_manager(tmp_path)
        assert mgr.get_system_status()["system"]["config_loaded"] is False

        # Create the config file
        mgr.config_file.write_text("{}", encoding="utf-8")
        assert mgr.get_system_status()["system"]["config_loaded"] is True

    def test_status_todo_stats_with_items(self, tmp_path: Path) -> None:
        mgr = _make_manager(
            tmp_path,
            todos=["task1 | desc1 | out1", "task2 | desc2 | out2"],
            completed=["done1 | finished | result"],
        )
        todo_stats = mgr.get_system_status()["todo_stats"]
        assert todo_stats["total_todos"] == 2
        assert todo_stats["completed_todos"] == 1
        # completion_rate = 1 / (2+1) * 100 = 33.33...
        assert 33.0 < todo_stats["completion_rate"] < 34.0

    def test_status_completion_rate_no_items(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        todo_stats = mgr.get_system_status()["todo_stats"]
        # 0 / max(0,1) * 100 = 0
        assert todo_stats["completion_rate"] == 0.0

    def test_status_controller_metrics_when_active(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        config = DroidConfig(mode=DroidMode.TEST)
        mgr.controller = DroidController(config)
        mgr.controller.start()

        metrics = mgr.get_system_status()["controller_metrics"]
        assert "sessions_started" in metrics
        assert metrics["sessions_started"] == 1

    def test_display_system_status_runs(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """display_system_status should print without error."""
        mgr = _make_manager(tmp_path)
        mgr.display_system_status()
        captured = capsys.readouterr()
        assert "Codomyrmex Droid System Status" in captured.out
        assert "TODO Statistics" in captured.out
        assert "Session Statistics" in captured.out

    def test_display_status_with_active_controller(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        mgr = _make_manager(tmp_path)
        config = DroidConfig(mode=DroidMode.TEST)
        mgr.controller = DroidController(config)
        mgr.controller.start()
        mgr.display_system_status()
        captured = capsys.readouterr()
        assert "Controller Active" in captured.out


@pytest.mark.unit
class TestDroidSystemManagerSessionStats:
    """Session stats dict is a mutable reference -- verify direct mutation works."""

    def test_session_stats_mutation(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        mgr.session_stats["total_sessions"] = 5
        mgr.session_stats["total_tasks_executed"] = 10
        assert mgr.session_stats["total_sessions"] == 5
        status = mgr.get_system_status()
        assert status["session_stats"]["total_sessions"] == 5
        assert status["session_stats"]["total_tasks_executed"] == 10

    def test_session_stats_copy_in_status(self, tmp_path: Path) -> None:
        """get_system_status returns a *copy* of session_stats."""
        mgr = _make_manager(tmp_path)
        status = mgr.get_system_status()
        status["session_stats"]["total_sessions"] = 999
        # Original should be unchanged
        assert mgr.session_stats["total_sessions"] == 0


# ---------------------------------------------------------------------------
# Convenience function tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for get_droid_manager and show_droid_status."""

    def test_get_droid_manager_returns_instance(self, tmp_path: Path) -> None:
        droid_dir = tmp_path / "conv"
        droid_dir.mkdir()
        (droid_dir / "todo_list.txt").write_text("[TODO]\n[COMPLETED]\n")
        mgr = get_droid_manager(droid_dir=droid_dir)
        assert isinstance(mgr, DroidSystemManager)

    def test_get_droid_manager_default_dir(self) -> None:
        mgr = get_droid_manager()
        assert isinstance(mgr, DroidSystemManager)

    def test_show_droid_status_prints(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        droid_dir = tmp_path / "show"
        droid_dir.mkdir()
        (droid_dir / "todo_list.txt").write_text("[TODO]\n[COMPLETED]\n")
        show_droid_status(droid_dir=droid_dir)
        captured = capsys.readouterr()
        assert "Codomyrmex Droid System Status" in captured.out


# ---------------------------------------------------------------------------
# Integration: DroidSystemManager + real DroidController lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestManagerControllerIntegration:
    """Verify DroidSystemManager works with a real DroidController."""

    def test_attach_controller_and_check_status(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        config = DroidConfig(mode=DroidMode.TEST, safe_mode=False)
        ctrl = DroidController(config)
        ctrl.start()
        mgr.controller = ctrl

        status = mgr.get_system_status()
        assert status["system"]["controller_active"] is True
        assert status["controller_metrics"]["sessions_started"] == 1

    def test_execute_task_through_controller(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        config = DroidConfig(mode=DroidMode.TEST, safe_mode=False)
        ctrl = DroidController(config)
        ctrl.start()
        mgr.controller = ctrl

        result = ctrl.execute_task("add", lambda a, b: a + b, 3, 7)
        assert result == 10

        metrics = mgr.get_system_status()["controller_metrics"]
        assert metrics["tasks_executed"] == 1
        assert metrics["last_task"] == "add"

    def test_controller_stop_reflects_in_status(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        config = DroidConfig(mode=DroidMode.TEST)
        ctrl = DroidController(config)
        ctrl.start()
        mgr.controller = ctrl
        ctrl.stop()

        metrics = mgr.get_system_status()["controller_metrics"]
        assert metrics["sessions_completed"] == 1

    def test_uptime_increases(self, tmp_path: Path) -> None:
        mgr = _make_manager(tmp_path)
        t0 = mgr.get_system_status()["system"]["uptime_seconds"]
        # Small sleep to ensure uptime advances
        time.sleep(0.05)
        t1 = mgr.get_system_status()["system"]["uptime_seconds"]
        assert t1 > t0
