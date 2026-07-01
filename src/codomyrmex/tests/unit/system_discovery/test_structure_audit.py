"""Tests for the system_discovery structure audit."""

from pathlib import Path

import pytest

from codomyrmex.system_discovery.structure_audit import audit_module_structure

pytestmark = pytest.mark.unit


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def test_current_repo_structure_audit_passes() -> None:
    audit = audit_module_structure(_repo_root())
    assert audit.passed
    assert audit.errors == ()
    assert audit.catalog.runtime_module_count == 129
    assert audit.to_dict()["orphaned_docs_module_count"] == 0


def test_audit_reports_missing_contract_docs(tmp_path: Path) -> None:
    module = tmp_path / "src" / "codomyrmex" / "thin_module"
    module.mkdir(parents=True)
    (module / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "docs" / "modules" / "thin_module").mkdir(parents=True)
    tests = tmp_path / "src" / "codomyrmex" / "tests" / "unit" / "thin_module"
    tests.mkdir(parents=True)
    (tests / "test_thin_module.py").write_text("def test_ok():\n    assert True\n")

    audit = audit_module_structure(tmp_path)

    codes = {issue.code for issue in audit.errors}
    assert {
        "readme-missing",
        "agents-missing",
        "spec-missing",
        "pai-missing",
        "api-spec-missing",
        "py-typed-missing",
    } <= codes


def test_audit_reports_orphaned_docs_module(tmp_path: Path) -> None:
    module = tmp_path / "src" / "codomyrmex" / "live_module"
    module.mkdir(parents=True)
    (module / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "docs" / "modules" / "stale_module").mkdir(parents=True)

    audit = audit_module_structure(tmp_path)

    assert any(
        issue.code == "docs-module-orphaned" and issue.module == "stale_module"
        for issue in audit.errors
    )


def test_audit_to_markdown_reports_pass_status() -> None:
    markdown = audit_module_structure(_repo_root()).to_markdown()
    assert "# Codomyrmex Source Structure Audit" in markdown
    assert "Orphaned docs module directories: 0" in markdown
    assert "Status: PASS" in markdown
