"""Tests for MCP Discovery Metrics (Stream 3).

Verifies:
- DiscoveryMetrics dataclass fields
- Metrics integration via MCPDiscoveryEngine
- Discovery metrics resource endpoint structure
"""

from __future__ import annotations

import json

import pytest

from codomyrmex.model_context_protocol.discovery import (
    DiscoveryMetrics,
    MCPDiscoveryEngine,
)


# ── DiscoveryMetrics dataclass ────────────────────────────────────────


class TestDiscoveryMetricsDataclass:
    def test_default_values(self) -> None:
        m = DiscoveryMetrics()
        assert m.total_tools == 0
        assert m.scan_duration_ms == 0.0
        assert m.failed_modules == []
        assert m.modules_scanned == 0
        assert m.cache_hits == 0
        assert m.last_scan_time is None

    def test_custom_values(self) -> None:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        m = DiscoveryMetrics(
            total_tools=42,
            scan_duration_ms=123.4,
            failed_modules=["foo", "bar"],
            modules_scanned=10,
            cache_hits=5,
            last_scan_time=now,
        )
        assert m.total_tools == 42
        assert m.scan_duration_ms == 123.4
        assert m.failed_modules == ["foo", "bar"]
        assert m.modules_scanned == 10
        assert m.cache_hits == 5
        assert m.last_scan_time == now


# ── Metrics via engine ────────────────────────────────────────────────


class TestMetricsViaEngine:
    def test_fresh_engine_metrics(self) -> None:
        engine = MCPDiscoveryEngine()
        m = engine.get_metrics()
        assert m.total_tools == 0
        assert m.cache_hits == 0

    def test_scan_updates_metrics(self) -> None:
        engine = MCPDiscoveryEngine()
        engine.scan_package("codomyrmex.model_context_protocol.discovery")
        m = engine.get_metrics()
        assert m.scan_duration_ms > 0
        assert m.last_scan_time is not None

    def test_cache_hit_increments_in_metrics(self) -> None:
        engine = MCPDiscoveryEngine()
        engine.record_cache_hit()
        engine.record_cache_hit()
        m = engine.get_metrics()
        assert m.cache_hits == 2

    def test_metrics_reflect_tool_count(self) -> None:
        engine = MCPDiscoveryEngine()
        engine.scan_package("codomyrmex.model_context_protocol.discovery")
        m = engine.get_metrics()
        assert m.total_tools == engine.tool_count


# ── Metrics serialisation (resource provider) ─────────────────────────


class TestMetricsSerialisation:
    def test_metrics_are_json_serialisable(self) -> None:
        from datetime import datetime, timezone

        m = DiscoveryMetrics(
            total_tools=5,
            scan_duration_ms=42.0,
            failed_modules=["bad_mod"],
            modules_scanned=3,
            cache_hits=1,
            last_scan_time=datetime.now(timezone.utc),
        )
        payload = {
            "total_tools": m.total_tools,
            "scan_duration_ms": m.scan_duration_ms,
            "failed_modules": m.failed_modules,
            "modules_scanned": m.modules_scanned,
            "cache_hits": m.cache_hits,
            "last_scan_time": m.last_scan_time.isoformat() if m.last_scan_time else None,
        }
        result = json.dumps(payload)
        parsed = json.loads(result)
        assert parsed["total_tools"] == 5
        assert parsed["failed_modules"] == ["bad_mod"]
        assert parsed["last_scan_time"] is not None


# ── Imports from top-level package ────────────────────────────────────


class TestStreamThreeExports:
    """Verify Stream 3 types are importable from top-level MCP package."""

    def test_import_from_mcp_package(self) -> None:
        from codomyrmex.model_context_protocol import (
            DiscoveryMetrics,
            DiscoveryReport,
            FailedModule,
            MCPDiscoveryEngine,
        )
        assert DiscoveryMetrics is not None
        assert DiscoveryReport is not None
        assert FailedModule is not None
        assert MCPDiscoveryEngine is not None
