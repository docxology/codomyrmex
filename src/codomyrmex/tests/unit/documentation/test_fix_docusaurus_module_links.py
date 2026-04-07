"""Unit tests for scripts/documentation/fix_docusaurus_module_links.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture(scope="module")
def fixer_mod():
    script = REPO_ROOT / "scripts" / "documentation" / "fix_docusaurus_module_links.py"
    assert script.is_file(), f"missing {script}"
    spec = importlib.util.spec_from_file_location("fix_docusaurus_module_links", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.unit
def test_transform_content_rewrites_spec_pai_mcp(fixer_mod, tmp_path: Path) -> None:
    root = tmp_path
    (root / "docs" / "modules" / "footest").mkdir(parents=True)
    (root / "docs" / "modules" / "footest" / "SPEC.md").write_text("# spec\n", encoding="utf-8")
    (root / "docs" / "modules" / "footest" / "PAI.md").write_text("# pai\n", encoding="utf-8")
    (root / "src" / "codomyrmex" / "footest").mkdir(parents=True)
    (root / "src" / "codomyrmex" / "footest" / "mcp_tools.py").write_text("#\n", encoding="utf-8")

    parent = root / "src" / "codomyrmex" / "documentation" / "docs" / "modules" / "footest"
    parent.mkdir(parents=True)
    text = "See [s](SPEC.md#h) [p](PAI.md) [m](mcp_tools.py)\n"
    out = fixer_mod.transform_content(text, "footest", parent, root)
    assert "](SPEC.md" not in out
    assert "docs/modules/footest/SPEC.md#h" in out
    assert "docs/modules/footest/PAI.md" in out
    assert "src/codomyrmex/footest/mcp_tools.py" in out


@pytest.mark.unit
def test_transform_content_idempotent_after_rewrite(fixer_mod, tmp_path: Path) -> None:
    root = tmp_path
    (root / "docs" / "modules" / "footest").mkdir(parents=True)
    (root / "docs" / "modules" / "footest" / "SPEC.md").write_text("#\n", encoding="utf-8")
    (root / "docs" / "modules" / "footest" / "PAI.md").write_text("#\n", encoding="utf-8")
    parent = root / "src" / "codomyrmex" / "documentation" / "docs" / "modules" / "footest"
    parent.mkdir(parents=True)
    first = fixer_mod.transform_content("[x](SPEC.md)", "footest", parent, root)
    second = fixer_mod.transform_content(first, "footest", parent, root)
    assert first == second


@pytest.mark.unit
def test_hrefs_fallback_docs_pai_when_module_pai_missing(fixer_mod, tmp_path: Path) -> None:
    root = tmp_path
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "PAI.md").write_text("#\n", encoding="utf-8")
    (root / "docs" / "modules" / "nomodpai").mkdir(parents=True)
    (root / "docs" / "modules" / "nomodpai" / "SPEC.md").write_text("#\n", encoding="utf-8")
    parent = root / "src" / "codomyrmex" / "documentation" / "docs" / "modules" / "nomodpai"
    parent.mkdir(parents=True)
    spec_h, pai_h, mcp_h = fixer_mod.hrefs_for_module("nomodpai", parent, root)
    assert spec_h is not None and "docs/modules/nomodpai/SPEC.md" in spec_h
    assert "docs/PAI.md" in pai_h
    assert mcp_h is None


@pytest.mark.unit
def test_prefix_for_depth_matches_parent_under_root(fixer_mod, tmp_path: Path) -> None:
    root = tmp_path
    parent = root / "a" / "b" / "c"
    parent.mkdir(parents=True)
    pre = fixer_mod.prefix_for(parent, root)
    assert pre == "../../../"
