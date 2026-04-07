"""Unit tests for scripts/documentation/validate_links_comprehensive.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture(scope="module")
def links_mod():
    script = REPO_ROOT / "scripts" / "documentation" / "validate_links_comprehensive.py"
    assert script.is_file(), f"missing {script}"
    spec = importlib.util.spec_from_file_location("validate_links_comprehensive", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.unit
def test_lines_outside_fences_excludes_fenced_lines(links_mod) -> None:
    content = """intro
```
[ignore](bad.md)
```
[keep](good.md)
"""
    lines = links_mod._lines_outside_fences(content)
    by_num = {n: line for n, line in lines}
    assert "[keep](good.md)" in by_num.get(5, "")
    assert not any("ignore" in line for _, line in lines)


@pytest.mark.unit
def test_extract_links_skips_links_inside_fences(links_mod, tmp_path: Path) -> None:
    f = tmp_path / "x.md"
    content = """Before
```
[a](in_fence.md)
```
[b](out_fence.md)
"""
    found = links_mod.extract_links(content, f)
    urls = [u for u, _ in found]
    assert "in_fence.md" not in urls
    assert "out_fence.md" in urls


@pytest.mark.unit
def test_validate_link_external(links_mod, tmp_path: Path) -> None:
    f = tmp_path / "a.md"
    f.write_text("x", encoding="utf-8")
    r = links_mod.validate_link("https://example.com/x", f, tmp_path, 1)
    assert r.status == "external"


@pytest.mark.unit
def test_validate_link_anchor_only(links_mod, tmp_path: Path) -> None:
    f = tmp_path / "a.md"
    f.write_text("x", encoding="utf-8")
    r = links_mod.validate_link("#section", f, tmp_path, 1)
    assert r.status == "ok"


@pytest.mark.unit
def test_validate_link_missing_target_broken(links_mod, tmp_path: Path) -> None:
    f = tmp_path / "a.md"
    f.write_text("[x](nope.md)", encoding="utf-8")
    r = links_mod.validate_link("nope.md", f, tmp_path, 1)
    assert r.status == "broken"


@pytest.mark.unit
def test_validate_link_existing_relative_ok(links_mod, tmp_path: Path) -> None:
    (tmp_path / "other.md").write_text("y", encoding="utf-8")
    f = tmp_path / "a.md"
    f.write_text("[x](other.md)", encoding="utf-8")
    r = links_mod.validate_link("other.md", f, tmp_path, 1)
    assert r.status == "ok"
