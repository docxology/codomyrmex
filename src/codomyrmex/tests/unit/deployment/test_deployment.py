"""Comprehensive tests for the deployment module.

Tests cover deployment strategies, health checks, rollback, the DeploymentManager,
GitOpsSynchronizer, and edge cases such as failed deployments and invalid configs.
"""

import subprocess

import pytest

from codomyrmex.deployment import (
    BlueGreenStrategy,
    CanaryStrategy,
    DeploymentManager,
    DeploymentResult,
    DeploymentState,
    DeploymentTarget,
    GitOpsSynchronizer,
    RollingStrategy,
    create_strategy,
)
from codomyrmex.deployment.health_checks import (
    AggregatedHealth,
    CommandHealthCheck,
    DiskHealthCheck,
    HealthCheck,
    HealthCheckResult,
    HealthChecker,
    HealthStatus,
)


# ---------------------------------------------------------------------------
# DeploymentTarget
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_deployment_target_creation():
    """Test DeploymentTarget default construction."""
    target = DeploymentTarget(id="t-1", name="node-1", address="localhost:8000")
    assert target.id == "t-1"
    assert target.healthy is True
    assert target.version is None
    assert target.metadata == {}


@pytest.mark.unit
def test_deployment_target_with_metadata():
    """Test DeploymentTarget with metadata and version."""
    target = DeploymentTarget(
        id="t-2", name="node-2", address="10.0.0.1:8080",
        healthy=False, version="v1.2", metadata={"zone": "us-east"},
    )
    assert target.version == "v1.2"
    assert target.metadata["zone"] == "us-east"
    assert target.healthy is False


# ---------------------------------------------------------------------------
# DeploymentResult
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_deployment_result_to_dict():
    """Test DeploymentResult serialization."""
    result = DeploymentResult(
        success=True, targets_updated=3, targets_failed=0,
        duration_ms=150.0, state=DeploymentState.COMPLETED,
    )
    d = result.to_dict()
    assert d["success"] is True
    assert d["state"] == "completed"
    assert d["targets_updated"] == 3
    assert d["errors"] == []


@pytest.mark.unit
def test_deployment_result_with_errors():
    """Test DeploymentResult with failures recorded."""
    result = DeploymentResult(
        success=False, targets_updated=1, targets_failed=2,
        duration_ms=500.0, state=DeploymentState.FAILED,
        errors=["timeout on t-2", "crash on t-3"],
    )
    assert len(result.errors) == 2
    assert result.targets_failed == 2


# ---------------------------------------------------------------------------
# DeploymentState enum
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_deployment_state_values():
    """Test all deployment state enum values exist."""
    assert DeploymentState.PENDING.value == "pending"
    assert DeploymentState.IN_PROGRESS.value == "in_progress"
    assert DeploymentState.COMPLETED.value == "completed"
    assert DeploymentState.FAILED.value == "failed"
    assert DeploymentState.ROLLED_BACK.value == "rolled_back"
    assert DeploymentState.PAUSED.value == "paused"


# ---------------------------------------------------------------------------
# RollingDeployment strategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_rolling_deployment_all_succeed():
    """Test rolling deployment where all targets succeed."""
    strategy = RollingStrategy(batch_size=2, delay_seconds=0)
    targets = [
        DeploymentTarget(id=f"t-{i}", name=f"n-{i}", address=f"localhost:{8000 + i}")
        for i in range(4)
    ]
    deploy_fn = lambda t, v: True
    result = strategy.deploy(targets, "v2", deploy_fn)

    assert result.success is True
    assert result.targets_updated == 4
    assert result.targets_failed == 0
    assert result.state == DeploymentState.COMPLETED


@pytest.mark.unit
def test_rolling_deployment_partial_failure():
    """Test rolling deployment where some targets fail."""
    strategy = RollingStrategy(batch_size=1, delay_seconds=0)
    targets = [
        DeploymentTarget(id=f"t-{i}", name=f"n-{i}", address=f"localhost:{8000 + i}")
        for i in range(3)
    ]
    # Second target fails
    call_count = 0
    def deploy_fn(t, v):
        nonlocal call_count
        call_count += 1
        return call_count != 2

    result = strategy.deploy(targets, "v2", deploy_fn)
    assert result.success is False
    assert result.targets_failed == 1
    assert result.state == DeploymentState.FAILED


@pytest.mark.unit
def test_rolling_deployment_with_health_check():
    """Test rolling deployment with health check callback."""
    strategy = RollingStrategy(
        batch_size=1, delay_seconds=0,
        health_check=lambda t: t.id != "t-1",  # t-1 fails health check
    )
    targets = [
        DeploymentTarget(id=f"t-{i}", name=f"n-{i}", address=f"localhost:{8000 + i}")
        for i in range(3)
    ]
    result = strategy.deploy(targets, "v3", lambda t, v: True)
    assert result.targets_failed == 1  # t-1 fails health check


@pytest.mark.unit
def test_rolling_deployment_rollback():
    """Test rolling rollback delegates to deploy."""
    strategy = RollingStrategy(batch_size=1, delay_seconds=0)
    targets = [
        DeploymentTarget(id="t-0", name="n-0", address="localhost:8000")
    ]
    result = strategy.rollback(targets, "v1", lambda t, v: True)
    assert result.success is True


# ---------------------------------------------------------------------------
# BlueGreenDeployment strategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_blue_green_deployment_success():
    """Test blue-green deployment with successful switch."""
    switch_calls = []
    strategy = BlueGreenStrategy(switch_fn=lambda v: switch_calls.append(v) or True)
    targets = [
        DeploymentTarget(id="t-0", name="blue", address="localhost:8000"),
        DeploymentTarget(id="t-1", name="green", address="localhost:8001"),
    ]
    result = strategy.deploy(targets, "v2", lambda t, v: True)
    assert result.success is True
    assert "v2" in switch_calls


@pytest.mark.unit
def test_blue_green_deployment_rollback():
    """Test blue-green rollback switches traffic back."""
    switch_calls = []
    strategy = BlueGreenStrategy(switch_fn=lambda v: switch_calls.append(v) or True)
    targets = [DeploymentTarget(id="t-0", name="n", address="localhost:8000")]
    result = strategy.rollback(targets, "v1", lambda t, v: True)
    assert result.success is True
    assert result.state == DeploymentState.ROLLED_BACK


# ---------------------------------------------------------------------------
# CanaryDeployment strategy
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_canary_deployment_full_rollout():
    """Test canary deployment progresses through all stages."""
    strategy = CanaryStrategy(stages=[50, 100], stage_duration_seconds=0)
    targets = [
        DeploymentTarget(id=f"t-{i}", name=f"n-{i}", address=f"localhost:{8000 + i}")
        for i in range(4)
    ]
    result = strategy.deploy(targets, "v2", lambda t, v: True)
    assert result.success is True
    assert result.state == DeploymentState.COMPLETED


@pytest.mark.unit
def test_canary_deployment_stops_on_failure():
    """Test canary halts when success rate drops below threshold."""
    strategy = CanaryStrategy(
        stages=[50, 100], stage_duration_seconds=0, success_threshold=1.0,
    )
    targets = [
        DeploymentTarget(id=f"t-{i}", name=f"n-{i}", address=f"localhost:{8000 + i}")
        for i in range(4)
    ]
    call_count = 0
    def flaky_deploy(t, v):
        nonlocal call_count
        call_count += 1
        return call_count != 1  # First call fails

    result = strategy.deploy(targets, "v2", flaky_deploy)
    # Should fail because success rate < 1.0 at first stage
    assert result.success is False
    assert result.state == DeploymentState.FAILED


# ---------------------------------------------------------------------------
# create_strategy factory
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_create_strategy_rolling():
    """Test factory creates rolling strategy."""
    s = create_strategy("rolling", batch_size=3, delay_seconds=0)
    assert isinstance(s, RollingStrategy)


@pytest.mark.unit
def test_create_strategy_blue_green():
    """Test factory creates blue-green strategy."""
    s = create_strategy("blue_green")
    assert isinstance(s, BlueGreenStrategy)


@pytest.mark.unit
def test_create_strategy_canary():
    """Test factory creates canary strategy."""
    s = create_strategy("canary", stages=[25, 50, 100], stage_duration_seconds=0)
    assert isinstance(s, CanaryStrategy)


@pytest.mark.unit
def test_create_strategy_unknown_raises():
    """Test factory raises on unknown strategy type."""
    with pytest.raises(ValueError, match="Unknown strategy"):
        create_strategy("invalid_strategy")


# ---------------------------------------------------------------------------
# DeploymentManager
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_manager_default_strategy():
    """Test manager uses rolling strategy by default."""
    manager = DeploymentManager()
    result = manager.deploy("svc-a", "v1")
    assert result is True


@pytest.mark.unit
def test_manager_deployment_history():
    """Test manager records deployment history."""
    manager = DeploymentManager()
    manager.deploy("svc-a", "v1")
    manager.deploy("svc-b", "v2")
    history = manager.get_deployment_history()
    assert len(history) == 2
    assert history[0]["service"] == "svc-a"
    assert history[1]["version"] == "v2"


@pytest.mark.unit
def test_manager_deploy_failure_recorded():
    """Test manager records failed deployments from raising strategies."""
    class FailingStrategy:
        def deploy(self, service_name, version):
            raise RuntimeError("crash")

    manager = DeploymentManager()
    result = manager.deploy("svc-fail", "v1", FailingStrategy())
    assert result is False
    history = manager.get_deployment_history()
    assert history[-1]["success"] is False


@pytest.mark.unit
def test_manager_rollback():
    """Test manager rollback delegates to deploy."""
    manager = DeploymentManager()
    result = manager.rollback("svc-a", "v0")
    assert result is True


# ---------------------------------------------------------------------------
# HealthCheck classes
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_health_status_enum_values():
    """Test HealthStatus has all expected values."""
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.UNHEALTHY.value == "unhealthy"
    assert HealthStatus.DEGRADED.value == "degraded"
    assert HealthStatus.UNKNOWN.value == "unknown"


@pytest.mark.unit
def test_health_check_result_to_dict():
    """Test HealthCheckResult serialization."""
    result = HealthCheckResult(
        name="test-check", status=HealthStatus.HEALTHY,
        message="OK", latency_ms=5.2,
    )
    d = result.to_dict()
    assert d["name"] == "test-check"
    assert d["status"] == "healthy"
    assert d["latency_ms"] == 5.2


@pytest.mark.unit
def test_command_health_check_success():
    """Test CommandHealthCheck with a simple successful command."""
    check = CommandHealthCheck(
        name="echo-check", command=["echo", "hello"],
        expected_exit_code=0, timeout=5.0,
    )
    result = check.check()
    assert result.status == HealthStatus.HEALTHY
    assert result.latency_ms >= 0


@pytest.mark.unit
def test_command_health_check_failure():
    """Test CommandHealthCheck with a failing command."""
    check = CommandHealthCheck(
        name="fail-check", command=["false"],
        expected_exit_code=0, timeout=5.0,
    )
    result = check.check()
    assert result.status == HealthStatus.UNHEALTHY


@pytest.mark.unit
def test_disk_health_check():
    """Test DiskHealthCheck against the root filesystem."""
    check = DiskHealthCheck(name="disk-root", path="/", critical_threshold=99.9)
    result = check.check()
    # Most systems are under 99.9% disk usage
    assert result.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)
    assert "percent_used" in result.details


@pytest.mark.unit
def test_health_checker_aggregation_all_healthy():
    """Test HealthChecker aggregates multiple healthy checks."""
    checker = HealthChecker()
    checker.add_check(CommandHealthCheck(name="c1", command=["true"]))
    checker.add_check(CommandHealthCheck(name="c2", command=["true"]))
    aggregated = checker.run_all()

    assert aggregated.overall_status == HealthStatus.HEALTHY
    assert aggregated.healthy_count == 2
    assert aggregated.unhealthy_count == 0


@pytest.mark.unit
def test_health_checker_aggregation_mixed():
    """Test HealthChecker returns DEGRADED when a non-critical check fails."""
    checker = HealthChecker()
    checker.add_check(CommandHealthCheck(name="ok", command=["true"], critical=True))
    checker.add_check(CommandHealthCheck(name="fail", command=["false"], critical=False))
    aggregated = checker.run_all()

    # Non-critical failure => DEGRADED
    assert aggregated.overall_status == HealthStatus.DEGRADED


@pytest.mark.unit
def test_health_checker_aggregation_critical_fail():
    """Test HealthChecker returns UNHEALTHY when a critical check fails."""
    checker = HealthChecker()
    checker.add_check(CommandHealthCheck(name="critical-fail", command=["false"], critical=True))
    aggregated = checker.run_all()
    assert aggregated.overall_status == HealthStatus.UNHEALTHY


@pytest.mark.unit
def test_aggregated_health_to_dict():
    """Test AggregatedHealth serialization."""
    agg = AggregatedHealth(
        overall_status=HealthStatus.HEALTHY,
        checks=[
            HealthCheckResult(name="c1", status=HealthStatus.HEALTHY),
        ],
    )
    d = agg.to_dict()
    assert d["overall_status"] == "healthy"
    assert d["total_checks"] == 1


# ---------------------------------------------------------------------------
# GitOpsSynchronizer
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_gitops_sync_method():
    """Test GitOpsSynchronizer sync sets synced flag."""
    sync = GitOpsSynchronizer(repo_url="https://example.com/repo.git")
    assert sync.is_synced() is False
    result = sync.sync()
    assert result is True
    assert sync.is_synced() is True


@pytest.mark.unit
def test_gitops_version_unknown_before_sync():
    """Test version returns 'unknown' before sync without local_path."""
    sync = GitOpsSynchronizer()
    assert sync.get_version() == "unknown"


@pytest.mark.unit
def test_gitops_version_after_sync():
    """Test version returns v1.0.0 after sync without local_path."""
    sync = GitOpsSynchronizer()
    sync.sync()
    assert sync.get_version() == "v1.0.0"


@pytest.mark.unit
def test_gitops_real_git_repo(tmp_path):
    """Test GitOpsSynchronizer with a real git repo."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo_dir), capture_output=True, check=True,
    )
    (repo_dir / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo_dir), capture_output=True, check=True,
    )

    sync = GitOpsSynchronizer(str(repo_dir), str(repo_dir))
    version = sync.get_version()
    assert version is not None
    assert len(version) >= 7
