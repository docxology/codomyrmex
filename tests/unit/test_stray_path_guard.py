"""Tests for the stray-path guard that tests/conftest.py registers."""

from __future__ import annotations

from pathlib import Path

import pytest
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
