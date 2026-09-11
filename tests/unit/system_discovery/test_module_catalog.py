"""Tests for the system_discovery module catalog."""

from pathlib import Path

import pytest
from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT

from codomyrmex.system_discovery.module_catalog import (
    ModuleCatalogEntry,
    build_module_catalog,
)

pytestmark = pytest.mark.unit


def _repo_root() -> Path:
    return REPO_ROOT


def test_catalog_counts_runtime_modules_without_tests_surface() -> None:
    root = _repo_root()
    catalog = build_module_catalog(root)
    expected = sum(
        1
        for path in (root / "src" / "codomyrmex").iterdir()
        if path.is_dir()
        and path.name not in {"__pycache__", "tests"}
        and (path / "__init__.py").is_file()
    )
    assert catalog.runtime_module_count == expected
    assert "tests" in {entry.name for entry in catalog.support_surfaces}


def test_catalog_has_no_retired_architecture_entry() -> None:
    catalog = build_module_catalog(_repo_root())
    names = {entry.name for entry in catalog.entries}
    parts = ("ghost", "architecture")
    retired_name = parts[0] + "_" + parts[1]
    assert retired_name not in names


def test_mcp_tool_modules_have_specs() -> None:
    catalog = build_module_catalog(_repo_root())
    assert catalog.mcp_tool_modules_missing_specs == ()


def test_has_mcp_contract_gap() -> None:
    def make_entry(*, has_mcp_tools: bool, has_mcp_spec: bool) -> ModuleCatalogEntry:
        return ModuleCatalogEntry(
            name="dummy",
            relative_path="dummy",
            kind="runtime_module",
            has_init=True,
            has_readme=True,
            has_agents=True,
            has_spec=True,
            has_pai=True,
            has_api_spec=True,
            has_mcp_tools=has_mcp_tools,
            has_mcp_spec=has_mcp_spec,
            has_py_typed=True,
            has_tests=True,
            docs_module_exists=True,
        )

    # Missing spec when tools exist is a gap
    entry1 = make_entry(has_mcp_tools=True, has_mcp_spec=False)
    assert entry1.has_mcp_contract_gap is True

    # Has spec when tools exist is not a gap
    entry2 = make_entry(has_mcp_tools=True, has_mcp_spec=True)
    assert entry2.has_mcp_contract_gap is False

    # No tools and no spec is not a gap
    entry3 = make_entry(has_mcp_tools=False, has_mcp_spec=False)
    assert entry3.has_mcp_contract_gap is False

    # No tools but has spec is not a gap (though perhaps unusual)
    entry4 = make_entry(has_mcp_tools=False, has_mcp_spec=True)
    assert entry4.has_mcp_contract_gap is False


def test_config_audits_has_api_spec() -> None:
    catalog = build_module_catalog(_repo_root())
    assert "config_audits" not in catalog.api_spec_missing


def test_runtime_modules_have_py_typed_markers() -> None:
    catalog = build_module_catalog(_repo_root())
    assert catalog.py_typed_missing == ()


def test_docs_modules_have_source_entries() -> None:
    catalog = build_module_catalog(_repo_root())
    assert catalog.docs_module_count == len(catalog.docs_module_names)
    assert catalog.docs_modules_without_source_entries == ()


def test_catalog_to_dict_is_json_ready() -> None:
    data = build_module_catalog(_repo_root()).to_dict()
    assert data["runtime_module_count"] > 0
    assert data["docs_modules_without_source_entries"] == []
    assert data["py_typed_missing"] == []
    assert isinstance(data["entries"], list)
    assert all(isinstance(entry["name"], str) for entry in data["entries"])


def test_system_discovery_exports_catalog_and_structure_commands() -> None:
    from codomyrmex import system_discovery

    assert system_discovery.build_module_catalog is build_module_catalog
    assert callable(system_discovery.audit_module_structure)

    commands = system_discovery.cli_commands()
    assert {"catalog", "structure"} <= set(commands)
    assert callable(commands["catalog"]["handler"])
    assert callable(commands["structure"]["handler"])
