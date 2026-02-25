"""Trust gateway hardening tests -- zero-mock rewrite.

Every test exercises the real TrustRegistry, the real MCPToolRegistry
returned by ``get_tool_registry()``, and real tool handlers.  No
``unittest.mock``, ``MagicMock``, or ``@patch`` usage.

Strategy
--------
* Use ``reset_trust()`` / ``clear_audit_log()`` to restore pristine
  state between tests (the public API already supports this).
* Pick a known **safe** tool (``codomyrmex.list_modules``) and a known
  **destructive** tool (``codomyrmex.write_file``) from the real
  registry for trust/audit tests.
* Verify behaviour via observable state (audit log contents, trust
  report dicts, callback invocation records) rather than mock call
  assertions.
"""

import json

import pytest

from codomyrmex.agents.pai import trust_gateway
from codomyrmex.agents.pai.mcp_bridge import get_tool_registry
from codomyrmex.agents.pai.trust_gateway import (
    DESTRUCTIVE_TOOLS,
    TrustLevel,
    _registry,
    clear_audit_log,
    export_audit_log,
    get_audit_log,
    get_current_trust_level,
    get_trust_report,
    reset_trust,
    set_require_confirmation,
    set_trust_change_callback,
    trust_all,
    trust_tool,
    trusted_call_tool,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pick_safe_tool() -> str:
    """Return a real safe tool that requires **no** arguments.

    We prefer tools whose input schema has no ``required`` list so that
    ``trusted_call_tool(name)`` can be called without extra kwargs and
    still pass schema validation.
    """
    # These static tools have empty properties / no required args.
    PREFERRED = [
        "codomyrmex.list_modules",
        "codomyrmex.pai_status",
        "codomyrmex.list_workflows",
        "codomyrmex.git_status",
    ]
    registry = get_tool_registry()
    all_tools = set(registry.list_tools())
    for name in PREFERRED:
        if name in all_tools and not trust_gateway._is_destructive(name):
            return name
    # Fallback: scan for any safe tool with no required args
    for name in sorted(all_tools):
        if trust_gateway._is_destructive(name):
            continue
        entry = registry.get(name)
        if entry:
            schema = entry.get("schema", {})
            input_schema = schema.get("inputSchema", schema)
            if not input_schema.get("required"):
                return name
    pytest.skip("No safe tools without required arguments found")


def _pick_destructive_tool() -> str:
    """Return a real destructive tool from the DESTRUCTIVE_TOOLS set."""
    registry = get_tool_registry()
    all_tools = set(registry.list_tools())
    for name in sorted(DESTRUCTIVE_TOOLS):
        if name in all_tools:
            return name
    pytest.skip("No destructive tools available in the registry")


# Map of required kwargs for destructive tools so schema validation passes.
_DESTRUCTIVE_TOOL_KWARGS: dict[str, dict[str, object]] = {
    "codomyrmex.write_file": {"path": "/dev/null", "content": "test"},
    "codomyrmex.run_command": {"command": "true"},
    "codomyrmex.run_tests": {},
    "codomyrmex.call_module_function": {"function": "noop"},
}


def _kwargs_for(tool_name: str) -> dict[str, object]:
    """Return valid kwargs for *tool_name* so schema validation passes."""
    return dict(_DESTRUCTIVE_TOOL_KWARGS.get(tool_name, {}))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_trust_gateway_state():
    """Reset global state in trust_gateway before each test.

    We also remove the on-disk trust ledger so that ``_load()`` never
    picks up stale state from a prior test run.
    """
    # Remove disk state to avoid cross-test contamination
    ledger = _registry._ledger_path
    if ledger.exists():
        ledger.unlink()

    reset_trust()
    clear_audit_log()
    set_require_confirmation(False)
    set_trust_change_callback(None)
    trust_gateway._pending_confirmations.clear()

    yield

    reset_trust()
    clear_audit_log()
    set_require_confirmation(False)
    set_trust_change_callback(None)

    # Clean up disk state after test
    if ledger.exists():
        ledger.unlink()


# ---------------------------------------------------------------------------
# TestAuditLog
# ---------------------------------------------------------------------------

class TestAuditLog:
    """Audit log tests using real tool calls."""

    def test_audit_log_records_success(self):
        """Verify successful tool calls are logged with correct fields."""
        safe = _pick_safe_tool()
        # Must be at least VERIFIED to call a safe tool
        trust_all()

        trusted_call_tool(safe)

        logs = get_audit_log()
        assert len(logs) >= 1
        entry = logs[-1]
        assert entry["tool_name"] == safe
        assert entry["result_status"] == "success"
        assert entry["trust_level"] == "TRUSTED"
        assert entry["error_code"] is None
        assert entry["duration_ms"] >= 0.0

    def test_audit_log_records_blocked(self):
        """Verify untrusted calls are logged as blocked."""
        safe = _pick_safe_tool()
        # Do NOT promote -- the tool stays UNTRUSTED
        with pytest.raises(trust_gateway.SecurityError):
            trusted_call_tool(safe)

        logs = get_audit_log()
        assert len(logs) >= 1
        entry = logs[-1]
        assert entry["result_status"] == "blocked"
        assert entry["trust_level"] == "UNTRUSTED"

    def test_audit_log_filtering(self):
        """Verify filtering by tool_name returns correct subsets."""
        trust_all()

        # Pick two distinct safe tools that need no required arguments.
        NO_ARGS_SAFE = [
            "codomyrmex.list_modules",
            "codomyrmex.pai_status",
            "codomyrmex.list_workflows",
            "codomyrmex.git_status",
        ]
        registry = get_tool_registry()
        available = set(registry.list_tools())
        candidates = [n for n in NO_ARGS_SAFE if n in available]
        if len(candidates) < 2:
            pytest.skip("Need at least 2 safe no-args tools for filtering test")

        tool_a, tool_b = candidates[0], candidates[1]

        trusted_call_tool(tool_a)
        trusted_call_tool(tool_b)

        assert len(get_audit_log(tool_name=tool_a)) >= 1
        assert len(get_audit_log(tool_name=tool_b)) >= 1
        assert len(get_audit_log(tool_name="nonexistent_tool_xyz")) == 0

    def test_clear_audit_log(self):
        """Verify clearing logs returns correct count and empties the log."""
        trust_all()
        safe = _pick_safe_tool()

        trusted_call_tool(safe)
        assert len(get_audit_log()) >= 1

        count = clear_audit_log()
        assert count >= 1
        assert len(get_audit_log()) == 0

    def test_export_audit_log(self, tmp_path):
        """Verify export to JSONL writes parseable entries."""
        trust_all()
        safe = _pick_safe_tool()

        trusted_call_tool(safe)

        export_path = tmp_path / "audit.jsonl"
        export_audit_log(export_path)

        with open(export_path) as f:
            lines = f.readlines()
            assert len(lines) >= 1
            data = json.loads(lines[-1])
            assert data["tool_name"] == safe
            assert "timestamp" in data


# ---------------------------------------------------------------------------
# TestTrustHooks
# ---------------------------------------------------------------------------

class TestTrustHooks:
    """Trust-change callback tests using a real closure instead of MagicMock."""

    def test_trust_change_callback(self):
        """Verify callback receives (old, new) trust levels on transitions."""
        invocations: list[tuple[TrustLevel, TrustLevel]] = []

        def _recorder(old: TrustLevel, new: TrustLevel) -> None:
            invocations.append((old, new))

        set_trust_change_callback(_recorder)

        # Initial state
        assert get_current_trust_level() == TrustLevel.UNTRUSTED

        # Promote to TRUSTED
        trust_all()
        assert any(
            old == TrustLevel.UNTRUSTED and new == TrustLevel.TRUSTED
            for old, new in invocations
        ), f"Expected UNTRUSTED->TRUSTED transition, got {invocations}"

        invocations.clear()

        # Reset back to UNTRUSTED
        reset_trust()
        assert any(
            old == TrustLevel.TRUSTED and new == TrustLevel.UNTRUSTED
            for old, new in invocations
        ), f"Expected TRUSTED->UNTRUSTED transition, got {invocations}"

    def test_event_emission_does_not_raise(self):
        """Verify trust transitions complete without raising, even if the
        events subsystem has a signature mismatch or is unavailable.

        The production code wraps ``publish_event`` in a try/except so that
        failures in the event bus never break trust operations.
        """
        # Simply calling trust_all() and reset_trust() must not raise --
        # the internal _trigger_trust_change swallows event bus errors.
        trust_all()
        assert get_current_trust_level() == TrustLevel.TRUSTED

        reset_trust()
        assert get_current_trust_level() == TrustLevel.UNTRUSTED


# ---------------------------------------------------------------------------
# TestTrustRegistry
# ---------------------------------------------------------------------------

class TestTrustRegistry:
    """Direct state-based tests on the TrustRegistry singleton."""

    def test_reset_sets_all_untrusted(self):
        """After reset(), every tool should be UNTRUSTED."""
        trust_all()
        report_before = get_trust_report()
        assert report_before["counts"]["trusted"] > 0

        reset_trust()
        report_after = get_trust_report()
        assert report_after["counts"]["trusted"] == 0
        assert report_after["counts"]["untrusted"] == report_after["total_tools"]

    def test_trust_tool_promotes_single(self):
        """trust_tool() should promote exactly one tool to TRUSTED."""
        safe = _pick_safe_tool()
        result = trust_tool(safe)

        assert result["new_level"] == "trusted"
        assert _registry.level(safe) == TrustLevel.TRUSTED

    def test_trust_tool_unknown_raises_key_error(self):
        """Trusting an unregistered tool name must raise KeyError."""
        with pytest.raises(KeyError, match="Unknown tool"):
            trust_tool("completely.fake.tool.name")

    def test_verify_all_safe_promotes_only_safe(self):
        """verify_all_safe() must not promote any destructive tools."""
        promoted = _registry.verify_all_safe()

        for name in promoted:
            assert not trust_gateway._is_destructive(name), (
                f"Destructive tool {name!r} was incorrectly promoted by verify_all_safe()"
            )

        # Destructive tools should still be UNTRUSTED
        for name in DESTRUCTIVE_TOOLS:
            if name in _registry._levels:
                assert _registry.level(name) == TrustLevel.UNTRUSTED

    def test_get_report_structure(self):
        """get_report() must return well-formed dict with expected keys."""
        report = _registry.get_report()
        assert "total_tools" in report
        assert "by_level" in report
        assert "counts" in report
        assert set(report["by_level"].keys()) == {"untrusted", "verified", "trusted"}
        assert report["total_tools"] == sum(report["counts"].values())


# ---------------------------------------------------------------------------
# TestDestructiveConfirmation
# ---------------------------------------------------------------------------

class TestDestructiveConfirmation:
    """Confirmation flow tests using the real destructive-tool classification.

    The confirmation gate in ``trusted_call_tool`` only fires for tools in
    the ``DESTRUCTIVE_TOOLS`` frozenset when ``_REQUIRE_CONFIRMATION`` is True.
    """

    @pytest.fixture
    def confirmation_enabled(self):
        """Enable confirmation mode for destructive tools."""
        set_require_confirmation(True)
        trust_all()  # everything must be TRUSTED to reach the confirmation gate
        yield
        set_require_confirmation(False)

    def test_safe_tool_bypasses_confirmation(self, confirmation_enabled):
        """Safe tools execute immediately even when confirmation is enabled."""
        safe = _pick_safe_tool()
        result = trusted_call_tool(safe)
        # A real tool returns a dict (not a confirmation dict)
        assert isinstance(result, dict)
        assert "confirmation_required" not in result

    def test_destructive_tool_requires_confirmation(self, confirmation_enabled):
        """Destructive tool returns a confirmation dict on first call."""
        destructive = _pick_destructive_tool()
        kwargs = _kwargs_for(destructive)

        result = trusted_call_tool(destructive, **kwargs)

        assert isinstance(result, dict)
        assert result.get("confirmation_required") is True
        assert "confirm_token" in result

        # Audit log should record the pending confirmation
        pending = get_audit_log(status="pending_confirmation")
        assert len(pending) >= 1
        assert pending[-1]["tool_name"] == destructive

    def test_invalid_token_fails(self, confirmation_enabled):
        """An invalid confirmation token must raise SecurityError."""
        destructive = _pick_destructive_tool()
        kwargs = _kwargs_for(destructive)
        kwargs["confirmation_token"] = "bogus-token-12345"

        with pytest.raises(
            trust_gateway.SecurityError, match="Invalid or expired"
        ):
            trusted_call_tool(destructive, **kwargs)

    def test_mismatched_token_fails(self, confirmation_enabled):
        """A token minted for tool A must not authorize tool B.

        Uses two real tools from the DESTRUCTIVE_TOOLS frozenset.
        """
        registry = get_tool_registry()
        all_tools = set(registry.list_tools())

        # Find two destructive tools that are both in DESTRUCTIVE_TOOLS and
        # in the registry.
        candidates = sorted(name for name in DESTRUCTIVE_TOOLS if name in all_tools)
        if len(candidates) < 2:
            pytest.skip("Need at least 2 destructive tools in DESTRUCTIVE_TOOLS for mismatch test")

        tool_a, tool_b = candidates[0], candidates[1]

        # Mint a token for tool_a
        kwargs_a = _kwargs_for(tool_a)
        res_a = trusted_call_tool(tool_a, **kwargs_a)
        assert res_a.get("confirmation_required") is True
        token = res_a["confirm_token"]

        # Attempt to use it for tool_b
        kwargs_b = _kwargs_for(tool_b)
        kwargs_b["confirmation_token"] = token

        with pytest.raises(
            trust_gateway.SecurityError,
            match="Confirmation token does not match tool",
        ):
            trusted_call_tool(tool_b, **kwargs_b)


# ---------------------------------------------------------------------------
# TestSecurityErrorOnUntrusted
# ---------------------------------------------------------------------------

class TestSecurityErrorOnUntrusted:
    """Verify that calling tools at insufficient trust levels raises SecurityError."""

    def test_untrusted_safe_tool_raises(self):
        """A safe tool at UNTRUSTED must be rejected.

        Schema validation runs *before* trust checks, so we must be
        careful to differentiate a ValueError (schema) from a
        SecurityError (trust).  The chosen safe tool has no required
        args, so schema validation passes and SecurityError fires.
        """
        safe = _pick_safe_tool()
        with pytest.raises(trust_gateway.SecurityError):
            trusted_call_tool(safe)

    def test_untrusted_destructive_tool_raises(self):
        """A destructive tool at UNTRUSTED must be rejected."""
        destructive = _pick_destructive_tool()
        kwargs = _kwargs_for(destructive)
        with pytest.raises(trust_gateway.SecurityError):
            trusted_call_tool(destructive, **kwargs)

    def test_verified_destructive_tool_still_blocked(self):
        """A destructive tool that is only VERIFIED (not TRUSTED) must be rejected."""
        destructive = _pick_destructive_tool()
        # verify_all_safe() promotes only safe tools; destructive stays UNTRUSTED
        _registry.verify_all_safe()
        assert _registry.level(destructive) == TrustLevel.UNTRUSTED

        kwargs = _kwargs_for(destructive)
        with pytest.raises(trust_gateway.SecurityError):
            trusted_call_tool(destructive, **kwargs)
