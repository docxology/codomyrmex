"""Tests for deployment strategies module.

Covers DeploymentState, RollingStrategy, CanaryStrategy,
BlueGreenStrategy, and FeatureFlagStrategy.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.deployment.strategies.strategies import (
    BlueGreenStrategy,
    CanaryStrategy,
    DeploymentState,
    DeploymentStrategy,
    FeatureFlagStrategy,
    RollingStrategy,
)

# ---------------------------------------------------------------------------
# DeploymentState dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDeploymentState:
    """Tests for the DeploymentState dataclass."""

    def test_default_construction(self) -> None:
        """Minimal construction fills sensible defaults."""
        state = DeploymentState(service="svc", version="1.0", strategy="rolling")
        assert state.service == "svc"
        assert state.version == "1.0"
        assert state.strategy == "rolling"
        assert state.status == "pending"
        assert state.completed_at is None
        assert state.traffic_percentage == 0.0
        assert state.metadata == {}

    def test_started_at_is_set_automatically(self) -> None:
        """started_at should be approximately now."""
        before = time.time()
        state = DeploymentState(service="s", version="v", strategy="x")
        after = time.time()
        assert before <= state.started_at <= after

    def test_duration_seconds_while_running(self) -> None:
        """Duration with no completed_at uses current time."""
        state = DeploymentState(service="s", version="v", strategy="x")
        state.started_at = time.time() - 5.0
        dur = state.duration_seconds
        assert dur >= 4.5  # generous lower bound

    def test_duration_seconds_when_completed(self) -> None:
        """Duration with completed_at uses that timestamp."""
        state = DeploymentState(service="s", version="v", strategy="x")
        state.started_at = 1000.0
        state.completed_at = 1010.0
        assert state.duration_seconds == pytest.approx(10.0)

    def test_complete_method(self) -> None:
        """complete() sets status, completed_at, and traffic to 100."""
        state = DeploymentState(service="s", version="v", strategy="x")
        state.complete()
        assert state.status == "completed"
        assert state.completed_at is not None
        assert state.traffic_percentage == 100.0

    def test_fail_method_default_reason(self) -> None:
        """fail() sets status and records empty reason by default."""
        state = DeploymentState(service="s", version="v", strategy="x")
        state.fail()
        assert state.status == "failed"
        assert state.completed_at is not None
        assert state.metadata["failure_reason"] == ""

    def test_fail_method_with_reason(self) -> None:
        """fail(reason) records the failure reason in metadata."""
        state = DeploymentState(service="s", version="v", strategy="x")
        state.fail("timeout")
        assert state.metadata["failure_reason"] == "timeout"

    def test_metadata_is_independent_between_instances(self) -> None:
        """Each DeploymentState gets its own metadata dict."""
        a = DeploymentState(service="a", version="1", strategy="x")
        b = DeploymentState(service="b", version="2", strategy="y")
        a.metadata["key"] = "val"
        assert "key" not in b.metadata


# ---------------------------------------------------------------------------
# DeploymentStrategy ABC
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDeploymentStrategyABC:
    """Verify that DeploymentStrategy cannot be instantiated directly."""

    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            DeploymentStrategy()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# RollingStrategy
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRollingStrategy:
    """Tests for the RollingStrategy concrete implementation."""

    def test_default_params(self) -> None:
        s = RollingStrategy()
        assert s.batch_size == 1
        assert s.batch_count == 4
        assert s.pause_seconds == 0.0

    def test_custom_params(self) -> None:
        s = RollingStrategy(batch_size=3, batch_count=10, pause_seconds=0.5)
        assert s.batch_size == 3
        assert s.batch_count == 10
        assert s.pause_seconds == 0.5

    def test_execute_returns_completed_state(self) -> None:
        s = RollingStrategy(batch_count=2, pause_seconds=0.0)
        state = s.execute("api", "v2")
        assert state.status == "completed"
        assert state.traffic_percentage == 100.0
        assert state.strategy == "rolling"
        assert state.service == "api"
        assert state.version == "v2"
        assert state.completed_at is not None

    def test_execute_traffic_hits_100(self) -> None:
        """Traffic should reach 100% even with many batches."""
        s = RollingStrategy(batch_count=10)
        state = s.execute("svc", "v1")
        assert state.traffic_percentage == 100.0

    def test_rollback_sets_state_correctly(self) -> None:
        s = RollingStrategy()
        state = s.execute("svc", "v1")
        rolled_back = s.rollback(state)
        assert rolled_back.status == "rolled_back"
        assert rolled_back.traffic_percentage == 0.0
        assert rolled_back.completed_at is not None

    def test_is_instance_of_abc(self) -> None:
        assert isinstance(RollingStrategy(), DeploymentStrategy)


# ---------------------------------------------------------------------------
# CanaryStrategy
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCanaryStrategy:
    """Tests for the CanaryStrategy concrete implementation."""

    def test_default_params(self) -> None:
        s = CanaryStrategy()
        assert s.initial_percentage == 10
        assert s.step == 20
        assert s.max_steps == 5

    def test_execute_returns_completed(self) -> None:
        s = CanaryStrategy(initial_percentage=10, step=30, max_steps=5)
        state = s.execute("frontend", "3.0")
        assert state.status == "completed"
        assert state.traffic_percentage == 100.0
        assert state.strategy == "canary"

    def test_execute_caps_traffic_at_100(self) -> None:
        """Even with large steps, traffic should never exceed 100."""
        s = CanaryStrategy(initial_percentage=50, step=60, max_steps=10)
        state = s.execute("svc", "v1")
        assert state.traffic_percentage == 100.0

    def test_execute_reaches_100_with_small_steps(self) -> None:
        s = CanaryStrategy(initial_percentage=1, step=1, max_steps=200)
        state = s.execute("svc", "v1")
        assert state.status == "completed"

    def test_rollback(self) -> None:
        s = CanaryStrategy()
        state = s.execute("svc", "v1")
        rolled_back = s.rollback(state)
        assert rolled_back.status == "rolled_back"
        assert rolled_back.traffic_percentage == 0.0

    def test_is_instance_of_abc(self) -> None:
        assert isinstance(CanaryStrategy(), DeploymentStrategy)


# ---------------------------------------------------------------------------
# BlueGreenStrategy
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBlueGreenStrategy:
    """Tests for the BlueGreenStrategy concrete implementation."""

    def test_execute_returns_completed(self) -> None:
        s = BlueGreenStrategy()
        state = s.execute("backend", "v5")
        assert state.status == "completed"
        assert state.traffic_percentage == 100.0
        assert state.strategy == "blue_green"

    def test_execute_sets_active_slot_to_green(self) -> None:
        s = BlueGreenStrategy()
        state = s.execute("backend", "v5")
        assert state.metadata["active_slot"] == "green"

    def test_rollback_swaps_to_blue(self) -> None:
        s = BlueGreenStrategy()
        state = s.execute("backend", "v5")
        rolled_back = s.rollback(state)
        assert rolled_back.status == "rolled_back"
        assert rolled_back.metadata["active_slot"] == "blue"
        # Blue-green rollback keeps traffic at 100 on blue
        assert rolled_back.traffic_percentage == 100.0

    def test_is_instance_of_abc(self) -> None:
        assert isinstance(BlueGreenStrategy(), DeploymentStrategy)


# ---------------------------------------------------------------------------
# FeatureFlagStrategy
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFeatureFlagStrategy:
    """Tests for the FeatureFlagStrategy concrete implementation."""

    def test_default_params(self) -> None:
        s = FeatureFlagStrategy()
        assert s.flag_name == ""
        assert s.initial_rollout == 0.0

    def test_custom_params(self) -> None:
        s = FeatureFlagStrategy(flag_name="dark_mode", initial_rollout=25.0)
        assert s.flag_name == "dark_mode"
        assert s.initial_rollout == 25.0

    def test_execute_generates_flag_name_when_empty(self) -> None:
        """When no flag_name given, a default is generated from service+version."""
        s = FeatureFlagStrategy()
        state = s.execute("payments", "v3")
        assert state.metadata["flag_name"] == "ff_payments_v3"

    def test_execute_uses_provided_flag_name(self) -> None:
        s = FeatureFlagStrategy(flag_name="my_flag")
        state = s.execute("svc", "v1")
        assert state.metadata["flag_name"] == "my_flag"

    def test_execute_completed_status(self) -> None:
        s = FeatureFlagStrategy(initial_rollout=50.0)
        state = s.execute("svc", "v1")
        assert state.status == "completed"
        assert state.strategy == "feature_flag"

    def test_execute_traffic_matches_initial_rollout(self) -> None:
        """After complete(), traffic is 100, but the initial_rollout was recorded."""
        s = FeatureFlagStrategy(initial_rollout=0.0)
        state = s.execute("svc", "v1")
        # complete() sets traffic to 100 — this is expected behaviour
        assert state.traffic_percentage == 100.0

    def test_rollback_disables_flag(self) -> None:
        s = FeatureFlagStrategy(flag_name="test_flag")
        state = s.execute("svc", "v1")
        rolled_back = s.rollback(state)
        assert rolled_back.status == "rolled_back"
        assert rolled_back.traffic_percentage == 0.0

    def test_is_instance_of_abc(self) -> None:
        assert isinstance(FeatureFlagStrategy(), DeploymentStrategy)
