"""Tests for the package-wide README/AGENTS audit."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDITOR_PATH = REPO_ROOT / "scripts" / "documentation" / "audit_readme_agents.py"
AUDITOR_SPEC = importlib.util.spec_from_file_location(
    "_test_audit_readme_agents",
    AUDITOR_PATH,
)
assert AUDITOR_SPEC is not None and AUDITOR_SPEC.loader is not None
AUDITOR = importlib.util.module_from_spec(AUDITOR_SPEC)
sys.modules[AUDITOR_SPEC.name] = AUDITOR
AUDITOR_SPEC.loader.exec_module(AUDITOR)
audit_repository = AUDITOR.audit_repository
write_reports = AUDITOR.write_reports


def _write_pair(directory: Path, title: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "README.md").write_text(f"# {title}\n", encoding="utf-8")
    (directory / "AGENTS.md").write_text(
        f"# {title} agent guide\n",
        encoding="utf-8",
    )


def _make_repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    _write_pair(repo, "Repository")
    _write_pair(repo / "docs", "Documentation")
    return repo


def test_valid_minimal_repository_has_no_errors(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)

    result = audit_repository(repo)

    assert result["scope"]["directory_count"] == 2
    assert result["scope"]["file_count"] == 4
    assert result["finding_counts"]["error"] == 0


def test_existing_test_guide_requires_its_pair(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    test_dir = repo / "tests" / "unit" / "example"
    test_dir.mkdir(parents=True)
    (test_dir / "AGENTS.md").write_text("# Test agent guide\n", encoding="utf-8")

    result = audit_repository(repo)

    errors = [
        finding
        for finding in result["findings"]
        if finding["code"] == "missing_pair_member"
    ]
    assert errors == [
        {
            "severity": "error",
            "code": "missing_pair_member",
            "file": "tests/unit/example",
            "line": 1,
            "message": "Directory is missing README.md",
        }
    ]


def test_missing_script_and_skill_references_are_blocking(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    (repo / "README.md").write_text(
        "# Repository\n\n"
        "Run `uv run python scripts/missing.py`.\n"
        "Read `.claude/skills/missing/SKILL.md`.\n",
        encoding="utf-8",
    )

    result = audit_repository(repo)
    codes = {finding["code"] for finding in result["findings"]}

    assert "missing_python_command" in codes
    assert "missing_local_skill" in codes
    assert result["finding_counts"]["error"] == 2


def test_existing_relative_command_and_link_are_accepted(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    script = repo / "scripts" / "check.py"
    script.parent.mkdir()
    script.write_text("print('ok')\n", encoding="utf-8")
    guide = repo / "docs" / "guide.md"
    guide.write_text("# Guide\n", encoding="utf-8")
    (repo / "README.md").write_text(
        "# Repository\n\n"
        "Run `uv run python scripts/check.py` and read [the guide](docs/guide.md).\n",
        encoding="utf-8",
    )

    result = audit_repository(repo)

    assert result["finding_counts"]["error"] == 0


def test_placeholder_script_names_are_not_treated_as_entry_points(
    tmp_path: Path,
) -> None:
    repo = _make_repository(tmp_path)
    (repo / "README.md").write_text(
        "# Repository\n\nUse `python your_script.py` while debugging.\n",
        encoding="utf-8",
    )

    result = audit_repository(repo)

    assert result["finding_counts"]["error"] == 0


def test_reports_are_portable_and_deterministic(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    result = audit_repository(repo)
    json_path = tmp_path / "audit.json"
    markdown_path = tmp_path / "audit.md"

    write_reports(
        result,
        json_path=json_path,
        markdown_path=markdown_path,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload == result
    assert str(tmp_path) not in json_path.read_text(encoding="utf-8")
    assert "# README / AGENTS audit" in markdown_path.read_text(encoding="utf-8")
