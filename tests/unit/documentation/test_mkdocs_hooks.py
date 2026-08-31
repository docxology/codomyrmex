"""Tests for the fail-closed MkDocs documentation hook."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip(
    "mkdocs", reason="mkdocs is an opt-in extra: uv sync --extra physical_management"
)
from mkdocs.exceptions import BuildError

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / "scripts" / "documentation" / "mkdocs_hooks.py"
SPEC = importlib.util.spec_from_file_location("codomyrmex_mkdocs_hooks", HOOK_PATH)
assert SPEC is not None
assert SPEC.loader is not None
HOOKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOKS)
on_post_build = HOOKS.on_post_build
rewrite_markdown_links = HOOKS.rewrite_markdown_links


def _rewrite(markdown: str, root: Path, source: Path) -> str:
    return rewrite_markdown_links(
        markdown,
        source_path=source,
        docs_dir=root / "docs",
        repo_root=root,
        repo_url="https://github.com/example/project",
        source_branch="main",
    )


def test_docs_directory_link_resolves_to_index(tmp_path: Path) -> None:
    source = tmp_path / "docs" / "guide" / "page.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Page\n", encoding="utf-8")
    target = tmp_path / "docs" / "reference"
    target.mkdir()
    (target / "index.md").write_text("# Reference\n", encoding="utf-8")

    result = _rewrite("[reference](../reference/)", tmp_path, source)

    assert result == "[reference](../reference/index.md)"


def test_readme_link_prefers_canonical_index(tmp_path: Path) -> None:
    source = tmp_path / "docs" / "page.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Page\n", encoding="utf-8")
    target = tmp_path / "docs" / "topic"
    target.mkdir()
    (target / "README.md").write_text("# Readme\n", encoding="utf-8")
    (target / "index.md").write_text("# Index\n", encoding="utf-8")

    result = _rewrite("[topic](topic/README.md#usage)", tmp_path, source)

    assert result == "[topic](topic/index.md#usage)"


@pytest.mark.parametrize(
    ("target_name", "kind"),
    [("pyproject.toml", "blob"), ("src", "tree")],
)
def test_repository_target_outside_docs_becomes_github_url(
    tmp_path: Path,
    target_name: str,
    kind: str,
) -> None:
    source = tmp_path / "docs" / "page.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Page\n", encoding="utf-8")
    target = tmp_path / target_name
    if "." in target_name:
        target.write_text("[project]\n", encoding="utf-8")
    else:
        target.mkdir()

    result = _rewrite(f"[target](../{target_name})", tmp_path, source)

    expected = f"https://github.com/example/project/{kind}/main/{target_name}"
    assert result == f"[target]({expected})"


def test_missing_targets_and_fenced_examples_are_unchanged(tmp_path: Path) -> None:
    source = tmp_path / "docs" / "page.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Page\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    markdown = "[missing](missing.md)\n```markdown\n[example](../pyproject.toml)\n```\n"

    assert _rewrite(markdown, tmp_path, source) == markdown


def test_reference_style_link_is_rewritten(tmp_path: Path) -> None:
    source = tmp_path / "docs" / "page.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Page\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("license\n", encoding="utf-8")

    result = _rewrite('[license]: ../LICENSE "License text"\n', tmp_path, source)

    assert result == (
        "[license]: https://github.com/example/project/blob/main/LICENSE "
        '"License text"\n'
    )


def test_post_build_fails_closed_without_generated_report(tmp_path: Path) -> None:
    config = {
        "config_file_path": str(tmp_path / "mkdocs.yml"),
        "site_dir": str(tmp_path / "site"),
        "extra": {"technical_report_source": "output/paper.html"},
    }

    with pytest.raises(BuildError, match="Generated semantic report is required"):
        on_post_build(config=config)


def test_post_build_copies_validated_semantic_report(tmp_path: Path) -> None:
    report = tmp_path / "output" / "paper.html"
    report.parent.mkdir(parents=True)
    report.write_text(
        "<!DOCTYPE html><title>Codomyrmex: Report</title>"
        '<figure aria-describedby="fig:one"></figure>',
        encoding="utf-8",
    )
    config = {
        "config_file_path": str(tmp_path / "mkdocs.yml"),
        "site_dir": str(tmp_path / "site"),
        "extra": {"technical_report_source": "output/paper.html"},
    }

    on_post_build(config=config)

    installed = tmp_path / "site" / "manuscript" / "technical-report.html"
    assert installed.read_bytes() == report.read_bytes()
