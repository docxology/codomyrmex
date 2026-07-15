"""Metrics helpers in ``scripts/doc_inventory.py`` (loaded by path; no package install)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT


def _load_doc_inventory():
    path = REPO_ROOT / "scripts" / "doc_inventory.py"
    spec = importlib.util.spec_from_file_location("_doc_inventory_under_test", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.unit
def test_count_github_workflow_yml_matches_glob() -> None:
    mod = _load_doc_inventory()
    wf_dir = REPO_ROOT / ".github" / "workflows"
    expected = sum(1 for p in wf_dir.glob("*.yml") if p.is_file())
    assert mod.count_github_workflow_yml(REPO_ROOT) == expected
    assert expected >= 1


@pytest.mark.unit
def test_collect_inventory_exposes_json_metrics_without_optional_scans() -> None:
    mod = _load_doc_inventory()

    metrics = mod.collect_inventory(REPO_ROOT)

    assert metrics["top_level_modules"] == 130
    assert metrics["runtime_mcp_tools"] is None
    assert metrics["pytest_collected"] is None


@pytest.mark.unit
def test_reference_consistency_reports_a_stale_value(tmp_path: Path) -> None:
    mod = _load_doc_inventory()
    inventory = tmp_path / "docs/reference/inventory.md"
    inventory.parent.mkdir(parents=True)
    inventory.write_text("| Top-level modules | 1 |\n", encoding="utf-8")
    metrics = {"top_level_modules": 130, "mcp_tools_py": None, "runtime_mcp_tools": None,
               "production_mcp_tool_decorators": None, "pytest_collected": None,
               "github_workflows": None, "markdown_docs_under_docs": None}

    errors = mod.reference_consistency(tmp_path, metrics)

    assert errors == ["Top-level modules: expected 130"]
