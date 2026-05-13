"""Tests for triple-check completeness repair helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from codomyrmex.documentation.scripts.repair_triple_check_completeness import (
    _collect_doc_files,
    repair_content,
    repair_tree,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.unit
def test_repair_content_adds_metadata_navigation_and_notes(tmp_path: Path) -> None:
    readme = tmp_path / "module" / "README.md"
    readme.parent.mkdir()
    (readme.parent / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (readme.parent / "SPEC.md").write_text("# Spec\n", encoding="utf-8")

    updated, stats = repair_content("# Module\n\nShort.\n", readme, tmp_path)

    assert stats.changed == 1
    assert stats.metadata_added == 1
    assert stats.navigation_added == 1
    assert stats.maintenance_added == 1
    assert "**Version**" in updated
    assert "**Status**" in updated
    assert "## Navigation" in updated
    assert "AGENTS.md" in updated
    assert "SPEC.md" in updated
    assert "## Validation Notes" in updated


@pytest.mark.unit
def test_repair_content_is_idempotent(tmp_path: Path) -> None:
    spec = tmp_path / "module" / "SPEC.md"
    spec.parent.mkdir()
    (spec.parent / "README.md").write_text("# Readme\n", encoding="utf-8")
    (spec.parent / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")

    once, first_stats = repair_content("# Spec\n\nBody.\n", spec, tmp_path)
    twice, second_stats = repair_content(once, spec, tmp_path)

    assert first_stats.changed == 1
    assert second_stats.changed == 0
    assert twice == once


@pytest.mark.unit
def test_collect_doc_files_skips_gitmodules_by_default(tmp_path: Path) -> None:
    (tmp_path / ".gitmodules").write_text(
        '[submodule "vendor/pkg"]\n\tpath = vendor/pkg\n', encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("# Root\n", encoding="utf-8")
    vendor = tmp_path / "vendor" / "pkg"
    vendor.mkdir(parents=True)
    (vendor / "README.md").write_text("# Vendor\n", encoding="utf-8")

    collected = {path.relative_to(tmp_path).as_posix() for path in _collect_doc_files(tmp_path, False)}

    assert collected == {"README.md"}


@pytest.mark.unit
def test_repair_tree_dry_run_does_not_write(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# Root\n\nShort.\n", encoding="utf-8")

    stats = repair_tree(tmp_path, dry_run=True, include_submodules=False)

    assert stats.changed == 1
    assert readme.read_text(encoding="utf-8") == "# Root\n\nShort.\n"
