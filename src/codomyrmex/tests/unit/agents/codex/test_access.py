"""Tests for read-only Codex access probes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codomyrmex.agents.codex.access import (
    codex_access_is_ready,
    get_codex_access_status,
    get_codex_dispatch_catalog,
)
from codomyrmex.agents.codex.mcp_tools import (
    codex_access_status,
    codex_dispatch_catalog,
)

REPO_ROOT = Path(__file__).resolve().parents[6]


@pytest.mark.unit
def test_dispatch_catalog_classifies_known_surfaces() -> None:
    catalog = get_codex_dispatch_catalog(REPO_ROOT)

    assert catalog["status"] == "ready"
    ids = {entry["id"] for entry in catalog["dispatchers"]}
    assert "improve_src.dry_run" in ids
    assert "pai.dispatch.execute" in ids
    assert catalog["summary"]["by_classification"]["dry_run"] >= 1
    assert catalog["summary"]["by_classification"]["side_effectful"] >= 1


@pytest.mark.unit
def test_access_status_is_json_serializable() -> None:
    payload = get_codex_access_status(REPO_ROOT)

    assert payload["status"] in {"ready", "partial"}
    assert payload["surfaces"]["codex_client"]["network_call_performed"] is False
    assert "codomyrmex.codex_access_status" in payload["entrypoints"]["mcp_status_tool"]
    assert codex_access_is_ready(payload) is (payload["status"] == "ready")
    json.dumps(payload)


@pytest.mark.unit
def test_access_ready_helper_rejects_partial_payload() -> None:
    assert (
        codex_access_is_ready(
            {"status": "partial", "surface_statuses": {"pai_mcp": "ready"}}
        )
        is False
    )


@pytest.mark.unit
def test_codex_access_mcp_tools_return_read_only_payloads() -> None:
    status = codex_access_status()
    catalog = codex_dispatch_catalog()

    assert status["surfaces"]["trust_gateway"]["status"] == "ready"
    assert catalog["summary"]["total"] >= 1
    assert "read_only" in catalog["summary"]["by_classification"]
