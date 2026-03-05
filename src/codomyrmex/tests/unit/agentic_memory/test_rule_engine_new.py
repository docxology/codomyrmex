"""Zero-Mock tests for RuleEngine.preload(), visualize(), and rules_visualize MCP tool.

Tests cover:
- preload() returns int count
- preload=True in constructor loads rules
- visualize() returns Mermaid diagram with expected structure
- rules_visualize MCP tool returns dict with status key

All tests use real .cursorrules files or temp hierarchies.
No mocks, stubs, or monkeypatching.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.agentic_memory.rules import RuleEngine

# The real rules directory that ships with the codebase
_RULES_ROOT = Path(__file__).resolve().parents[3] / "agentic_memory" / "rules"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rules_root():
    """Return the real rules root directory."""
    return _RULES_ROOT


@pytest.fixture
def tmp_rules(tmp_path):
    """Create a temporary rules hierarchy for isolated tests."""
    (tmp_path / "general.cursorrules").write_text(
        "# General Rules\n\n## 0. Preamble\nGeneral preamble.\n",
        encoding="utf-8",
    )
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    (modules_dir / "agents.cursorrules").write_text(
        "# Agents Module\n\n## 0. Preamble\nAgents preamble.\n",
        encoding="utf-8",
    )
    (modules_dir / "cloud.cursorrules").write_text(
        "# Cloud Module\nCloud rules.\n",
        encoding="utf-8",
    )
    cross_dir = tmp_path / "cross-module"
    cross_dir.mkdir()
    (cross_dir / "logging.cursorrules").write_text(
        "# Logging Cross-Module\nLogging rules.\n",
        encoding="utf-8",
    )
    fs_dir = tmp_path / "file-specific"
    fs_dir.mkdir()
    (fs_dir / "python.cursorrules").write_text(
        "# Python File Rules\nPython file rules.\n",
        encoding="utf-8",
    )
    return tmp_path


# ===========================================================================
# PART 1: preload()
# ===========================================================================


@pytest.mark.unit
class TestPreload:
    """Tests for RuleEngine.preload()."""

    def test_preload_returns_int(self, tmp_rules):
        """preload() should return an integer."""
        engine = RuleEngine(rules_root=tmp_rules)
        result = engine.preload()
        assert isinstance(result, int)

    def test_preload_returns_positive_count(self, tmp_rules):
        """preload() should return count > 0 when rules exist."""
        engine = RuleEngine(rules_root=tmp_rules)
        count = engine.preload()
        assert count > 0

    def test_preload_returns_zero_for_empty(self, tmp_path):
        """preload() should return 0 when no rules exist."""
        engine = RuleEngine(rules_root=tmp_path)
        count = engine.preload()
        assert count == 0

    def test_preload_count_matches_list_all(self, tmp_rules):
        """preload() count should match list_all_rules() length."""
        engine = RuleEngine(rules_root=tmp_rules)
        count = engine.preload()
        assert count == len(engine.list_all_rules())

    def test_preload_true_in_constructor(self, tmp_rules):
        """preload=True in constructor should load rules at init time."""
        engine = RuleEngine(rules_root=tmp_rules, preload=True)
        # After preload, list_all_rules should work and return rules
        rules = engine.list_all_rules()
        assert len(rules) > 0

    def test_preload_false_is_default(self, tmp_rules):
        """preload=False should be the default (no eager loading)."""
        engine = RuleEngine(rules_root=tmp_rules)
        # Engine should still work -- lazy loading
        rules = engine.list_all_rules()
        assert len(rules) > 0

    def test_preload_with_real_rules(self, rules_root):
        """preload() with real rules should return a substantial count."""
        if not (rules_root / "general.cursorrules").exists():
            pytest.skip("Real rules root not available")
        engine = RuleEngine(rules_root=rules_root)
        count = engine.preload()
        assert count > 5

    def test_preload_idempotent(self, tmp_rules):
        """Calling preload() twice should return the same count."""
        engine = RuleEngine(rules_root=tmp_rules)
        c1 = engine.preload()
        c2 = engine.preload()
        assert c1 == c2


# ===========================================================================
# PART 2: visualize()
# ===========================================================================


@pytest.mark.unit
class TestVisualize:
    """Tests for RuleEngine.visualize()."""

    def test_visualize_returns_string(self, tmp_rules):
        """visualize() should return a string."""
        engine = RuleEngine(rules_root=tmp_rules)
        result = engine.visualize()
        assert isinstance(result, str)

    def test_visualize_nonempty(self, tmp_rules):
        """visualize() should return a non-empty string."""
        engine = RuleEngine(rules_root=tmp_rules)
        result = engine.visualize()
        assert len(result) > 0

    def test_visualize_contains_graph_td(self, tmp_rules):
        """visualize() output should contain 'graph TD'."""
        engine = RuleEngine(rules_root=tmp_rules)
        result = engine.visualize()
        assert "graph TD" in result

    def test_visualize_contains_priority_levels(self, tmp_rules):
        """visualize() output should contain all four priority level names."""
        engine = RuleEngine(rules_root=tmp_rules)
        result = engine.visualize()
        assert "GENERAL" in result
        assert "CROSS_MODULE" in result
        assert "MODULE" in result
        assert "FILE_SPECIFIC" in result

    def test_visualize_contains_edges(self, tmp_rules):
        """visualize() should include the priority flow edges."""
        engine = RuleEngine(rules_root=tmp_rules)
        result = engine.visualize()
        assert "GENERAL --> CROSS_MODULE" in result
        assert "CROSS_MODULE --> MODULE" in result
        assert "MODULE --> FILE_SPECIFIC" in result

    def test_visualize_contains_rule_names(self, tmp_rules):
        """visualize() should include actual rule names from the hierarchy."""
        engine = RuleEngine(rules_root=tmp_rules)
        result = engine.visualize()
        assert "agents" in result
        assert "general" in result
        assert "python" in result

    def test_visualize_empty_rules(self, tmp_path):
        """visualize() with no rules should still produce valid Mermaid."""
        engine = RuleEngine(rules_root=tmp_path)
        result = engine.visualize()
        assert "graph TD" in result
        # Should still have the edges
        assert "GENERAL --> CROSS_MODULE" in result

    def test_visualize_with_real_rules(self, rules_root):
        """visualize() with real rules should produce a substantial diagram."""
        if not (rules_root / "general.cursorrules").exists():
            pytest.skip("Real rules root not available")
        engine = RuleEngine(rules_root=rules_root)
        result = engine.visualize()
        assert "graph TD" in result
        # Real rules should have many lines
        assert result.count("\n") > 10


# ===========================================================================
# PART 3: rules_visualize MCP tool
# ===========================================================================


@pytest.mark.unit
class TestRulesVisualizeMCPTool:
    """Tests for the rules_visualize MCP tool function."""

    def test_returns_dict(self):
        """rules_visualize should return a dict."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_visualize

        result = rules_visualize()
        assert isinstance(result, dict)

    def test_has_status_key(self):
        """rules_visualize result should contain a 'status' key."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_visualize

        result = rules_visualize()
        assert "status" in result

    def test_status_is_success(self):
        """rules_visualize status should be 'success'."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_visualize

        result = rules_visualize()
        assert result["status"] == "success"

    def test_has_diagram_key(self):
        """rules_visualize result should contain a 'diagram' key."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_visualize

        result = rules_visualize()
        assert "diagram" in result
        assert isinstance(result["diagram"], str)
        assert "graph TD" in result["diagram"]

    def test_has_rule_count_key(self):
        """rules_visualize result should contain a 'rule_count' key."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_visualize

        result = rules_visualize()
        assert "rule_count" in result
        assert isinstance(result["rule_count"], int)
        assert result["rule_count"] >= 0
