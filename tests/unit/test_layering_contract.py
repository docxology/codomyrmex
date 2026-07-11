"""Repository-level import-linter contract guardrails."""

import tomllib
from pathlib import Path

import pytest
from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT

pytestmark = pytest.mark.unit


def test_import_linter_has_no_layer_ignore_imports() -> None:
    root = REPO_ROOT
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    contracts = data["tool"]["importlinter"]["contracts"]
    layering = next(
        contract
        for contract in contracts
        if contract["name"] == "Foundation/Core/Service/Application layering"
    )
    assert layering.get("ignore_imports", []) == []
