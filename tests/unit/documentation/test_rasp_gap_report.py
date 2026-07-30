"""Tests for the scoped RASP gap report."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "rasp_gap_report.py"
SPEC = importlib.util.spec_from_file_location("codomyrmex_rasp_gap_report", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def test_scan_root_ignores_empty_directory_remnants(tmp_path: Path) -> None:
    empty_leaf = tmp_path / "src" / "codomyrmex" / "retired" / "nested"
    empty_leaf.mkdir(parents=True)

    assert REPORT.scan_root(tmp_path, "src/codomyrmex") == []


def test_scan_root_keeps_live_directories_and_reports_missing_docs(
    tmp_path: Path,
) -> None:
    module = tmp_path / "src" / "codomyrmex" / "live_module"
    module.mkdir(parents=True)
    (module / "__init__.py").write_text('"""Live module."""\n', encoding="utf-8")
    root = tmp_path / "src" / "codomyrmex"
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (root / "README.md").write_text("# Source\n", encoding="utf-8")

    rows = REPORT.scan_root(tmp_path, "src/codomyrmex")

    assert rows == [("src/codomyrmex/live_module", False, False)]


def test_scan_root_ignores_files_under_excluded_cache(tmp_path: Path) -> None:
    cache = tmp_path / "src" / "codomyrmex" / "retired" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "legacy.pyc").write_bytes(b"bytecode")

    assert REPORT.scan_root(tmp_path, "src/codomyrmex") == []


def test_help_is_read_only(tmp_path: Path) -> None:
    report = tmp_path / "docs" / "plans" / "agents-readme-gap-report.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-root",
            str(tmp_path),
            "--help",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--check" in result.stdout
    assert not report.exists()


def test_check_mode_is_read_only_and_fails_on_gap(tmp_path: Path) -> None:
    package_root = tmp_path / "src" / "codomyrmex"
    package_root.mkdir(parents=True)
    (package_root / "README.md").write_text("# Package\n", encoding="utf-8")
    (package_root / "AGENTS.md").write_text("# Package agents\n", encoding="utf-8")
    module = package_root / "live_module"
    module.mkdir(parents=True)
    (module / "__init__.py").write_text('"""Live module."""\n', encoding="utf-8")
    report = tmp_path / "docs" / "plans" / "agents-readme-gap-report.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-root",
            str(tmp_path),
            "--check",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "1 gap rows" in result.stdout
    assert not report.exists()
