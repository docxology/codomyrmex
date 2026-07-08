"""Tests for trust gateway audit log and utility functions.

Sprint 2 coverage: targets audit log, export, and helper
functions in ``codomyrmex.agents.pai.trust_gateway``.
"""

import json
import tempfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from codomyrmex.agents.pai.trust_gateway import (
    DESTRUCTIVE_TOOLS,
    TrustLevel,
    TrustRegistry,
    _cleanup_expired_confirmations_locked,
    _confirmations_lock,
    _is_destructive,
    _log_audit_entry,
    _pending_confirmations,
    clear_audit_log,
    export_audit_log,
    get_audit_log,
)


@pytest.mark.unit
class TestAuditLog:
    """Tests for audit log recording and retrieval."""

    def test_log_entry_recorded(self):
        """_log_audit_entry adds an entry to the global log."""
        initial_count = len(get_audit_log())
        _log_audit_entry(
            tool_name="codomyrmex.test_tool",
            args={"x": 1},
            status="success",
            trust_level="VERIFIED",
            duration_ms=42.0,
        )
        assert len(get_audit_log()) == initial_count + 1

    def test_log_entry_fields(self):
        """Audit entry contains expected fields."""
        _log_audit_entry(
            tool_name="codomyrmex.check_fields",
            args={"a": "b"},
            status="success",
            trust_level="TRUSTED",
            duration_ms=10.0,
        )
        entries = get_audit_log(tool_name="codomyrmex.check_fields")
        assert len(entries) >= 1
        entry = entries[-1]
        assert entry["tool_name"] == "codomyrmex.check_fields"
        assert entry["result_status"] == "success"
        assert entry["trust_level"] == "TRUSTED"
        assert entry["duration_ms"] == 10.0
        assert entry["error_code"] is None

    def test_log_entry_with_error(self):
        """Audit entry captures error type."""
        _log_audit_entry(
            tool_name="codomyrmex.error_test",
            args={},
            status="error",
            trust_level="UNTRUSTED",
            duration_ms=0.0,
            error=ValueError("bad input"),
        )
        entries = get_audit_log(tool_name="codomyrmex.error_test")
        assert entries[-1]["error_code"] == "ValueError"

    def test_filter_by_status(self):
        """get_audit_log filters by status."""
        _log_audit_entry("test.filter", {}, "blocked", "UNTRUSTED", 0.0)
        blocked = get_audit_log(status="blocked")
        assert all(e["result_status"] == "blocked" for e in blocked)

    def test_filter_by_since(self):
        """get_audit_log(since=) excludes entries before the cutoff."""
        clear_audit_log()
        _log_audit_entry("since.old", {}, "success", "TRUSTED", 1.0)
        cutoff = datetime.now(UTC)
        _log_audit_entry("since.new", {}, "success", "TRUSTED", 1.0)
        recent = get_audit_log(since=cutoff)
        tool_names = [e["tool_name"] for e in recent]
        assert "since.new" in tool_names
        assert "since.old" not in tool_names
        assert all(datetime.fromisoformat(e["timestamp"]) >= cutoff for e in recent)

    def test_unhashable_args(self):
        """Non-serializable args get 'unhashable' hash."""
        _log_audit_entry(
            tool_name="codomyrmex.unhashable",
            args={"fn": lambda: None},  # not JSON-serializable
            status="success",
            trust_level="VERIFIED",
            duration_ms=1.0,
        )
        entries = get_audit_log(tool_name="codomyrmex.unhashable")
        assert entries[-1]["args_hash"] == "unhashable"


@pytest.mark.unit
class TestAuditExport:
    """Tests for audit log export."""

    def test_export_jsonl(self):
        """export_audit_log writes JSONL to disk."""
        _log_audit_entry("export.test", {}, "success", "TRUSTED", 1.0)

        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = Path(f.name)

        try:
            export_audit_log(path, format="jsonl")
            lines = path.read_text().strip().split("\n")
            assert len(lines) >= 1
            # Each line should be valid JSON
            for line in lines:
                json.loads(line)
        finally:
            path.unlink(missing_ok=True)

    def test_export_invalid_format(self):
        """export_audit_log raises for unknown format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            export_audit_log("/tmp/nope.csv", format="csv")


@pytest.mark.unit
class TestClearAuditLog:
    """Tests for audit log clearing."""

    def test_clear_all(self):
        """clear_audit_log(None) clears everything."""
        _log_audit_entry("clear.test", {}, "success", "TRUSTED", 1.0)
        count = clear_audit_log()
        assert count >= 1
        assert len(get_audit_log()) == 0

    def test_clear_before_date(self):
        """clear_audit_log(before) only removes older entries."""
        clear_audit_log()  # start fresh
        _log_audit_entry("old.entry", {}, "success", "TRUSTED", 1.0)
        cutoff = datetime.now(UTC)
        _log_audit_entry("new.entry", {}, "success", "TRUSTED", 1.0)
        removed = clear_audit_log(before=cutoff)
        assert removed >= 1
        remaining = get_audit_log()
        # The new entry should survive
        assert any(e["tool_name"] == "new.entry" for e in remaining)


@pytest.mark.unit
class TestDestructiveDetection:
    """Tests for _is_destructive helper."""

    def test_explicit_destructive(self):
        """Explicitly listed tools are destructive."""
        for tool in DESTRUCTIVE_TOOLS:
            assert _is_destructive(tool) is True

    def test_safe_tool(self):
        """Read-only tools are not destructive."""
        assert _is_destructive("codomyrmex.list_modules") is False

    def test_pattern_match(self):
        """Auto-discovered tools with destructive patterns match."""
        assert _is_destructive("codomyrmex.auth.delete_user") is True
        assert _is_destructive("codomyrmex.cache.clear_all") is True

    def test_safe_auto_discovered(self):
        """Auto-discovered tools without destructive patterns are safe."""
        assert _is_destructive("codomyrmex.cache.get_stats") is False


def _make_isolated_registry(levels: dict) -> "TrustRegistry":
    """Create a TrustRegistry that is fully isolated from disk state.

    Uses a non-existent ledger path so _load() is a no-op and overrides
    _save() to prevent any filesystem writes during tests.
    """
    reg = TrustRegistry.__new__(TrustRegistry)
    # Non-existent path means _load() returns immediately (no file found)
    reg._ledger_path = Path("/nonexistent_test_trust_ledger_path.json")
    reg._levels = dict(levels)
    # Prevent writes to disk during tests
    reg._save = lambda: None
    return reg


@pytest.mark.unit
class TestTrustStateMachine:
    """Tests for the UNTRUSTED → VERIFIED → TRUSTED state machine."""

    def test_trust_level_ordering(self):
        """TrustLevel enum has the three expected values."""
        assert TrustLevel.UNTRUSTED.value == "untrusted"
        assert TrustLevel.VERIFIED.value == "verified"
        assert TrustLevel.TRUSTED.value == "trusted"

    def test_new_registry_reports_untrusted(self):
        """A registry with UNTRUSTED levels reports them correctly."""
        tool = "codomyrmex.list_modules"
        reg = _make_isolated_registry({tool: TrustLevel.UNTRUSTED})
        assert reg.level(tool) == TrustLevel.UNTRUSTED

    def test_verify_all_safe_promotes_safe_tools(self):
        """verify_all_safe() promotes eligible safe tools from UNTRUSTED to VERIFIED."""
        from codomyrmex.agents.pai.trust_gateway import SAFE_TOOLS

        if not SAFE_TOOLS:
            pytest.skip("No safe tools registered in this environment")
        safe_tool = next(iter(SAFE_TOOLS))
        reg = _make_isolated_registry({safe_tool: TrustLevel.UNTRUSTED})
        promoted = reg.verify_all_safe()
        assert safe_tool in promoted
        assert reg.level(safe_tool) == TrustLevel.VERIFIED

    def test_verify_does_not_promote_already_trusted(self):
        """verify_all_safe() leaves TRUSTED tools unchanged."""
        from codomyrmex.agents.pai.trust_gateway import SAFE_TOOLS

        if not SAFE_TOOLS:
            pytest.skip("No safe tools registered in this environment")
        tool = next(iter(SAFE_TOOLS))
        reg = _make_isolated_registry({tool: TrustLevel.TRUSTED})
        promoted = reg.verify_all_safe()
        assert tool not in promoted
        assert reg.level(tool) == TrustLevel.TRUSTED

    def test_trust_tool_promotes_to_trusted(self):
        """trust_tool() raises a tool from VERIFIED to TRUSTED."""
        from codomyrmex.agents.pai.trust_gateway import SAFE_TOOLS

        if not SAFE_TOOLS:
            pytest.skip("No safe tools registered in this environment")
        tool = next(iter(SAFE_TOOLS))
        reg = _make_isolated_registry({tool: TrustLevel.VERIFIED})
        result = reg.trust_tool(tool)
        assert result == TrustLevel.TRUSTED
        assert reg.level(tool) == TrustLevel.TRUSTED

    def test_destructive_tool_not_promoted_by_verify(self):
        """verify_all_safe() never promotes a destructive tool."""
        for dtool in DESTRUCTIVE_TOOLS:
            reg = _make_isolated_registry({dtool: TrustLevel.UNTRUSTED})
            promoted = reg.verify_all_safe()
            assert dtool not in promoted
            assert reg.level(dtool) == TrustLevel.UNTRUSTED

    def test_is_at_least_verified(self):
        """is_at_least_verified returns True only for VERIFIED or TRUSTED."""
        tool = "codomyrmex.list_modules"
        reg = _make_isolated_registry({tool: TrustLevel.UNTRUSTED})
        assert reg.is_at_least_verified(tool) is False
        reg._levels[tool] = TrustLevel.VERIFIED
        assert reg.is_at_least_verified(tool) is True
        reg._levels[tool] = TrustLevel.TRUSTED
        assert reg.is_at_least_verified(tool) is True

    def test_reset_returns_all_to_untrusted(self):
        """reset() sets every tool back to UNTRUSTED."""
        reg = _make_isolated_registry(
            {
                "codomyrmex.list_modules": TrustLevel.TRUSTED,
                "codomyrmex.write_file": TrustLevel.VERIFIED,
            }
        )
        reg.reset()
        for level in reg._levels.values():
            assert level == TrustLevel.UNTRUSTED


@pytest.mark.unit
class TestConcurrentAuditLog:
    """Verify audit log remains consistent under concurrent writes."""

    def test_concurrent_writes_all_recorded(self):
        """Multiple threads writing simultaneously produce no lost entries."""
        clear_audit_log()
        n_threads = 10
        writes_per_thread = 5
        errors = []

        def write_entries(thread_id: int) -> None:
            try:
                for i in range(writes_per_thread):
                    _log_audit_entry(
                        tool_name=f"codomyrmex.concurrent_test_{thread_id}_{i}",
                        args={},
                        status="success",
                        trust_level="UNTRUSTED",
                        duration_ms=0.1,
                    )
            except Exception as exc:
                errors.append(exc)

        threads = [
            threading.Thread(target=write_entries, args=(t,)) for t in range(n_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent write errors: {errors}"
        log = get_audit_log()
        concurrent_entries = [e for e in log if "concurrent_test_" in e["tool_name"]]
        assert len(concurrent_entries) == n_threads * writes_per_thread


@pytest.mark.unit
class TestConfirmationTTL:
    """Verify expired pending confirmations are cleaned up."""

    def test_expired_confirmations_are_removed(self):
        """_cleanup_expired_confirmations() removes entries past TTL.

        Uses time.monotonic() to match the implementation's clock source.
        """
        _pending_confirmations.clear()
        expired_token = "test-expired-token"
        # Insert a confirmation whose monotonic timestamp is far in the past
        _pending_confirmations[expired_token] = {
            "tool_name": "codomyrmex.test",
            "timestamp": time.monotonic() - 9999,
        }
        assert expired_token in _pending_confirmations
        with _confirmations_lock:
            _cleanup_expired_confirmations_locked()
        assert expired_token not in _pending_confirmations

    def test_fresh_confirmations_are_kept(self):
        """_cleanup_expired_confirmations() retains non-expired entries."""
        _pending_confirmations.clear()
        fresh_token = "test-fresh-token"
        _pending_confirmations[fresh_token] = {
            "tool_name": "codomyrmex.test",
            "timestamp": time.monotonic(),
        }
        with _confirmations_lock:
            _cleanup_expired_confirmations_locked()
        assert fresh_token in _pending_confirmations
        _pending_confirmations.clear()
