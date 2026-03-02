"""
Unit tests for deployment.manager.manager — Zero-Mock compliant.

Covers DeploymentManager orchestration of strategies.
"""

from __future__ import annotations

import pytest

from codomyrmex.deployment.manager.manager import DeploymentManager
from codomyrmex.deployment.strategies import (
    BlueGreenDeployment,
    CanaryDeployment,
    DeploymentState,
    RollingDeployment,
)


@pytest.mark.unit
class TestDeploymentManager:
    """Tests for DeploymentManager."""

    def test_initial_state_empty(self):
        """Initial state with no history or active deployments."""
        mgr = DeploymentManager()
        assert mgr.history == []
        assert mgr.summary()["total_deployments"] == 0

    def test_deploy_rolling_success(self):
        """Deploying a service using the rolling strategy."""
        mgr = DeploymentManager()
        strat = RollingDeployment(batch_size=1, delay_seconds=0)
        
        result = mgr.deploy("api", "v1.0", strat)

        assert result.success is True
        assert result.state == DeploymentState.COMPLETED
        assert mgr.get_active_version("api") == "v1.0"
        assert len(mgr.history) == 1
        assert mgr.summary()["completed"] == 1

    def test_deploy_rolling_failure(self):
        """Deploying a service that fails updating some targets."""
        mgr = DeploymentManager()
        strat = RollingDeployment(batch_size=1, delay_seconds=0)

        # Custom deploy function to simulate failure
        class BadStrategy(RollingDeployment):
            def deploy(self, targets, version, deploy_fn):
                return super().deploy(targets, version, lambda t, v: False)

        result = mgr.deploy("api", "v1.0", BadStrategy())

        assert result.success is False
        assert result.state == DeploymentState.FAILED
        assert mgr.get_active_version("api") is None
        assert mgr.summary()["failed"] == 1

    def test_deploy_canary_success(self):
        """Deploying a service using the canary strategy."""
        mgr = DeploymentManager()
        strat = CanaryDeployment(stages=[10, 50, 100], stage_duration_seconds=0)

        result = mgr.deploy("api", "v1.0", strat)

        assert result.success is True
        assert result.state == DeploymentState.COMPLETED
        assert mgr.get_active_version("api") == "v1.0"

    def test_rollback_success(self):
        """Rolling back a service to a previous version."""
        mgr = DeploymentManager()
        mgr.deploy("api", "v2.0", RollingDeployment())
        assert mgr.get_active_version("api") == "v2.0"

        result = mgr.rollback("api", "v1.0", RollingDeployment())

        assert result.success is True
        assert result.state == DeploymentState.COMPLETED
        assert mgr.get_active_version("api") == "v1.0"
        # Two history entries: one for deploy, one for rollback
        assert len(mgr.history) == 2

    def test_deploy_exception_recovery(self):
        """Recovery from an exception during strategy execution."""
        mgr = DeploymentManager()

        class ExplodingStrategy(RollingDeployment):
            def deploy(self, targets, version, deploy_fn):
                raise RuntimeError("unhandled explosion")

        result = mgr.deploy("api", "v1.0", ExplodingStrategy())

        assert result.success is False
        assert result.state == DeploymentState.FAILED
        assert "unhandled explosion" in result.errors[0]
        assert mgr.summary()["failed"] == 1

    def test_summary_accuracy(self):
        """Summary metrics should accurately reflect history."""
        mgr = DeploymentManager()
        
        # 1 Success
        mgr.deploy("svc1", "v1", RollingDeployment())
        # 1 Fail
        class FailStrat(RollingDeployment):
            def deploy(self, targets, version, deploy_fn):
                return super().deploy(targets, version, lambda t, v: False)
        mgr.deploy("svc2", "v2", FailStrat())
        # 1 Rollback
        mgr.rollback("svc1", "v0", BlueGreenDeployment())

        summary = mgr.summary()
        assert summary["total_deployments"] == 3
        assert summary["completed"] == 1
        assert summary["failed"] == 1
        assert summary["rolled_back"] == 1
        assert "svc1" in summary["active_services"]
        assert "svc2" not in summary["active_services"]
