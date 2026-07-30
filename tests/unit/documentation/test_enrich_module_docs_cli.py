"""Regression tests for the fail-closed module documentation enricher."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "documentation" / "enrich_module_docs.py"


def _make_repository(tmp_path: Path) -> Path:
    """Create the smallest real repository layout accepted by the CLI."""
    repo = tmp_path / "repo"
    module = repo / "src" / "codomyrmex" / "demo"
    docs = repo / "docs" / "modules" / "demo"
    module.mkdir(parents=True)
    docs.mkdir(parents=True)
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "demo-package"\nversion = "9.8.7"\n',
        encoding="utf-8",
    )
    (module / "__init__.py").write_text(
        '"""Demo module with a source-derived description."""\n'
        '__all__ = ["run"]\n\n'
        "def run() -> str:\n"
        '    """Return a deterministic result."""\n'
        '    return "ok"\n',
        encoding="utf-8",
    )
    return repo


def _run(repo: Path | None, *args: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT)]
    if repo is not None:
        command.extend(("--repo-root", str(repo)))
    command.extend(args)
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_help_is_read_only() -> None:
    result = _run(None, "--help")

    assert result.returncode == 0
    assert "--dry-run" in result.stdout
    assert "--apply" in result.stdout


def test_mode_is_required_before_repository_is_touched(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    docs = repo / "docs" / "modules" / "demo"

    result = _run(repo, "--module", "demo")

    assert result.returncode == 2
    assert "one of the arguments --dry-run --apply is required" in result.stderr
    assert list(docs.iterdir()) == []


def test_dry_run_reports_missing_files_without_writing(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    docs = repo / "docs" / "modules" / "demo"

    result = _run(repo, "--dry-run", "--module", "demo")

    assert result.returncode == 0
    assert "Planned: 3 files" in result.stdout
    assert list(docs.iterdir()) == []


def test_apply_writes_source_derived_safe_examples(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    docs = repo / "docs" / "modules" / "demo"

    result = _run(repo, "--apply", "--module", "demo")

    assert result.returncode == 0
    readme = (docs / "README.md").read_text(encoding="utf-8")
    agents = (docs / "AGENTS.md").read_text(encoding="utf-8")
    spec = (docs / "SPEC.md").read_text(encoding="utf-8")
    assert "<!-- readme: generated -->" in readme
    assert "<!-- agents: generated -->" in agents
    assert "<!-- spec: generated -->" in spec
    assert "v9.8.7" in readme
    assert "import codomyrmex.demo as demo" in readme
    assert "import *" not in readme + agents


def test_curated_files_remain_protected_under_force(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    docs = repo / "docs" / "modules" / "demo"
    curated_readme = "<!-- readme: curated -->\n# Reviewed demo\n"
    curated_agents = "<!-- agents: curated -->\n# Reviewed agent guide\n"
    (docs / "README.md").write_text(curated_readme, encoding="utf-8")
    (docs / "AGENTS.md").write_text(curated_agents, encoding="utf-8")

    result = _run(
        repo,
        "--apply",
        "--module",
        "demo",
        "--force-readmes",
        "--force-agents",
    )

    assert result.returncode == 0
    assert (docs / "README.md").read_text(encoding="utf-8") == curated_readme
    assert (docs / "AGENTS.md").read_text(encoding="utf-8") == curated_agents
    assert (docs / "SPEC.md").is_file()


def test_existing_unmarked_file_requires_explicit_force(tmp_path: Path) -> None:
    repo = _make_repository(tmp_path)
    readme = repo / "docs" / "modules" / "demo" / "README.md"
    original = "# Hand-authored demo\n"
    readme.write_text(original, encoding="utf-8")

    dry_run = _run(repo, "--dry-run", "--module", "demo")
    assert dry_run.returncode == 0
    assert readme.read_text(encoding="utf-8") == original
    assert "docs/modules/demo/README.md" not in dry_run.stdout

    applied = _run(
        repo,
        "--apply",
        "--module",
        "demo",
        "--force-readmes",
    )
    assert applied.returncode == 0
    assert "<!-- readme: generated -->" in readme.read_text(encoding="utf-8")
