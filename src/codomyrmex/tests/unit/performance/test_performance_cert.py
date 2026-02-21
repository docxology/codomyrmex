"""Tests for Sprint 40: Performance Certification.

Covers BenchmarkRunner, LoadTester, and MemoryProfiler.
"""

import pytest

from codomyrmex.performance.benchmark_runner import BenchmarkRunner
from codomyrmex.performance.load_tester import LoadTester
from codomyrmex.performance.memory_profiler import MemoryProfiler


# ─── BenchmarkRunner ──────────────────────────────────────────────────

class TestBenchmarkRunner:

    def test_basic_benchmark(self):
        runner = BenchmarkRunner()
        runner.add("noop", lambda: None, iterations=10)
        suite = runner.run()
        assert suite.all_passed
        assert len(suite.results) == 1

    def test_threshold_pass(self):
        runner = BenchmarkRunner()
        runner.add("fast", lambda: None, iterations=10, threshold_ms=100)
        suite = runner.run()
        assert suite.results[0].passed

    def test_ops_per_sec(self):
        runner = BenchmarkRunner()
        runner.add("work", lambda: sum(range(100)), iterations=50)
        suite = runner.run()
        assert suite.results[0].ops_per_sec > 0

    def test_markdown_output(self):
        runner = BenchmarkRunner()
        runner.add("test", lambda: None, iterations=5)
        suite = runner.run()
        md = runner.to_markdown(suite)
        assert "test" in md
        assert "Ops/s" in md

    def test_multiple_benchmarks(self):
        runner = BenchmarkRunner()
        runner.add("a", lambda: None, iterations=5)
        runner.add("b", lambda: sum(range(10)), iterations=5)
        suite = runner.run()
        assert len(suite.results) == 2


# ─── LoadTester ───────────────────────────────────────────────────────

class TestLoadTester:

    def test_successful_load(self):
        tester = LoadTester()
        result = tester.run(fn=lambda: None, total_requests=50)
        assert result.successful == 50
        assert result.error_rate == 0.0

    def test_error_rate(self):
        call_count = {"n": 0}
        def sometimes_fail():
            call_count["n"] += 1
            if call_count["n"] % 5 == 0:
                raise RuntimeError("fail")

        tester = LoadTester()
        result = tester.run(fn=sometimes_fail, total_requests=50)
        assert result.failed == 10
        assert result.error_rate == pytest.approx(0.2)

    def test_throughput(self):
        tester = LoadTester()
        result = tester.run(fn=lambda: None, total_requests=100)
        assert result.throughput_per_sec > 0


# ─── MemoryProfiler ──────────────────────────────────────────────────

class TestMemoryProfiler:

    def test_snapshot(self):
        profiler = MemoryProfiler()
        snap = profiler.snapshot_lightweight("test", tracked_count=100)
        assert snap.object_count == 100

    def test_diff_no_leak(self):
        profiler = MemoryProfiler(leak_threshold=1000)
        profiler.snapshot_lightweight("before", 100)
        profiler.snapshot_lightweight("after", 150)
        delta = profiler.diff("before", "after")
        assert delta.object_delta == 50
        assert not delta.leak_suspected

    def test_diff_leak_detected(self):
        profiler = MemoryProfiler(leak_threshold=100)
        profiler.snapshot_lightweight("before", 100)
        profiler.snapshot_lightweight("after", 300)
        delta = profiler.diff("before", "after")
        assert delta.leak_suspected

    def test_gc_snapshot(self):
        profiler = MemoryProfiler()
        snap = profiler.snapshot("gc_test")
        assert snap.object_count > 0
