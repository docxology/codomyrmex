"""Regression tests for the fail-closed placeholder checker CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "src"
    / "codomyrmex"
    / "documentation"
    / "scripts"
    / "placeholder_check.py"
)


def _run(repo: Path | None, *arguments: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT)]
    if repo is not None:
        command.extend(("--repo-root", str(repo)))
    command.extend(arguments)
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _make_repository(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    readme = repo / "src" / "codomyrmex" / "demo" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text(
        "# Demo\n\nContains components for the src system.\n",
        encoding="utf-8",
    )
    return repo, readme


def test_help_is_read_only(tmp_path: Path) -> None:
    repo, readme = _make_repository(tmp_path)
    original = readme.read_bytes()

    result = _run(repo, "--help")

    assert result.returncode == 0
    assert "--dry-run" in result.stdout
    assert "--apply" in result.stdout
    assert readme.read_bytes() == original


def test_mode_is_required(tmp_path: Path) -> None:
    repo, readme = _make_repository(tmp_path)
    original = readme.read_bytes()

    result = _run(repo)

    assert result.returncode == 2
    assert "one of the arguments --dry-run --apply is required" in result.stderr
    assert readme.read_bytes() == original


def test_dry_run_reports_without_writing(tmp_path: Path) -> None:
    repo, readme = _make_repository(tmp_path)
    original = readme.read_bytes()

    result = _run(repo, "--dry-run")

    assert result.returncode == 0
    assert "Would fix generic placeholders" in result.stdout
    assert readme.read_bytes() == original


def test_apply_writes_single_terminal_period(tmp_path: Path) -> None:
    repo, readme = _make_repository(tmp_path)

    result = _run(repo, "--apply")

    assert result.returncode == 0
    content = readme.read_text(encoding="utf-8")
    assert "local coordination for Demo." in content
    assert "Demo.." not in content
