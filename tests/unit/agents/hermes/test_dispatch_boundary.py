"""Hermes local dispatch guardrails."""

from pathlib import Path

import pytest
from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT

from codomyrmex.agents.hermes._dispatch import filter_agent_names, spawn_agent

pytestmark = pytest.mark.unit


def _repo_root() -> Path:
    return REPO_ROOT


def test_filter_agent_names_uses_role_prefixes() -> None:
    assert filter_agent_names(
        ["reviewer_fast", "writer"],
        {"review": ["reviewer"]},
        "review",
    ) == ["reviewer_fast"]


def test_spawn_agent_preserves_success_shape() -> None:
    result = spawn_agent(
        "review",
        "check this",
        agents={"reviewer_fast": lambda task: {"task": task}},
        capability_profile={"review": ["reviewer"]},
    )

    assert result["status"] == "success"
    assert result["role"] == "review"
    assert result["agent"] == "reviewer_fast"
    assert result["result"] == {"task": "check this"}


def test_hermes_mcp_tools_do_not_import_orchestrator() -> None:
    text = (_repo_root() / "src/codomyrmex/agents/hermes/mcp_tools.py").read_text(
        encoding="utf-8"
    )
    assert "codomyrmex.orchestrator.integration" not in text
