"""Zero-mock tests for the read-only agent capability catalog."""

import json

import pytest

from codomyrmex.agents.navigation.catalog import (
    CapabilityCatalog,
    CapabilityRecord,
    _module_doc_path,
    build_capability_catalog,
)
from codomyrmex.agents.pai.mcp.trust_metadata import is_destructive_tool


def test_catalog_has_deterministic_agent_and_module_records():
    catalog = build_capability_catalog()
    records = catalog.list(limit=500)
    assert records
    assert catalog.get("agent:claude") is not None
    assert catalog.get("claude") == catalog.get("agent:claude")
    assert [record.id for record in records] == [
        record.id
        for record in sorted(records, key=lambda item: (item.kind, item.name, item.id))
    ]


def test_catalog_search_and_limits_are_stable():
    catalog = build_capability_catalog()
    results = catalog.search("claude", kind="agent", limit=1)
    assert len(results) == 1
    assert results[0].id == "agent:claude"
    assert len(catalog.list(limit=0)) == 1


def test_catalog_metadata_does_not_include_probe_results_or_handlers():
    record = build_capability_catalog().get("agent:claude")
    assert record is not None
    payload = record.to_dict()
    assert payload["details"]["live_probe_performed"] is False
    assert "sk-" not in repr(payload)
    assert all(not callable(value) for value in payload.values())
    assert payload["provenance"]["metadata_only"] is True
    assert payload["details"]["construction_verified"] is False


def test_tool_catalog_is_explicitly_opt_in():
    catalog = build_capability_catalog()
    assert not catalog.list(kind="tool", include_unavailable=True, limit=500)


def test_tool_trust_metadata_matches_shared_destructive_policy():
    assert is_destructive_tool("codomyrmex.deserialize_data") is True
    assert is_destructive_tool("codomyrmex.cache.clear_cache") is True
    assert is_destructive_tool("codomyrmex.cache.get_stats") is False

    catalog = build_capability_catalog(include_tools=True)
    record = catalog.get("tool:codomyrmex.deserialize_data")
    assert record is not None
    assert record.trust == "restricted"
    assert record.details["destructive"] is True


def test_catalog_rejects_ambiguous_inputs_and_searches_documentation():
    catalog = build_capability_catalog()
    with pytest.raises(ValueError, match="limit must be an integer"):
        catalog.list(limit="10")
    with pytest.raises(ValueError, match="include_unavailable must be a boolean"):
        catalog.list(include_unavailable="yes")
    with pytest.raises(ValueError, match="capability_id must be a string"):
        catalog.get(None)
    with pytest.raises(ValueError, match="query must not be empty"):
        catalog.search("   ")
    with pytest.raises(ValueError, match="searchable characters"):
        catalog.search("!!!")
    assert catalog.search("docs/agents/claude", kind="agent")


def test_catalog_serialization_is_json_safe_and_empty_state_is_explicit():
    record = CapabilityRecord(
        id="module:example",
        kind="module",
        name="example",
        display_name="Example",
        description="Example",
        status="available",
        source="src/codomyrmex/example",
        details={"values": {3, 1}, "unknown": object(), "not_finite": float("nan")},
    )
    payload = record.to_dict()
    json.dumps(payload, allow_nan=False)
    assert payload["details"]["values"] == [1, 3]
    assert payload["details"]["unknown"]["unsupported_type"] == "builtins.object"
    assert payload["details"]["not_finite"] == "nan"

    summary = CapabilityCatalog(()).summary()
    assert summary["catalog_state"] == "empty"
    assert summary["count"] == 0


def test_catalog_provenance_and_documentation_claims_are_source_bound():
    catalog = build_capability_catalog()
    summary = catalog.summary()
    assert summary["provenance"] == {
        "live_probes_performed": False,
        "mode": "metadata_only",
        "schema_version": 1,
        "sources": ["agent_registry", "package_filesystem"],
        "tool_discovery_requested": False,
    }
    ollama = catalog.get("agent:ollama")
    assert ollama is not None
    assert ollama.documentation is None
    assert all(not record.source.startswith("/") for record in catalog.list(limit=500))


def test_catalog_can_disambiguate_bare_names_by_kind():
    records = (
        CapabilityRecord(
            id="agent:shared",
            kind="agent",
            name="shared",
            display_name="Shared agent",
            description="agent",
            status="declared",
            source="agent registry",
        ),
        CapabilityRecord(
            id="module:shared",
            kind="module",
            name="shared",
            display_name="Shared module",
            description="module",
            status="available",
            source="src/codomyrmex/shared",
        ),
    )
    catalog = CapabilityCatalog(records)
    assert catalog.get("shared") is None
    assert catalog.get("shared", kind="agent") == catalog.get("agent:shared")
    assert [record.id for record in catalog.find("shared")] == [
        "agent:shared",
        "module:shared",
    ]


def test_search_scans_beyond_the_page_limit():
    records = tuple(
        [
            CapabilityRecord(
                id=f"tool:capability_{index:03d}",
                kind="tool",
                name=f"capability_{index:03d}",
                display_name=f"Capability {index}",
                description="ordinary capability",
                status="available",
                source="test",
            )
            for index in range(600)
        ]
        + [
            CapabilityRecord(
                id="tool:wallet_list",
                kind="tool",
                name="wallet_list",
                display_name="Wallet list",
                description="list wallet records",
                status="available",
                source="test",
            )
        ]
    )
    catalog = CapabilityCatalog(records)

    results = catalog.search("wallet", kind="tool", limit=1)

    assert [record.id for record in results] == ["tool:wallet_list"]


def test_tool_documentation_paths_reject_traversal_like_module_names():
    assert _module_doc_path("codomyrmex.agents.mcp_tools") == (
        "src/codomyrmex/agents/README.md"
    )
    assert _module_doc_path("codomyrmex..outside") is None
    assert _module_doc_path("codomyrmex.agents/../../outside") is None
