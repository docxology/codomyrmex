"""Tests for v1.1.12 — Autonomous CI, Budget Controls, Final Integration.

Zero-Mock: All tests use real implementations.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

# ── C1: Flaky Test Quarantine ─────────────────────────────────────
from codomyrmex.ci_cd_automation.flaky_quarantine import (
    FlakyTestQuarantine,
)


class TestFlakyQuarantine:
    """Verify flaky test detection and quarantine."""

    def test_stable_test_not_quarantined(self) -> None:
        q = FlakyTestQuarantine()
        for _ in range(10):
            q.record_run("test_stable", passed=True)
        assert not q.is_flaky("test_stable")

    def test_consistently_failing_not_flaky(self) -> None:
        q = FlakyTestQuarantine()
        for _ in range(10):
            q.record_run("test_broken", passed=False)
        # Always fails = not flaky (it's just broken)
        assert not q.is_flaky("test_broken")

    def test_intermittent_is_flaky(self) -> None:
        q = FlakyTestQuarantine(window_size=10, fail_threshold=2)
        # Mix of pass/fail
        for _ in range(5):
            q.record_run("test_flaky", passed=True)
        q.record_run("test_flaky", passed=False)
        q.record_run("test_flaky", passed=False)
        assert q.is_flaky("test_flaky")

    def test_quarantine_entry_details(self) -> None:
        q = FlakyTestQuarantine(window_size=5, fail_threshold=2)
        for _ in range(3):
            q.record_run("test_x", passed=True)
        q.record_run("test_x", passed=False)
        q.record_run("test_x", passed=False)

        entries = q.get_quarantined()
        assert len(entries) == 1
        assert entries[0].test_id == "test_x"
        assert entries[0].fail_rate > 0

    def test_release_from_quarantine(self) -> None:
        q = FlakyTestQuarantine(window_size=5, fail_threshold=2)
        q.record_run("test_y", passed=True)
        q.record_run("test_y", passed=False)
        q.record_run("test_y", passed=False)
        assert q.is_flaky("test_y")
        assert q.release("test_y")
        assert not q.is_flaky("test_y")

    def test_summary(self) -> None:
        q = FlakyTestQuarantine(window_size=5, fail_threshold=2)
        q.record_run("test_a", passed=True)
        q.record_run("test_a", passed=False)
        q.record_run("test_a", passed=False)

        summary = q.get_summary()
        assert summary["total_tracked"] == 1
        assert summary["quarantined_count"] == 1

    def test_generate_markers(self) -> None:
        q = FlakyTestQuarantine(window_size=5, fail_threshold=2)
        q.record_run("test_z", passed=True)
        q.record_run("test_z", passed=False)
        q.record_run("test_z", passed=False)

        markers = q.generate_pytest_markers()
        assert "test_z" in markers
        assert "flaky" in markers

    def test_window_trimming(self) -> None:
        q = FlakyTestQuarantine(window_size=3)
        for _ in range(20):
            q.record_run("test_trim", passed=True)
        # Internal window should be trimmed to 3
        assert len(q._runs["test_trim"]) == 3


# ── B1: Budget Manager ───────────────────────────────────────────

from codomyrmex.cost_management.budget_manager import (
    BudgetManager,
    SpendRecord,
    get_budget_manager,
)


class TestBudgetManager:
    """Verify dynamic budget management."""

    def test_record_spend(self) -> None:
        mgr = BudgetManager(daily_limit=100.0)
        record = mgr.record_spend("gpt-4o", 5.0)
        assert isinstance(record, SpendRecord)
        assert record.amount == 5.0

    def test_can_spend_under_budget(self) -> None:
        mgr = BudgetManager(daily_limit=100.0, pause_threshold=0.90)
        mgr.record_spend("gpt-4o", 10.0)
        assert mgr.can_spend(5.0)  # 10 + 5 = 15 < 90

    def test_auto_pause_at_threshold(self) -> None:
        mgr = BudgetManager(daily_limit=100.0, pause_threshold=0.90)
        mgr.record_spend("gpt-4o", 91.0)
        assert mgr.is_paused
        assert not mgr.can_spend(1.0)

    def test_warning_alert(self) -> None:
        mgr = BudgetManager(daily_limit=100.0, warning_threshold=0.80, pause_threshold=0.95)
        mgr.record_spend("gpt-4o", 85.0)
        alerts = mgr.get_alerts()
        assert len(alerts) >= 1
        assert any(a.level == "warning" for a in alerts)

    def test_spend_by_model(self) -> None:
        mgr = BudgetManager(daily_limit=1000.0)
        mgr.record_spend("gpt-4o", 5.0)
        mgr.record_spend("gemma3", 2.0)
        mgr.record_spend("gpt-4o", 3.0)

        breakdown = mgr.get_spend_by_model()
        assert breakdown.get("gpt-4o", 0) == 8.0
        assert breakdown.get("gemma3", 0) == 2.0

    def test_utilization(self) -> None:
        mgr = BudgetManager(daily_limit=100.0)
        mgr.record_spend("test", 25.0)
        assert mgr.get_utilization() == pytest.approx(0.25, abs=0.01)

    def test_summary(self) -> None:
        mgr = BudgetManager(daily_limit=100.0)
        mgr.record_spend("test", 10.0)
        summary = mgr.get_summary()
        assert summary["daily_limit"] == 100.0
        assert summary["daily_spend"] == pytest.approx(10.0, abs=0.01)
        assert not summary["paused"]

    def test_singleton(self) -> None:
        m1 = get_budget_manager()
        m2 = get_budget_manager()
        assert m1 is m2

    def test_webhook_registration(self) -> None:
        mgr = BudgetManager()
        mgr.register_webhook("https://example.com/webhook")
        assert len(mgr._webhooks) == 1


# ── I1: WebSocket Live Feed ──────────────────────────────────────

from codomyrmex.website.live_feed import (
    FeedEvent,
    LiveFeedProvider,
    get_live_feed,
)


class TestLiveFeed:
    """Verify WebSocket live feed provider."""

    def test_emit_event(self) -> None:
        feed = LiveFeedProvider()
        event = feed.emit("log", "hermes", {"message": "hello"})
        assert isinstance(event, FeedEvent)
        assert event.event_type == "log"
        assert event.source == "hermes"

    def test_get_recent(self) -> None:
        feed = LiveFeedProvider()
        for i in range(10):
            feed.emit("metric", "telemetry", {"value": i})
        recent = feed.get_recent_events(limit=5)
        assert len(recent) == 5

    def test_filter_by_type(self) -> None:
        feed = LiveFeedProvider()
        feed.emit("log", "auth")
        feed.emit("metric", "telemetry")
        feed.emit("log", "hermes")

        logs = feed.get_recent_events(event_type="log")
        assert len(logs) == 2
        assert all(e.event_type == "log" for e in logs)

    def test_filter_by_source(self) -> None:
        feed = LiveFeedProvider()
        feed.emit("log", "hermes")
        feed.emit("log", "claude")
        feed.emit("metric", "hermes")

        hermes_events = feed.get_recent_events(source="hermes")
        assert len(hermes_events) == 2

    def test_snapshot(self) -> None:
        feed = LiveFeedProvider()
        feed.emit("log", "auth")
        feed.emit("metric", "telemetry")

        snapshot = feed.get_snapshot()
        assert snapshot["total_events"] == 2
        assert "log" in snapshot["event_types"]
        assert "auth" in snapshot["sources"]

    def test_clear(self) -> None:
        feed = LiveFeedProvider()
        feed.emit("log", "test")
        feed.clear()
        assert feed.get_snapshot()["total_events"] == 0

    def test_events_since(self) -> None:
        feed = LiveFeedProvider()
        before = time.time()
        time.sleep(0.01)
        feed.emit("log", "test")

        events = feed.get_events_since(before)
        assert len(events) == 1

    def test_json_serialization(self) -> None:
        event = FeedEvent(event_type="log", source="test", data={"key": "val"})
        j = event.to_json()
        parsed = json.loads(j)
        assert parsed["event_type"] == "log"
        assert parsed["data"]["key"] == "val"

    def test_bounded_buffer(self) -> None:
        feed = LiveFeedProvider(max_events=5)
        for i in range(20):
            feed.emit("metric", "test", {"i": i})
        assert feed.get_snapshot()["total_events"] == 5

    def test_singleton(self) -> None:
        f1 = get_live_feed()
        f2 = get_live_feed()
        assert f1 is f2


# ── I3: Release Auditor ──────────────────────────────────────────

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts" / "maintenance"))

from release_audit import AuditCheck, ReleaseAuditor


class TestReleaseAuditor:
    """Verify pre-release audit checks."""

    def test_version_consistency(self) -> None:
        auditor = ReleaseAuditor()
        result = auditor.check_version_consistency()
        assert isinstance(result, AuditCheck)
        assert result.passed

    def test_dockerfile_check(self) -> None:
        auditor = ReleaseAuditor()
        result = auditor.check_dockerfile()
        assert result.passed

    def test_documentation_check(self) -> None:
        auditor = ReleaseAuditor()
        result = auditor.check_documentation()
        assert result.passed

    def test_module_docs(self) -> None:
        auditor = ReleaseAuditor()
        result = auditor.check_module_docs()
        assert result.passed  # 90%+ modules have README

    def test_release_tests_exist(self) -> None:
        auditor = ReleaseAuditor()
        result = auditor.check_test_file_exists()
        assert result.passed

    def test_run_all(self) -> None:
        auditor = ReleaseAuditor()
        results = auditor.run_all()
        assert len(results) == 6
        passed = sum(1 for r in results if r.passed)
        assert passed >= 5  # at least 5/6 should pass

    def test_report(self) -> None:
        auditor = ReleaseAuditor()
        report = auditor.get_report()
        assert "Pre-Release Audit Report" in report
        assert "✅" in report
