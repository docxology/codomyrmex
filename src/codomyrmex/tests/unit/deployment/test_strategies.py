"""
Unit tests for deployment.strategies — Zero-Mock compliant.

Covers RollingDeployment, CanaryDeployment, and BlueGreenDeployment.
"""

from __future__ import annotations

import pytest

from codomyrmex.deployment.strategies import (
    BlueGreenDeployment,
    CanaryDeployment,
    DeploymentState,
    DeploymentTarget,
    RollingDeployment,
)


@pytest.mark.unit
class TestRollingDeployment:
    """Tests for RollingDeployment strategy."""

    def test_deploy_all_success(self):
        """Standard rolling deploy with all targets succeeding."""
        strat = RollingDeployment(batch_size=1, delay_seconds=0)
        targets = [
            DeploymentTarget(id="t1", name="target1", address="1.1.1.1"),
            DeploymentTarget(id="t2", name="target2", address="1.1.1.2"),
        ]

        def deploy_fn(target, version):
            return True

        result = strat.deploy(targets, "v2.0", deploy_fn)

        assert result.success is True
        assert result.targets_updated == 2
        assert result.targets_failed == 0
        assert result.state == DeploymentState.COMPLETED
        assert targets[0].version == "v2.0"
        assert targets[1].version == "v2.0"

    def test_deploy_with_failure(self):
        """Rolling deploy where one target fails."""
        strat = RollingDeployment(batch_size=1, delay_seconds=0)
        targets = [
            DeploymentTarget(id="t1", name="target1", address="1.1.1.1"),
            DeploymentTarget(id="t2", name="target2", address="1.1.1.2"),
        ]

        def deploy_fn(target, version):
            return target.id == "t1"

        result = strat.deploy(targets, "v2.0", deploy_fn)

        assert result.success is False
        assert result.targets_updated == 1
        assert result.targets_failed == 1
        assert result.state == DeploymentState.FAILED
        assert targets[0].version == "v2.0"
        assert targets[1].version is None

    def test_deploy_with_health_check(self):
        """Rolling deploy with an integrated health check."""
        def health_check(target):
            return target.id == "t1"

        strat = RollingDeployment(batch_size=1, delay_seconds=0, health_check=health_check)
        targets = [
            DeploymentTarget(id="t1", name="target1", address="1.1.1.1"),
            DeploymentTarget(id="t2", name="target2", address="1.1.1.2"),
        ]

        def deploy_fn(target, version):
            return True

        result = strat.deploy(targets, "v2.0", deploy_fn)

        assert result.success is False
        assert result.targets_updated == 1
        assert result.targets_failed == 1
        assert targets[0].healthy is True
        assert targets[1].healthy is False


@pytest.mark.unit
class TestBlueGreenDeployment:
    """Tests for BlueGreenDeployment strategy."""

    def test_deploy_success_with_switch(self):
        """Blue-green deploy with successful switch."""
        switched_version = None

        def switch_fn(version):
            nonlocal switched_version
            switched_version = version
            return True

        strat = BlueGreenDeployment(switch_fn=switch_fn)
        targets = [
            DeploymentTarget(id="t1", name="target1", address="1.1.1.1"),
        ]

        result = strat.deploy(targets, "v2.0", lambda t, v: True)

        assert result.success is True
        assert result.state == DeploymentState.COMPLETED
        assert switched_version == "v2.0"
        assert result.metadata["active_slot"] == "green"

    def test_deploy_failure_no_switch(self):
        """Blue-green deploy that fails during target update, preventing switch."""
        switched_version = None

        def switch_fn(version):
            nonlocal switched_version
            switched_version = version
            return True

        strat = BlueGreenDeployment(switch_fn=switch_fn)
        targets = [
            DeploymentTarget(id="t1", name="target1", address="1.1.1.1"),
        ]

        result = strat.deploy(targets, "v2.0", lambda t, v: False)

        assert result.success is False
        assert result.state == DeploymentState.FAILED
        assert switched_version is None
        assert result.metadata["active_slot"] == "blue"

    def test_rollback(self):
        """Blue-green rollback should trigger switch back."""
        switched_version = None

        def switch_fn(version):
            nonlocal switched_version
            switched_version = version
            return True

        strat = BlueGreenDeployment(switch_fn=switch_fn)
        targets = [DeploymentTarget(id="t1", name="t1", address="")]

        result = strat.rollback(targets, "v1.0", lambda t, v: True)

        assert result.success is True
        assert result.state == DeploymentState.ROLLED_BACK
        assert switched_version == "v1.0"
        assert result.metadata["active_slot"] == "blue"


@pytest.mark.unit
class TestCanaryDeployment:
    """Tests for CanaryDeployment strategy."""

    def test_deploy_full_success(self):
        """Canary deploy through all stages successfully."""
        strat = CanaryDeployment(stages=[50.0, 100.0], stage_duration_seconds=0)
        targets = [
            DeploymentTarget(id="t1", name="t1", address=""),
            DeploymentTarget(id="t2", name="t2", address=""),
            DeploymentTarget(id="t3", name="t3", address=""),
            DeploymentTarget(id="t4", name="t4", address=""),
        ]

        result = strat.deploy(targets, "v2.0", lambda t, v: True)

        assert result.success is True
        assert result.targets_updated == 4
        assert result.state == DeploymentState.COMPLETED
        for t in targets:
            assert t.version == "v2.0"

    def test_deploy_aborted_by_threshold(self):
        """Canary deploy aborted when success rate falls below threshold."""
        strat = CanaryDeployment(stages=[50.0, 100.0], success_threshold=0.9)
        targets = [
            DeploymentTarget(id="t1", name="t1", address=""),
            DeploymentTarget(id="t2", name="t2", address=""),
        ]

        # Fail the first target in the first stage (50%)
        def deploy_fn(target, version):
            return target.id != "t1"

        result = strat.deploy(targets, "v2.0", deploy_fn)

        assert result.success is False
        assert result.state == DeploymentState.FAILED
        assert result.targets_updated == 0  # Stage 1: t1 fails, stage aborted
        assert result.metadata["stopped_at_stage"] == 50.0

    def test_rollback(self):
        """Canary rollback uses rolling deployment to restore version."""
        strat = CanaryDeployment()
        targets = [DeploymentTarget(id="t1", name="t1", address="")]

        result = strat.rollback(targets, "v1.0", lambda t, v: True)

        assert result.success is True
        assert result.state == DeploymentState.ROLLED_BACK
        assert targets[0].version == "v1.0"
