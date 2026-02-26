"""Tests for trust gateway audit log and utility functions.

Sprint 2 coverage: targets audit log, export, and helper
functions in ``codomyrmex.agents.pai.trust_gateway``.
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from codomyrmex.agents.pai.trust_gateway import (
    _log_audit_entry,
    get_audit_log,
    export_audit_log,
    clear_audit_log,
    _is_destructive,
    DESTRUCTIVE_TOOLS,
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
        cutoff = datetime.now(timezone.utc)
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
