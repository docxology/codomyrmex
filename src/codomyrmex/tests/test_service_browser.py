"""Unit tests for service browser resource completeness.

# Feature: local-web-viewer
# Tests Property 1 from the design document.

Validates that each resource type returned by the DataProvider
contains all required fields.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.website.data_provider import DataProvider

# ── Property 1: Service browser resource completeness ──────────────
# Feature: local-web-viewer, Property 1: Service browser resource completeness
# Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6


@pytest.fixture(scope="module")
def provider():
    return DataProvider(root_dir=Path("."))


def test_property1_modules_have_required_fields(provider: DataProvider) -> None:
    """Each module SHALL have name, status, and description."""
    modules = provider.get_modules()
    assert len(modules) > 0, "Expected at least one module"
    for mod in modules:
        assert "name" in mod, f"Module missing 'name': {mod}"
        assert "status" in mod, f"Module {mod.get('name')} missing 'status'"
        assert "description" in mod, f"Module {mod.get('name')} missing 'description'"


def test_property1_agents_have_required_fields(provider: DataProvider) -> None:
    """Each agent SHALL have name, type, and description."""
    agents = provider.get_actual_agents()
    assert len(agents) > 0, "Expected at least one agent"
    for agent in agents:
        assert "name" in agent, f"Agent missing 'name': {agent}"
        assert "type" in agent, f"Agent {agent.get('name')} missing 'type'"
        name = agent.get("name")
        assert "description" in agent, f"Agent {name} missing 'description'"


def test_property1_scripts_have_required_fields(provider: DataProvider) -> None:
    """Each script SHALL have name and description."""
    scripts = provider.get_available_scripts()
    assert len(scripts) > 0, "Expected at least one script"
    for script in scripts:
        assert "name" in script, f"Script missing 'name': {script}"
        name = script.get("name")
        assert "description" in script, f"Script {name} missing 'description'"


def test_property1_tools_have_required_fields(provider: DataProvider) -> None:
    """Each tool SHALL have name and description."""
    tools_data = provider.get_mcp_tools()
    # Tools may be empty if MCP bridge isn't available, which is fine
    for tool in tools_data.get("tools", []):
        assert "name" in tool, f"Tool missing 'name': {tool}"
        assert "description" in tool, f"Tool {tool.get('name')} missing 'description'"
