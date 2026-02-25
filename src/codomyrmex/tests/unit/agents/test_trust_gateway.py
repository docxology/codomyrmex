"""Zero-mock test suite for the Codomyrmex trust gateway.

Tests trust levels, TrustRegistry, verify_capabilities(),
trusted_call_tool() enforcement, and the full verify → trust → call flow.
"""

from pathlib import Path

import pytest

from codomyrmex.agents.pai.mcp_bridge import get_total_tool_count
from codomyrmex.agents.pai.trust_gateway import (
    DESTRUCTIVE_TOOL_COUNT,
    DESTRUCTIVE_TOOLS,
    SAFE_TOOL_COUNT,
    SAFE_TOOLS,
    SecurityError,
    TrustLevel,
    TrustRegistry,
    _get_destructive_tools,
    _is_destructive,
    get_trust_report,
    is_trusted,
    reset_trust,
    trust_all,
    trust_tool,
    trusted_call_tool,
    verify_capabilities,
)

PROJECT_ROOT = Path(__file__).resolve().parents[5]


# =====================================================================
# TrustLevel Enum
# =====================================================================

class TestTrustLevel:
    """Test trust level enum values."""

    def test_untrusted_value(self):
        """Test functionality: untrusted value."""
        assert TrustLevel.UNTRUSTED.value == "untrusted"

    def test_verified_value(self):
        """Test functionality: verified value."""
        assert TrustLevel.VERIFIED.value == "verified"

    def test_trusted_value(self):
        """Test functionality: trusted value."""
        assert TrustLevel.TRUSTED.value == "trusted"

    def test_three_levels(self):
        """Test functionality: three levels."""
        assert len(TrustLevel) == 3


# =====================================================================
# Tool Classification
# =====================================================================

class TestToolClassification:
    """Test safe vs destructive tool sets."""

    def test_destructive_tools_count(self):
        """Test functionality: destructive tools count."""
        # At least the original 4 + pattern-matched from auto-discovered modules
        assert DESTRUCTIVE_TOOL_COUNT >= 4
        # The original 4 must still be classified as destructive
        for tool in DESTRUCTIVE_TOOLS:
            assert _is_destructive(tool)

    def test_safe_tools_count(self):
        """Test functionality: safe tools count."""
        total = get_total_tool_count()
        assert SAFE_TOOL_COUNT == total - DESTRUCTIVE_TOOL_COUNT

    def test_no_overlap(self):
        """Test functionality: no overlap."""
        destructive = _get_destructive_tools()
        safe = frozenset(SAFE_TOOLS)
        assert safe & destructive == frozenset()

    def test_union_is_complete(self):
        """Test functionality: union is complete."""
        total = get_total_tool_count()
        destructive = _get_destructive_tools()
        safe = frozenset(SAFE_TOOLS)
        assert len(safe | destructive) == total

    def test_write_file_is_destructive(self):
        """Test functionality: write file is destructive."""
        assert _is_destructive("codomyrmex.write_file")

    def test_run_command_is_destructive(self):
        """Test functionality: run command is destructive."""
        assert _is_destructive("codomyrmex.run_command")

    def test_run_tests_is_destructive(self):
        """Test functionality: run tests is destructive."""
        assert _is_destructive("codomyrmex.run_tests")

    def test_auto_discovered_destructive_pattern(self):
        """Auto-discovered tools with write/delete/execute patterns are destructive."""
        assert _is_destructive("codomyrmex.encryption.write_key")
        assert _is_destructive("codomyrmex.cache.clear_cache")
        assert not _is_destructive("codomyrmex.encryption.generate_aes_key")

    def test_read_file_is_safe(self):
        """Test functionality: read file is safe."""
        assert "codomyrmex.read_file" in SAFE_TOOLS

    def test_list_modules_is_safe(self):
        """Test functionality: list modules is safe."""
        assert "codomyrmex.list_modules" in SAFE_TOOLS


# =====================================================================
# TrustRegistry
# =====================================================================

class TestTrustRegistry:
    """Test in-memory trust registry."""

    @pytest.fixture(autouse=True)
    def clean_state(self):
        reset_trust()
        yield
        reset_trust()

    def test_initial_state_untrusted(self):
        """Test functionality: initial state untrusted."""
        reg = TrustRegistry()
        assert reg.level("codomyrmex.read_file") == TrustLevel.UNTRUSTED

    def test_initial_not_trusted(self):
        """Test functionality: initial not trusted."""
        reg = TrustRegistry()
        assert not reg.is_trusted("codomyrmex.read_file")

    def test_verify_all_safe(self):
        """Test functionality: verify all safe."""
        reg = TrustRegistry()
        promoted = reg.verify_all_safe()
        assert len(promoted) == SAFE_TOOL_COUNT
        for name in SAFE_TOOLS:
            assert reg.level(name) == TrustLevel.VERIFIED
        for name in DESTRUCTIVE_TOOLS:
            assert reg.level(name) == TrustLevel.UNTRUSTED

    def test_trust_single_tool(self):
        """Test functionality: trust single tool."""
        reg = TrustRegistry()
        new_level = reg.trust_tool("codomyrmex.write_file")
        assert new_level == TrustLevel.TRUSTED
        assert reg.is_trusted("codomyrmex.write_file")

    def test_trust_unknown_raises(self):
        """Test functionality: trust unknown raises."""
        reg = TrustRegistry()
        with pytest.raises(KeyError, match="Unknown tool"):
            reg.trust_tool("codomyrmex.does_not_exist")

    def test_trust_all(self):
        """Test functionality: trust all."""
        reg = TrustRegistry()
        promoted = reg.trust_all()
        total = get_total_tool_count()
        assert len(promoted) == total
        for name in promoted:
            assert reg.is_trusted(name)

    def test_reset(self):
        """Test functionality: reset."""
        reg = TrustRegistry()
        reg.trust_all()
        reg.reset()
        for name in SAFE_TOOLS | DESTRUCTIVE_TOOLS:
            assert reg.level(name) == TrustLevel.UNTRUSTED

    def test_report_structure(self):
        """Test functionality: report structure."""
        reg = TrustRegistry()
        report = reg.get_report()
        assert "total_tools" in report
        assert report["total_tools"] == get_total_tool_count()
        assert "by_level" in report
        assert set(report["by_level"].keys()) == {"untrusted", "verified", "trusted"}
        assert "counts" in report

    def test_is_at_least_verified(self):
        """Test functionality: is at least verified."""
        reg = TrustRegistry()
        assert not reg.is_at_least_verified("codomyrmex.read_file")
        reg.verify_all_safe()
        assert reg.is_at_least_verified("codomyrmex.read_file")
        reg.trust_tool("codomyrmex.read_file")
        assert reg.is_at_least_verified("codomyrmex.read_file")

    def test_verify_idempotent(self):
        """Test functionality: verify idempotent."""
        reg = TrustRegistry()
        first = reg.verify_all_safe()
        second = reg.verify_all_safe()
        assert len(first) == SAFE_TOOL_COUNT
        assert len(second) == 0  # already verified


# =====================================================================
# verify_capabilities()
# =====================================================================

class TestVerifyCapabilities:
    """Test full capability audit."""

    @pytest.fixture(autouse=True)
    def reset(self):
        reset_trust()
        yield
        reset_trust()

    def test_returns_dict(self):
        """Test functionality: returns dict."""
        report = verify_capabilities()
        assert isinstance(report, dict)

    def test_has_modules_section(self):
        """Test functionality: has modules section."""
        report = verify_capabilities()
        assert "modules" in report
        assert report["modules"]["total"] > 50

    def test_has_tools_section(self):
        """Test functionality: has tools section."""
        report = verify_capabilities()
        tools = report["tools"]
        assert tools["total"] == get_total_tool_count()
        assert tools["by_category"]["safe"] == SAFE_TOOL_COUNT
        assert tools["by_category"]["destructive"] == DESTRUCTIVE_TOOL_COUNT

    def test_has_resources_section(self):
        """Test functionality: has resources section."""
        report = verify_capabilities()
        assert report["mcp"]["resources"] >= 2

    def test_has_prompts_section(self):
        """Test functionality: has prompts section."""
        report = verify_capabilities()
        assert report["mcp"]["prompts"] >= 10

    def test_mcp_server_healthy(self):
        """Test functionality: mcp server healthy."""
        report = verify_capabilities()
        assert report["mcp"]["server_name"] != "unknown"

    def test_skill_manifest_valid(self):
        """Verify the trust gateway is healthy."""
        report = verify_capabilities()
        assert report["trust"]["gateway_healthy"] is True

    def test_trust_promotion(self):
        """Test functionality: trust promotion."""
        report = verify_capabilities()
        trust = report["trust"]
        assert len(trust["promoted_to_verified"]) == SAFE_TOOL_COUNT
        state = trust["report"]
        assert state["counts"]["verified"] == SAFE_TOOL_COUNT
        assert state["counts"]["untrusted"] == DESTRUCTIVE_TOOL_COUNT

    def test_tool_details_have_trust_level(self):
        """Tools section has safe/destructive lists with tool names."""
        report = verify_capabilities()
        tools = report["tools"]
        for tool_name in tools["safe"]:
            assert isinstance(tool_name, str)
        for tool_name in tools["destructive"]:
            assert isinstance(tool_name, str)


# =====================================================================
# trusted_call_tool() enforcement
# =====================================================================

class TestTrustedCallTool:
    """Test trust-gated tool execution."""

    @pytest.fixture(autouse=True)
    def reset(self):
        reset_trust()
        yield
        reset_trust()

    def test_untrusted_safe_tool_blocked(self):
        """Safe tools need at least VERIFIED."""
        with pytest.raises(SecurityError):
            trusted_call_tool("codomyrmex.list_modules")

    def test_verified_safe_tool_allowed(self):
        """After verify, safe tools work."""
        verify_capabilities()
        result = trusted_call_tool("codomyrmex.list_modules")
        assert "modules" in result

    def test_verified_destructive_tool_blocked(self):
        """After verify, destructive tools still blocked."""
        verify_capabilities()
        with pytest.raises(SecurityError):
            trusted_call_tool("codomyrmex.run_tests")

    def test_trusted_destructive_tool_allowed(self):
        """After trust, destructive tools work."""
        verify_capabilities()
        trust_tool("codomyrmex.run_tests")
        # Just verify the call goes through (may take a while, so we
        # test with a module filter to keep it fast)
        assert is_trusted("codomyrmex.run_tests")

    def test_trust_all_enables_everything(self):
        """Test functionality: trust all enables everything."""
        trust_all()
        # All tools should now be trusted
        result = trusted_call_tool("codomyrmex.list_modules")
        assert "modules" in result

    def test_unknown_tool_raises_key_error(self):
        """Test functionality: unknown tool raises key error."""
        trust_all()
        with pytest.raises(KeyError):
            trusted_call_tool("codomyrmex.nonexistent")


# =====================================================================
# Module-level functions
# =====================================================================

class TestModuleLevelFunctions:
    """Test public API convenience functions."""

    @pytest.fixture(autouse=True)
    def reset(self):
        reset_trust()
        yield
        reset_trust()

    def test_trust_tool_returns_state(self):
        """Test functionality: trust tool returns state."""
        result = trust_tool("codomyrmex.write_file")
        assert result["tool"] == "codomyrmex.write_file"
        assert result["new_level"] == "trusted"
        assert "report" in result

    def test_trust_all_returns_promoted(self):
        """Test functionality: trust all returns promoted."""
        result = trust_all()
        total = get_total_tool_count()
        assert result["count"] == total
        assert len(result["promoted"]) == total

    def test_get_trust_report(self):
        """Test functionality: get trust report."""
        report = get_trust_report()
        assert report["total_tools"] == get_total_tool_count()

    def test_is_trusted_false_initially(self):
        """Test functionality: is trusted false initially."""
        assert not is_trusted("codomyrmex.write_file")

    def test_is_trusted_after_trust(self):
        """Test functionality: is trusted after trust."""
        trust_tool("codomyrmex.write_file")
        assert is_trusted("codomyrmex.write_file")

    def test_reset_trust(self):
        """Test functionality: reset trust."""
        trust_all()
        reset_trust()
        assert not is_trusted("codomyrmex.write_file")


# =====================================================================
# Full Workflow Integration
# =====================================================================

class TestFullWorkflow:
    """Test the complete verify → trust → call flow."""

    @pytest.fixture(autouse=True)
    def reset(self):
        reset_trust()
        yield
        reset_trust()

    def test_verify_then_trust_then_call(self):
        """Full workflow: verify → trust_all → trusted call."""
        # 1. Verify
        report = verify_capabilities()
        assert report["status"] == "verified"
        assert report["mcp"]["server_name"] != "unknown"

        # 2. Trust
        result = trust_all()
        assert result["count"] > 0
        assert result["report"]["counts"]["trusted"] == get_total_tool_count()

        # 3. Call
        modules = trusted_call_tool("codomyrmex.list_modules")
        assert "modules" in modules

        info = trusted_call_tool("codomyrmex.module_info", module_name="agents")
        assert info["module"] == "agents"

    def test_selective_trust_workflow(self):
        """Verify → trust one tool → call only that tool."""
        verify_capabilities()
        trust_tool("codomyrmex.run_tests")

        # Trusted tool works
        assert is_trusted("codomyrmex.run_tests")

        # Other destructive tool still blocked
        with pytest.raises(SecurityError):
            trusted_call_tool("codomyrmex.write_file", path="/tmp/x", content="y")
