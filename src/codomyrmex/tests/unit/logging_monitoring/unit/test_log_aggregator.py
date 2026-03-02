"""
Unit tests for logging_monitoring.core.log_aggregator — Zero-Mock compliant.

Covers: LogRecord, LogQuery, LogStats, LogAggregator
(add, add_many, search with all filter types, stats, tail, clear,
max_records eviction)
"""

import time

import pytest

from codomyrmex.logging_monitoring.core.log_aggregator import (
    LogAggregator,
    LogQuery,
    LogRecord,
    LogStats,
)


def _rec(level="info", message="msg", module="app", cid="", **fields):
    return LogRecord(level=level, message=message, module=module, correlation_id=cid, fields=fields)


# ── LogRecord ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLogRecord:
    def test_defaults(self):
        r = LogRecord(level="info", message="hello")
        assert r.module == ""
        assert r.correlation_id == ""
        assert r.fields == {}
        assert r.timestamp > 0

    def test_explicit_fields(self):
        r = LogRecord(level="error", message="boom", module="db", correlation_id="cid-1")
        assert r.level == "error"
        assert r.module == "db"
        assert r.correlation_id == "cid-1"


# ── LogQuery ───────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLogQuery:
    def test_defaults(self):
        q = LogQuery()
        assert q.levels == []
        assert q.modules == []
        assert q.start_time == 0.0
        assert q.end_time == 0.0
        assert q.correlation_id == ""
        assert q.message_contains == ""
        assert q.limit == 100


# ── LogAggregator ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLogAggregatorBasic:
    def test_starts_empty(self):
        agg = LogAggregator()
        assert agg.count == 0

    def test_add_single(self):
        agg = LogAggregator()
        agg.add(_rec())
        assert agg.count == 1

    def test_add_many(self):
        agg = LogAggregator()
        agg.add_many([_rec(), _rec(), _rec()])
        assert agg.count == 3

    def test_clear_removes_all(self):
        agg = LogAggregator()
        agg.add(_rec())
        agg.clear()
        assert agg.count == 0

    def test_max_records_evicts_oldest(self):
        agg = LogAggregator(max_records=3)
        for i in range(5):
            agg.add(_rec(message=f"msg{i}"))
        assert agg.count == 3
        # Most recent 3 are kept: msg2, msg3, msg4
        messages = [r.message for r in agg.tail(10)]
        assert "msg4" in messages
        assert "msg0" not in messages

    def test_tail_returns_recent(self):
        agg = LogAggregator()
        for i in range(10):
            agg.add(_rec(message=f"msg{i}"))
        tail = agg.tail(3)
        assert len(tail) == 3
        assert tail[-1].message == "msg9"

    def test_tail_fewer_than_n(self):
        agg = LogAggregator()
        agg.add(_rec(message="only"))
        tail = agg.tail(10)
        assert len(tail) == 1


@pytest.mark.unit
class TestLogAggregatorSearch:
    def test_search_all_returns_all(self):
        agg = LogAggregator()
        agg.add_many([_rec(level="info"), _rec(level="error"), _rec(level="debug")])
        results = agg.search(LogQuery())
        assert len(results) == 3

    def test_search_by_level(self):
        agg = LogAggregator()
        agg.add(_rec(level="info", message="i1"))
        agg.add(_rec(level="error", message="e1"))
        agg.add(_rec(level="info", message="i2"))
        results = agg.search(LogQuery(levels=["error"]))
        assert len(results) == 1
        assert results[0].level == "error"

    def test_search_by_module(self):
        agg = LogAggregator()
        agg.add(_rec(module="db"))
        agg.add(_rec(module="api"))
        agg.add(_rec(module="db"))
        results = agg.search(LogQuery(modules=["db"]))
        assert len(results) == 2

    def test_search_by_message_contains(self):
        agg = LogAggregator()
        agg.add(_rec(message="request started"))
        agg.add(_rec(message="request failed"))
        agg.add(_rec(message="connection ok"))
        results = agg.search(LogQuery(message_contains="request"))
        assert len(results) == 2

    def test_search_by_correlation_id(self):
        agg = LogAggregator()
        agg.add(_rec(cid="cid-aaa"))
        agg.add(_rec(cid="cid-bbb"))
        agg.add(_rec(cid="cid-aaa"))
        results = agg.search(LogQuery(correlation_id="cid-aaa"))
        assert len(results) == 2

    def test_search_by_time_range(self):
        agg = LogAggregator()
        now = time.time()
        r1 = LogRecord(level="info", message="old", timestamp=now - 100)
        r2 = LogRecord(level="info", message="recent", timestamp=now)
        agg.add_many([r1, r2])
        results = agg.search(LogQuery(start_time=now - 50))
        assert len(results) == 1
        assert results[0].message == "recent"

    def test_search_end_time(self):
        agg = LogAggregator()
        now = time.time()
        r1 = LogRecord(level="info", message="past", timestamp=now - 200)
        r2 = LogRecord(level="info", message="future", timestamp=now + 100)
        agg.add_many([r1, r2])
        results = agg.search(LogQuery(end_time=now))
        assert len(results) == 1
        assert results[0].message == "past"

    def test_search_respects_limit(self):
        agg = LogAggregator()
        agg.add_many([_rec() for _ in range(20)])
        results = agg.search(LogQuery(limit=5))
        assert len(results) == 5

    def test_search_most_recent_first(self):
        agg = LogAggregator()
        agg.add(_rec(message="first"))
        agg.add(_rec(message="second"))
        agg.add(_rec(message="third"))
        results = agg.search(LogQuery())
        assert results[0].message == "third"

    def test_search_combined_filters(self):
        agg = LogAggregator()
        agg.add(_rec(level="error", module="db", message="db crash"))
        agg.add(_rec(level="error", module="api", message="api error"))
        agg.add(_rec(level="info", module="db", message="db ok"))
        results = agg.search(LogQuery(levels=["error"], modules=["db"]))
        assert len(results) == 1
        assert results[0].message == "db crash"

    def test_search_empty_agg_returns_empty(self):
        agg = LogAggregator()
        results = agg.search(LogQuery())
        assert results == []


@pytest.mark.unit
class TestLogAggregatorStats:
    def test_stats_empty_returns_default(self):
        agg = LogAggregator()
        stats = agg.stats()
        assert isinstance(stats, LogStats)
        assert stats.total_count == 0
        assert stats.error_rate == 0.0

    def test_stats_total_count(self):
        agg = LogAggregator()
        agg.add_many([_rec(level="info"), _rec(level="error"), _rec(level="debug")])
        stats = agg.stats()
        assert stats.total_count == 3

    def test_stats_level_counts(self):
        agg = LogAggregator()
        agg.add(_rec(level="info"))
        agg.add(_rec(level="info"))
        agg.add(_rec(level="error"))
        stats = agg.stats()
        assert stats.level_counts["info"] == 2
        assert stats.level_counts["error"] == 1

    def test_stats_error_rate_all_errors(self):
        agg = LogAggregator()
        agg.add_many([_rec(level="error"), _rec(level="critical")])
        stats = agg.stats()
        assert stats.error_rate == 1.0

    def test_stats_error_rate_mixed(self):
        agg = LogAggregator()
        agg.add(_rec(level="error"))
        agg.add(_rec(level="info"))
        stats = agg.stats()
        assert abs(stats.error_rate - 0.5) < 1e-9

    def test_stats_module_counts(self):
        agg = LogAggregator()
        agg.add(_rec(module="db"))
        agg.add(_rec(module="db"))
        agg.add(_rec(module="api"))
        stats = agg.stats()
        assert stats.module_counts["db"] == 2
        assert stats.module_counts["api"] == 1

    def test_stats_top_modules_sorted(self):
        agg = LogAggregator()
        agg.add_many([_rec(module="a")] * 3 + [_rec(module="b")] * 5 + [_rec(module="c")] * 1)
        stats = agg.stats()
        # Top module should be "b" with count 5
        assert stats.top_modules[0] == ("b", 5)

    def test_stats_time_range_single_record(self):
        agg = LogAggregator()
        agg.add(_rec())
        stats = agg.stats()
        assert stats.time_range_seconds == 0.0

    def test_stats_time_range_multiple(self):
        agg = LogAggregator()
        now = time.time()
        agg.add(LogRecord(level="info", message="a", timestamp=now))
        agg.add(LogRecord(level="info", message="b", timestamp=now + 10))
        stats = agg.stats()
        assert abs(stats.time_range_seconds - 10.0) < 1.0
