"""Metrics helpers in ``scripts/doc_inventory.py`` (loaded by path; no package install)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]


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
