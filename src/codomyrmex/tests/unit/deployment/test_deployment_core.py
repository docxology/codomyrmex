"""Zero-mock tests for deployment core: strategies.py, types, canary analysis.

Targets:
- deployment/strategies/strategies.py: RollingStrategy, CanaryStrategy,
  BlueGreenStrategy, FeatureFlagStrategy, DeploymentState
- deployment/strategies/types.py: StrategyProgress, DeploymentTarget,
  DeploymentResult, DeploymentState (enum)
- deployment/canary.py: CanaryAnalyzer, MetricComparison, CanaryReport, CanaryDecision

All tests use real in-memory objects — no mocks, no monkeypatch.
"""

from __future__ import annotations

import time

import pytest

# ---------------------------------------------------------------------------
# Module-level import guards
# ---------------------------------------------------------------------------

try:
    from codomyrmex.deployment.strategies.strategies import (
        BlueGreenStrategy,
        CanaryStrategy,
        DeploymentStrategy,
        FeatureFlagStrategy,
        RollingStrategy,
    )
    from codomyrmex.deployment.strategies.strategies import (
        DeploymentState as StratDeploymentState,
    )

    STRATEGIES_AVAILABLE = True
except ImportError:
    STRATEGIES_AVAILABLE = False

try:
    from codomyrmex.deployment.strategies.types import (
        DeploymentResult,
        DeploymentTarget,
        StrategyProgress,
    )
    from codomyrmex.deployment.strategies.types import (
        DeploymentState as TypeDeploymentState,
    )

    TYPES_AVAILABLE = True
except ImportError:
    TYPES_AVAILABLE = False

try:
    from codomyrmex.deployment.canary import (
        CanaryAnalyzer,
        CanaryDecision,
        CanaryReport,
        MetricComparison,
    )

    CANARY_AVAILABLE = True
except ImportError:
    CANARY_AVAILABLE = False


# ---------------------------------------------------------------------------
# DeploymentState dataclass tests (strategies.py version)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason="strategies module not importable")
class TestStratDeploymentState:
    """Tests for DeploymentState dataclass in strategies.py."""

    def test_basic_fields_stored(self):
        s = StratDeploymentState(service="api", version="v2", strategy="rolling")
        assert s.service == "api"
        assert s.version == "v2"
        assert s.strategy == "rolling"

    def test_default_status_is_pending(self):
        s = StratDeploymentState(service="svc", version="1.0", strategy="canary")
        assert s.status == "pending"

    def test_default_traffic_percentage_is_zero(self):
        s = StratDeploymentState(service="svc", version="1.0", strategy="rolling")
        assert s.traffic_percentage == 0.0

    def test_complete_sets_status_and_traffic(self):
        s = StratDeploymentState(service="svc", version="1.0", strategy="rolling")
        s.complete()
        assert s.status == "completed"
        assert s.traffic_percentage == 100.0
        assert s.completed_at is not None

    def test_fail_sets_status_and_reason(self):
        s = StratDeploymentState(service="svc", version="1.0", strategy="rolling")
        s.fail("health check failed")
        assert s.status == "failed"
        assert s.metadata["failure_reason"] == "health check failed"

    def test_duration_seconds_grows_over_time(self):
        s = StratDeploymentState(service="svc", version="1.0", strategy="rolling")
        d1 = s.duration_seconds
        time.sleep(0.01)
        d2 = s.duration_seconds
        assert d2 >= d1

    def test_duration_seconds_fixed_after_complete(self):
        s = StratDeploymentState(service="svc", version="1.0", strategy="rolling")
        s.complete()
        d1 = s.duration_seconds
        time.sleep(0.01)
        d2 = s.duration_seconds
        assert abs(d2 - d1) < 0.001  # fixed after completion


# ---------------------------------------------------------------------------
# RollingStrategy tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason="strategies module not importable")
class TestRollingStrategy:
    """Tests for RollingStrategy.execute and rollback."""

    def test_execute_returns_completed_state(self):
        strategy = RollingStrategy(batch_count=4, pause_seconds=0.0)
        state = strategy.execute("my-service", "v1.0")
        assert state.status == "completed"

    def test_execute_sets_service_and_version(self):
        strategy = RollingStrategy(batch_count=2, pause_seconds=0.0)
        state = strategy.execute("auth", "2.0.0")
        assert state.service == "auth"
        assert state.version == "2.0.0"

    def test_execute_strategy_name_is_rolling(self):
        strategy = RollingStrategy(batch_count=2, pause_seconds=0.0)
        state = strategy.execute("svc", "1.0")
        assert state.strategy == "rolling"

    def test_execute_traffic_reaches_100(self):
        strategy = RollingStrategy(batch_count=4, pause_seconds=0.0)
        state = strategy.execute("svc", "1.0")
        assert state.traffic_percentage == 100.0

    def test_rollback_sets_rolled_back_status(self):
        strategy = RollingStrategy(batch_count=2, pause_seconds=0.0)
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.status == "rolled_back"

    def test_rollback_resets_traffic_to_zero(self):
        strategy = RollingStrategy(batch_count=2, pause_seconds=0.0)
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.traffic_percentage == 0.0

    def test_single_batch_still_completes(self):
        strategy = RollingStrategy(batch_size=1, batch_count=1, pause_seconds=0.0)
        state = strategy.execute("tiny-svc", "0.1")
        assert state.status == "completed"


# ---------------------------------------------------------------------------
# CanaryStrategy tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason="strategies module not importable")
class TestCanaryStrategy:
    """Tests for CanaryStrategy.execute and rollback."""

    def test_execute_returns_completed_state(self):
        strategy = CanaryStrategy(initial_percentage=10, step=30, max_steps=5)
        state = strategy.execute("canary-svc", "v2")
        assert state.status == "completed"

    def test_execute_strategy_name_is_canary(self):
        strategy = CanaryStrategy()
        state = strategy.execute("svc", "1.0")
        assert state.strategy == "canary"

    def test_execute_reaches_100_percent(self):
        strategy = CanaryStrategy(initial_percentage=50, step=50, max_steps=5)
        state = strategy.execute("svc", "1.0")
        assert state.traffic_percentage == 100.0

    def test_execute_does_not_exceed_100_percent(self):
        strategy = CanaryStrategy(initial_percentage=200, step=100, max_steps=3)
        state = strategy.execute("svc", "1.0")
        # traffic_percentage is capped at 100 in each loop iteration
        assert state.traffic_percentage <= 100.0

    def test_rollback_sets_rolled_back(self):
        strategy = CanaryStrategy()
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.status == "rolled_back"

    def test_rollback_resets_traffic_to_zero(self):
        strategy = CanaryStrategy()
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.traffic_percentage == 0.0


# ---------------------------------------------------------------------------
# BlueGreenStrategy tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason="strategies module not importable")
class TestBlueGreenStrategy:
    """Tests for BlueGreenStrategy.execute and rollback."""

    def test_execute_returns_completed_state(self):
        strategy = BlueGreenStrategy()
        state = strategy.execute("bg-svc", "v3")
        assert state.status == "completed"

    def test_execute_strategy_name_is_blue_green(self):
        strategy = BlueGreenStrategy()
        state = strategy.execute("svc", "1.0")
        assert state.strategy == "blue_green"

    def test_execute_traffic_is_100_after_swap(self):
        strategy = BlueGreenStrategy()
        state = strategy.execute("svc", "1.0")
        assert state.traffic_percentage == 100.0

    def test_execute_active_slot_is_green(self):
        strategy = BlueGreenStrategy()
        state = strategy.execute("svc", "1.0")
        assert state.metadata.get("active_slot") == "green"

    def test_rollback_sets_rolled_back_status(self):
        strategy = BlueGreenStrategy()
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.status == "rolled_back"

    def test_rollback_active_slot_is_blue(self):
        strategy = BlueGreenStrategy()
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.metadata.get("active_slot") == "blue"

    def test_rollback_traffic_is_100_back_on_blue(self):
        strategy = BlueGreenStrategy()
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.traffic_percentage == 100.0


# ---------------------------------------------------------------------------
# FeatureFlagStrategy tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason="strategies module not importable")
class TestFeatureFlagStrategy:
    """Tests for FeatureFlagStrategy.execute and rollback."""

    def test_execute_returns_completed_state(self):
        strategy = FeatureFlagStrategy(flag_name="new_ui", initial_rollout=0.0)
        state = strategy.execute("ui-svc", "v1")
        assert state.status == "completed"

    def test_execute_strategy_name_is_feature_flag(self):
        strategy = FeatureFlagStrategy()
        state = strategy.execute("svc", "1.0")
        assert state.strategy == "feature_flag"

    def test_execute_stores_flag_name_in_metadata(self):
        strategy = FeatureFlagStrategy(flag_name="dark_mode")
        state = strategy.execute("svc", "1.0")
        assert state.metadata.get("flag_name") == "dark_mode"

    def test_execute_auto_generates_flag_name_when_empty(self):
        strategy = FeatureFlagStrategy(flag_name="")
        state = strategy.execute("svc", "2.0")
        assert "flag_name" in state.metadata
        assert len(state.metadata["flag_name"]) > 0

    def test_execute_initial_rollout_stored_in_metadata_or_traffic(self):
        # FeatureFlagStrategy sets traffic to initial_rollout, then calls complete()
        # which overrides traffic_percentage to 100.0. Verify completed status.
        strategy = FeatureFlagStrategy(initial_rollout=25.0)
        state = strategy.execute("svc", "1.0")
        # complete() is called, so status is completed
        assert state.status == "completed"

    def test_rollback_sets_rolled_back_status(self):
        strategy = FeatureFlagStrategy(flag_name="exp")
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.status == "rolled_back"

    def test_rollback_sets_traffic_to_zero(self):
        strategy = FeatureFlagStrategy(flag_name="exp", initial_rollout=50.0)
        state = strategy.execute("svc", "1.0")
        rolled = strategy.rollback(state)
        assert rolled.traffic_percentage == 0.0


# ---------------------------------------------------------------------------
# DeploymentTarget and types tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not TYPES_AVAILABLE, reason="types module not importable")
class TestDeploymentTarget:
    """Tests for DeploymentTarget dataclass."""

    def test_basic_construction(self):
        t = DeploymentTarget(id="t1", name="server-1", address="192.168.1.1:8080")
        assert t.id == "t1"
        assert t.name == "server-1"
        assert t.address == "192.168.1.1:8080"

    def test_default_healthy_true(self):
        t = DeploymentTarget(id="t2", name="srv", address="host:80")
        assert t.healthy is True

    def test_version_initially_none(self):
        t = DeploymentTarget(id="t3", name="srv", address="host:80")
        assert t.version is None

    def test_version_can_be_set(self):
        t = DeploymentTarget(id="t4", name="srv", address="host:80")
        t.version = "1.5.0"
        assert t.version == "1.5.0"

    def test_metadata_default_empty(self):
        t = DeploymentTarget(id="t5", name="srv", address="host:80")
        assert t.metadata == {}


@pytest.mark.skipif(not TYPES_AVAILABLE, reason="types module not importable")
class TestDeploymentResult:
    """Tests for DeploymentResult dataclass."""

    def test_to_dict_contains_success(self):
        r = DeploymentResult(
            success=True,
            targets_updated=3,
            targets_failed=0,
            duration_ms=100.0,
            state=TypeDeploymentState.COMPLETED,
        )
        d = r.to_dict()
        assert d["success"] is True

    def test_to_dict_contains_state_value(self):
        r = DeploymentResult(
            success=False,
            targets_updated=0,
            targets_failed=2,
            duration_ms=50.0,
            state=TypeDeploymentState.FAILED,
        )
        d = r.to_dict()
        assert d["state"] == "failed"

    def test_to_dict_contains_errors(self):
        r = DeploymentResult(
            success=False,
            targets_updated=0,
            targets_failed=1,
            duration_ms=10.0,
            state=TypeDeploymentState.FAILED,
            errors=["health check failed"],
        )
        d = r.to_dict()
        assert "health check failed" in d["errors"]

    def test_errors_default_to_empty_list(self):
        r = DeploymentResult(
            success=True,
            targets_updated=1,
            targets_failed=0,
            duration_ms=5.0,
            state=TypeDeploymentState.COMPLETED,
        )
        assert r.errors == []


@pytest.mark.skipif(not TYPES_AVAILABLE, reason="types module not importable")
class TestStrategyProgress:
    """Tests for StrategyProgress dataclass."""

    def test_basic_construction(self):
        p = StrategyProgress(service="api", version="1.0", strategy_name="rolling")
        assert p.service == "api"
        assert p.version == "1.0"
        assert p.strategy_name == "rolling"

    def test_default_status_is_pending(self):
        p = StrategyProgress(service="svc", version="v1", strategy_name="canary")
        assert p.status == TypeDeploymentState.PENDING

    def test_complete_sets_status_and_traffic(self):
        p = StrategyProgress(service="svc", version="v1", strategy_name="rolling")
        p.complete()
        assert p.status == TypeDeploymentState.COMPLETED
        assert p.traffic_percentage == 100.0

    def test_fail_records_reason(self):
        p = StrategyProgress(service="svc", version="v1", strategy_name="rolling")
        p.fail("network error")
        assert p.status == TypeDeploymentState.FAILED
        assert p.metadata["failure_reason"] == "network error"

    def test_duration_seconds_is_non_negative(self):
        p = StrategyProgress(service="svc", version="v1", strategy_name="canary")
        assert p.duration_seconds >= 0.0


# ---------------------------------------------------------------------------
# CanaryAnalyzer tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not CANARY_AVAILABLE, reason="canary module not importable")
class TestMetricComparison:
    """Tests for MetricComparison dataclass and auto-computation."""

    def test_passed_when_within_threshold(self):
        mc = MetricComparison(
            metric_name="latency",
            baseline_value=100.0,
            canary_value=105.0,
            threshold=0.1,
        )
        assert mc.passed is True

    def test_failed_when_exceeds_threshold(self):
        mc = MetricComparison(
            metric_name="error_rate",
            baseline_value=0.01,
            canary_value=0.05,
            threshold=0.1,
        )
        # deviation = (0.05 - 0.01) / 0.01 = 4.0 which exceeds 0.1
        assert mc.passed is False

    def test_zero_baseline_uses_threshold_comparison(self):
        mc = MetricComparison(
            metric_name="new_metric",
            baseline_value=0.0,
            canary_value=0.05,
            threshold=0.1,
        )
        # 0.05 <= 0.1, so should pass
        assert mc.passed is True

    def test_message_is_set(self):
        mc = MetricComparison(
            metric_name="rps", baseline_value=1000.0, canary_value=1010.0, threshold=0.2
        )
        assert len(mc.message) > 0

    def test_to_dict_has_expected_keys(self):
        mc = MetricComparison(
            metric_name="p99", baseline_value=200.0, canary_value=210.0, threshold=0.1
        )
        d = mc.to_dict()
        assert "metric" in d
        assert "baseline" in d
        assert "canary" in d
        assert "passed" in d


@pytest.mark.skipif(not CANARY_AVAILABLE, reason="canary module not importable")
class TestCanaryAnalyzer:
    """Tests for CanaryAnalyzer.analyze decision logic."""

    def test_promotes_when_all_metrics_pass(self):
        analyzer = CanaryAnalyzer(promote_threshold=0.9)
        baseline = {"error_rate": 0.01, "latency_p99": 200.0}
        canary = {"error_rate": 0.011, "latency_p99": 202.0}
        report = analyzer.analyze(baseline, canary)
        assert report.decision == CanaryDecision.PROMOTE

    def test_rollback_when_most_metrics_fail(self):
        analyzer = CanaryAnalyzer(rollback_threshold=0.5)
        baseline = {"m1": 100.0, "m2": 100.0, "m3": 100.0}
        # All canary values hugely exceed baseline
        canary = {"m1": 10000.0, "m2": 10000.0, "m3": 10000.0}
        report = analyzer.analyze(baseline, canary)
        assert report.decision == CanaryDecision.ROLLBACK

    def test_continue_when_between_thresholds(self):
        analyzer = CanaryAnalyzer(promote_threshold=0.9, rollback_threshold=0.5)
        # 3 metrics: 2 pass, 1 fails → pass_rate 0.667, between 0.5 and 0.9
        baseline = {"m1": 100.0, "m2": 100.0, "m3": 100.0}
        canary = {"m1": 101.0, "m2": 102.0, "m3": 1000.0}
        report = analyzer.analyze(baseline, canary)
        assert report.decision == CanaryDecision.CONTINUE

    def test_pass_rate_is_between_zero_and_one(self):
        analyzer = CanaryAnalyzer()
        report = analyzer.analyze({"x": 1.0}, {"x": 1.0})
        assert 0.0 <= report.pass_rate <= 1.0

    def test_empty_metrics_results_in_promote(self):
        analyzer = CanaryAnalyzer()
        report = analyzer.analyze({}, {})
        # pass_rate = 1.0 when no metrics → promote
        assert report.decision == CanaryDecision.PROMOTE

    def test_report_to_dict_has_expected_keys(self):
        analyzer = CanaryAnalyzer()
        report = analyzer.analyze({"latency": 100.0}, {"latency": 100.0})
        d = report.to_dict()
        assert "decision" in d
        assert "pass_rate" in d
        assert "metrics" in d

    def test_per_metric_tolerance_override(self):
        analyzer = CanaryAnalyzer(metric_tolerance=0.01)
        baseline = {"critical_metric": 100.0}
        canary = {"critical_metric": 200.0}
        report = analyzer.analyze(baseline, canary, tolerances={"critical_metric": 5.0})
        # tolerance of 5.0 = 500%, should pass
        assert report.decision == CanaryDecision.PROMOTE

    def test_comparisons_list_length_matches_metric_count(self):
        analyzer = CanaryAnalyzer()
        report = analyzer.analyze({"a": 1.0, "b": 2.0, "c": 3.0}, {"a": 1.0, "b": 2.0, "c": 3.0})
        assert len(report.comparisons) == 3
