"""Tests for the stray-path guard that tests/conftest.py registers."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT
from tests.support.stray_paths import (
    MODE_ENV,
    StrayPathGuard,
    format_report,
    guard_mode,
)


@pytest.mark.unit
class TestStrayPathGuard:
    def test_reports_entries_created_after_the_baseline(self, tmp_path: Path) -> None:
        (tmp_path / "existing").mkdir()
        guard = StrayPathGuard(tmp_path)
        (tmp_path / "git_analysis").mkdir()
        (tmp_path / "report.txt").write_text("x")
        assert guard.stray_paths() == ["git_analysis", "report.txt"]

    def test_removed_entries_are_not_reported(self, tmp_path: Path) -> None:
        guard = StrayPathGuard(tmp_path)
        (tmp_path / "transient").mkdir()
        (tmp_path / "transient").rmdir()
        assert guard.stray_paths() == []

    def test_removed_repository_is_an_observation_failure(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        guard = StrayPathGuard(repo)
        repo.rmdir()
        assert guard.stray_paths() == []
        assert "FileNotFoundError" in guard.snapshot_errors["."]

    def test_renamed_invocation_directory_keeps_first_failure(
        self, tmp_path: Path
    ) -> None:
        start = tmp_path / "tests"
        start.mkdir()
        guard = StrayPathGuard(tmp_path, invocation_dir=start)
        renamed = tmp_path / "renamed"
        start.rename(renamed)
        guard.note("test_removed_directory")
        renamed.rename(start)
        assert guard.stray_paths() == []
        assert "FileNotFoundError" in guard.snapshot_errors["tests"]

    def test_pytest_and_coverage_outputs_are_ignored(self, tmp_path: Path) -> None:
        guard = StrayPathGuard(tmp_path)
        for name in (".pytest_cache", ".coverage.host.123", "coverage.xml", "htmlcov"):
            (tmp_path / name).mkdir()
        (tmp_path / "junit-unit.xml").write_text("<testsuites/>")
        assert guard.stray_paths() == []

    def test_configured_outputs_and_their_parents_are_ignored(
        self, tmp_path: Path
    ) -> None:
        basetemp = tmp_path / "build" / "pytest-tmp"
        guard = StrayPathGuard(tmp_path, tool_outputs=[basetemp, "/elsewhere/x.xml"])
        basetemp.mkdir(parents=True)
        assert guard.stray_paths() == []

    def test_watches_invocation_dir_inside_the_repository(self, tmp_path: Path) -> None:
        start = tmp_path / "tests"
        start.mkdir()
        guard = StrayPathGuard(tmp_path, invocation_dir=start)
        (start / "output").mkdir()
        assert guard.stray_paths() == ["tests/output"]

    def test_ignores_invocation_dir_outside_the_repository(
        self, tmp_path: Path
    ) -> None:
        repo, outside = tmp_path / "repo", tmp_path / "outside"
        repo.mkdir()
        outside.mkdir()
        guard = StrayPathGuard(repo, invocation_dir=outside)
        (outside / "scratch").mkdir()
        assert guard.stray_paths() == []

    def test_note_keeps_the_first_test_after_which_a_path_appeared(
        self, tmp_path: Path
    ) -> None:
        guard = StrayPathGuard(tmp_path)
        guard.note("test_a")
        (tmp_path / "config_audits").mkdir()
        guard.note("test_b")
        guard.note("test_c")
        assert guard.first_seen == {"config_audits": "test_b"}
        assert format_report(["config_audits"], {"config_audits": ["test_b"]}) == [
            "config_audits  (first seen after: test_b)"
        ]


@pytest.mark.unit
class TestGuardMode:
    def test_defaults_to_fail(self) -> None:
        assert guard_mode({}) == "fail"
        assert guard_mode({MODE_ENV: ""}) == "fail"

    def test_accepts_known_modes_case_insensitively(self) -> None:
        assert guard_mode({MODE_ENV: "WARN"}) == "warn"
        assert guard_mode({MODE_ENV: " off "}) == "off"

    def test_rejects_unknown_modes(self) -> None:
        with pytest.raises(ValueError, match=MODE_ENV):
            guard_mode({MODE_ENV: "strict"})


@pytest.mark.unit
@pytest.mark.parametrize(("mode", "expected_exit"), [("fail", 1), ("warn", 0)])
@pytest.mark.parametrize("workers", [0, 2])
def test_plugin_reports_missing_directory_without_accepting_fail_mode(
    tmp_path: Path, mode: str, expected_exit: int, workers: int
) -> None:
    watched = tmp_path / "watched"
    watched.mkdir()
    (tmp_path / "conftest.py").write_text(
        "from pathlib import Path\n"
        "from tests.support.stray_paths import StrayPathPlugin\n"
        "def pytest_configure(config):\n"
        f"    root = Path({str(watched)!r})\n"
        f"    config.pluginmanager.register(StrayPathPlugin(config, root, {mode!r}))\n",
        encoding="utf-8",
    )
    (tmp_path / "test_observation.py").write_text(
        "from pathlib import Path\n"
        "def test_remove_watched_directory():\n"
        f"    Path({str(watched)!r}).rmdir()\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(REPO_ROOT), env.get("PYTHONPATH")])
    )
    command = [sys.executable, "-m", "pytest", "-q", "--confcutdir", str(tmp_path)]
    if workers:
        command.extend(["-n", str(workers)])
    result = subprocess.run(
        command,
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == expected_exit, result.stdout + result.stderr
    assert "Cannot inspect watched directory '.'" in result.stdout
    assert "FileNotFoundError" in result.stdout
