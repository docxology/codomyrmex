"""Regression tests for the repository dependency graph normalizer."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT


@pytest.fixture(scope="module")
def dependency_module():
    script = REPO_ROOT / "scripts" / "validation" / "dependency_analyzer.py"
    spec = importlib.util.spec_from_file_location("dependency_analyzer", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_dependency_graph_excludes_test_support_nodes(
    dependency_module, tmp_path: Path
):
    source_root = tmp_path / "src" / "codomyrmex"
    (source_root / "alpha").mkdir(parents=True)
    (source_root / "beta").mkdir()
    (source_root / "__init__.py").write_text("", encoding="utf-8")
    (source_root / "conftest.py").write_text("pytest_plugins = []\n", encoding="utf-8")
    (source_root / "alpha" / "__init__.py").write_text(
        "from codomyrmex.beta import value\n", encoding="utf-8"
    )
    (source_root / "beta" / "__init__.py").write_text("value = 1\n", encoding="utf-8")

    graph = dependency_module.build_dependency_graph(source_root)

    assert "codomyrmex" not in graph
    assert "conftest" not in graph
    assert {module.split(".")[0] for module in graph} == {"alpha", "beta"}
    assert graph["alpha"] == {"beta"}
