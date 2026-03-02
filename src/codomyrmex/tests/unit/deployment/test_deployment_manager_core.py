"""
Unit tests for deployment.manager.manager — Zero-Mock compliant.

Covers DeploymentManager and the standalone strategies in
deployment/manager/manager.py and deployment/strategies/strategies.py.

These import from the DIRECT module paths (not the package __init__.py)
to achieve coverage of the isolated implementation files.
"""

import pytest

from codomyrmex.deployment.manager.manager import DeploymentManager
from codomyrmex.deployment.strategies.strategies import (
    BlueGreenStrategy,
    CanaryStrategy,
    DeploymentState,
    DeploymentStrategy,
    FeatureFlagStrategy,
    RollingStrategy,
)

# ── DeploymentState ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeploymentState:
    """Tests for DeploymentState dataclass (in strategies.py)."""

    def test_initial_status_is_pending(self):
        s = DeploymentState(service="svc", version="v1", strategy="rolling")
        assert s.status == "pending"
        assert s.traffic_percentage == 0.0

    def test_complete_sets_status(self):
        s = DeploymentState(service="svc", version="v1", strategy="rolling")
        s.complete()
        assert s.status == "completed"
        assert s.traffic_percentage == 100.0
        assert s.completed_at is not None

    def test_fail_sets_status_and_reason(self):
        s = DeploymentState(service="svc", version="v1", strategy="rolling")
        s.fail("out of memory")
        assert s.status == "failed"
        assert s.metadata["failure_reason"] == "out of memory"

    def test_duration_seconds_before_completion(self):
        s = DeploymentState(service="svc", version="v1", strategy="rolling")
        duration = s.duration_seconds
        assert duration >= 0.0

    def test_duration_seconds_after_completion(self):
        s = DeploymentState(service="svc", version="v1", strategy="rolling")
        s.complete()
        duration = s.duration_seconds
        assert duration >= 0.0


# ── RollingStrategy ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRollingStrategy:
    """Tests for RollingStrategy."""

    def test_execute_returns_completed_state(self):
        strat = RollingStrategy(batch_size=1, batch_count=3, pause_seconds=0)
        state = strat.execute("api", "v1.0")
        assert state.status == "completed"
        assert state.traffic_percentage == 100.0

    def test_execute_service_and_version_stored(self):
        strat = RollingStrategy()
        state = strat.execute("my-service", "2.0.0")
        assert state.service == "my-service"
        assert state.version == "2.0.0"

    def test_rollback_sets_rolled_back(self):
        strat = RollingStrategy()
        state = strat.execute("svc", "v1")
        rolled = strat.rollback(state)
        assert rolled.status == "rolled_back"
        assert rolled.traffic_percentage == 0.0


# ── CanaryStrategy ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCanaryStrategy:
    """Tests for CanaryStrategy."""

    def test_execute_returns_completed(self):
        strat = CanaryStrategy(initial_percentage=10, step=30, max_steps=4)
        state = strat.execute("frontend", "v3.0")
        assert state.status == "completed"

    def test_rollback_resets_traffic(self):
        strat = CanaryStrategy()
        state = strat.execute("svc", "v1")
        rolled = strat.rollback(state)
        assert rolled.status == "rolled_back"
        assert rolled.traffic_percentage == 0.0


# ── BlueGreenStrategy ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestBlueGreenStrategy:
    """Tests for BlueGreenStrategy."""

    def test_execute_switches_to_green(self):
        strat = BlueGreenStrategy()
        state = strat.execute("backend", "v5.0")
        assert state.status == "completed"
        assert state.metadata.get("active_slot") == "green"

    def test_rollback_switches_to_blue(self):
        strat = BlueGreenStrategy()
        state = strat.execute("backend", "v5.0")
        rolled = strat.rollback(state)
        assert rolled.status == "rolled_back"
        assert rolled.metadata["active_slot"] == "blue"


# ── FeatureFlagStrategy ────────────────────────────────────────────────────


@pytest.mark.unit
class TestFeatureFlagStrategy:
    """Tests for FeatureFlagStrategy."""

    def test_execute_with_explicit_flag(self):
        strat = FeatureFlagStrategy(flag_name="my_flag", initial_rollout=5.0)
        state = strat.execute("svc", "v2")
        assert state.status == "completed"
        assert state.metadata["flag_name"] == "my_flag"
        # complete() is called by execute(), which sets traffic_percentage=100.0

    def test_execute_auto_names_flag(self):
        strat = FeatureFlagStrategy()
        state = strat.execute("payments", "v2.1")
        # Auto flag name should contain service and version
        assert "payments" in state.metadata["flag_name"]
        assert "v2.1" in state.metadata["flag_name"]

    def test_rollback_disables_flag(self):
        strat = FeatureFlagStrategy(flag_name="ff_test")
        state = strat.execute("svc", "v1")
        rolled = strat.rollback(state)
        assert rolled.status == "rolled_back"
        assert rolled.traffic_percentage == 0.0


# ── DeploymentManager ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeploymentManager:
    """Tests for DeploymentManager in manager/manager.py."""

    def test_initial_state_empty(self):
        mgr = DeploymentManager()
        assert mgr.history == []
        assert mgr.active_deployments == {}

    def test_deploy_rolling_returns_completed_state(self):
        mgr = DeploymentManager()
        strat = RollingStrategy(batch_size=1, batch_count=2, pause_seconds=0)
        state = mgr.deploy("api", "v1.0", strat)
        assert state.status == "completed"
        assert state.service == "api"
        assert state.version == "v1.0"

    def test_deploy_records_in_history(self):
        mgr = DeploymentManager()
        mgr.deploy("svc", "v1", RollingStrategy(batch_count=1, pause_seconds=0))
        assert len(mgr.history) == 1

    def test_deploy_sets_active(self):
        mgr = DeploymentManager()
        mgr.deploy("svc", "v1", RollingStrategy(batch_count=1, pause_seconds=0))
        active = mgr.get_active("svc")
        assert active is not None
        assert active.service == "svc"

    def test_multiple_deploys_stack_in_history(self):
        mgr = DeploymentManager()
        strat = RollingStrategy(batch_count=1, pause_seconds=0)
        mgr.deploy("svc", "v1", strat)
        mgr.deploy("svc", "v2", strat)
        assert len(mgr.history) == 2

    def test_get_active_returns_latest(self):
        mgr = DeploymentManager()
        strat = RollingStrategy(batch_count=1, pause_seconds=0)
        mgr.deploy("svc", "v1", strat)
        mgr.deploy("svc", "v2", strat)
        active = mgr.get_active("svc")
        assert active.version == "v2"

    def test_get_active_unknown_service_returns_none(self):
        mgr = DeploymentManager()
        assert mgr.get_active("no-such-service") is None

    def test_rollback_no_active_returns_none(self):
        mgr = DeploymentManager()
        result = mgr.rollback("no-service", RollingStrategy(batch_count=1, pause_seconds=0))
        assert result is None

    def test_rollback_active_deployment(self):
        mgr = DeploymentManager()
        mgr.deploy("svc", "v1", RollingStrategy(batch_count=1, pause_seconds=0))
        rolled = mgr.rollback("svc", RollingStrategy(batch_count=1, pause_seconds=0))
        assert rolled is not None
        assert rolled.status == "rolled_back"
        # After rollback, no more active
        assert mgr.get_active("svc") is None

    def test_rollback_adds_to_history(self):
        mgr = DeploymentManager()
        mgr.deploy("svc", "v1", RollingStrategy(batch_count=1, pause_seconds=0))
        mgr.rollback("svc", RollingStrategy(batch_count=1, pause_seconds=0))
        assert len(mgr.history) == 2

    def test_summary_counts(self):
        mgr = DeploymentManager()
        strat = RollingStrategy(batch_count=1, pause_seconds=0)
        mgr.deploy("svc-a", "v1", strat)
        mgr.deploy("svc-b", "v1", strat)
        summary = mgr.summary()
        assert summary["total_deployments"] == 2
        assert summary["completed"] == 2
        assert summary["failed"] == 0

    def test_summary_failed_count(self):
        mgr = DeploymentManager()

        class _FailStrat(DeploymentStrategy):
            def execute(self, sn, v):
                raise RuntimeError("deployment error")

            def rollback(self, state):
                return state

        mgr.deploy("svc", "v1", _FailStrat())
        summary = mgr.summary()
        assert summary["failed"] == 1
        assert summary["completed"] == 0

    def test_active_deployments_property(self):
        mgr = DeploymentManager()
        mgr.deploy("svc-a", "v1", RollingStrategy(batch_count=1, pause_seconds=0))
        mgr.deploy("svc-b", "v2", CanaryStrategy(max_steps=1))
        active = mgr.active_deployments
        assert "svc-a" in active
        assert "svc-b" in active

    def test_deploy_exception_recorded_as_failed(self):
        mgr = DeploymentManager()

        class _BadStrat(DeploymentStrategy):
            def execute(self, sn, v):
                raise ValueError("bad config")

            def rollback(self, state):
                return state

        state = mgr.deploy("svc", "v1", _BadStrat())
        assert state.status == "failed"
        assert "bad config" in state.metadata.get("failure_reason", "")
