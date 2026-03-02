"""Comprehensive unit tests for ci_cd_automation.deployment_orchestrator.

Tests cover: DeploymentStatus enum, EnvironmentType enum, Environment dataclass,
Deployment dataclass, DeploymentOrchestrator constructor, config loading from
JSON/YAML, create_deployment, deploy lifecycle, rollback logic, health checks,
cancel_deployment, list_deployments, get_deployment_status, hooks execution,
and the manage_deployments convenience function.

Zero-mock policy: all tests use real objects and tmp_path for filesystem.
"""

import json
import os
from datetime import UTC, datetime

import pytest
import yaml

from codomyrmex.ci_cd_automation.deployment_orchestrator import (
    Deployment,
    DeploymentOrchestrator,
    DeploymentStatus,
    Environment,
    EnvironmentType,
    manage_deployments,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_env(
    name: str = "dev",
    env_type: EnvironmentType = EnvironmentType.DEVELOPMENT,
    host: str = "localhost",
    **kwargs,
) -> Environment:
    """Build a minimal Environment for testing."""
    return Environment(name=name, type=env_type, host=host, **kwargs)


def _write_json_config(path, environments=None):
    """Write a JSON deployment config to *path*."""
    config = {"environments": environments or []}
    with open(path, "w") as f:
        json.dump(config, f)


def _write_yaml_config(path, environments=None):
    """Write a YAML deployment config to *path*."""
    config = {"environments": environments or []}
    with open(path, "w") as f:
        yaml.dump(config, f)


def _env_dict(
    name="dev",
    env_type="development",
    host="localhost",
    port=22,
    **extra,
) -> dict:
    """Return an environment dict suitable for config files."""
    d = {"name": name, "type": env_type, "host": host, "port": port}
    d.update(extra)
    return d


def _orchestrator_with_env(
    tmp_path, env_name="staging", env_type="staging", host="stage.example.com"
):
    """Create an orchestrator whose config contains one environment."""
    config_path = str(tmp_path / "deploy.json")
    _write_json_config(config_path, [_env_dict(env_name, env_type, host)])
    return DeploymentOrchestrator(config_path=config_path)


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDeploymentStatusEnum:
    """Verify DeploymentStatus enum members and values."""

    def test_all_members_present(self):
        expected = {"PENDING", "RUNNING", "SUCCESS", "FAILURE", "ROLLED_BACK", "CANCELLED"}
        assert set(DeploymentStatus.__members__.keys()) == expected

    def test_values_are_lowercase_strings(self):
        for member in DeploymentStatus:
            assert member.value == member.name.lower()


@pytest.mark.unit
class TestEnvironmentTypeEnum:
    """Verify EnvironmentType enum members and values."""

    def test_all_members_present(self):
        expected = {"DEVELOPMENT", "STAGING", "PRODUCTION", "TESTING"}
        assert set(EnvironmentType.__members__.keys()) == expected

    def test_values_are_lowercase(self):
        for member in EnvironmentType:
            assert member.value == member.name.lower()


# ---------------------------------------------------------------------------
# Environment dataclass tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEnvironmentDataclass:
    """Tests for the Environment dataclass."""

    def test_minimal_construction(self):
        env = _make_env()
        assert env.name == "dev"
        assert env.type == EnvironmentType.DEVELOPMENT
        assert env.host == "localhost"
        assert env.port == 22
        assert env.user == "deploy"
        assert env.key_path is None
        assert env.docker_registry is None
        assert env.kubernetes_context is None
        assert env.variables == {}
        assert env.pre_deploy_hooks == []
        assert env.post_deploy_hooks == []
        assert env.health_checks == []

    def test_full_construction(self):
        env = Environment(
            name="prod",
            type=EnvironmentType.PRODUCTION,
            host="prod.example.com",
            port=2222,
            user="admin",
            key_path="/keys/prod.pem",
            docker_registry="registry.example.com",
            kubernetes_context="prod-cluster",
            variables={"APP_ENV": "production"},
            pre_deploy_hooks=["echo pre"],
            post_deploy_hooks=["echo post"],
            health_checks=[{"type": "http", "endpoint": "http://prod/health"}],
        )
        assert env.port == 2222
        assert env.user == "admin"
        assert env.variables["APP_ENV"] == "production"

    def test_to_dict_round_trip(self):
        env = _make_env(variables={"KEY": "val"})
        d = env.to_dict()
        assert d["name"] == "dev"
        assert d["type"] == "development"
        assert d["host"] == "localhost"
        assert d["port"] == 22
        assert d["variables"] == {"KEY": "val"}

    def test_to_dict_contains_all_fields(self):
        env = _make_env()
        d = env.to_dict()
        expected_keys = {
            "name", "type", "host", "port", "user", "key_path",
            "docker_registry", "kubernetes_context", "variables",
            "pre_deploy_hooks", "post_deploy_hooks", "health_checks",
        }
        assert set(d.keys()) == expected_keys


# ---------------------------------------------------------------------------
# Deployment dataclass tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDeploymentDataclass:
    """Tests for the Deployment dataclass."""

    def test_minimal_construction(self):
        env = _make_env()
        dep = Deployment(name="app", version="1.0.0", environment=env, artifacts=["app.tar.gz"])
        assert dep.name == "app"
        assert dep.version == "1.0.0"
        assert dep.strategy == "rolling"
        assert dep.timeout == 1800
        assert dep.rollback_on_failure is True
        assert dep.status == DeploymentStatus.PENDING
        assert isinstance(dep.created_at, datetime)
        assert dep.started_at is None
        assert dep.finished_at is None
        assert dep.duration == 0.0
        assert dep.logs == []
        assert dep.metrics == {}

    def test_post_init_sets_created_at(self):
        env = _make_env()
        before = datetime.now(UTC)
        dep = Deployment(name="a", version="1", environment=env, artifacts=[])
        after = datetime.now(UTC)
        assert before <= dep.created_at <= after

    def test_explicit_created_at_preserved(self):
        env = _make_env()
        ts = datetime(2025, 1, 1, tzinfo=UTC)
        dep = Deployment(name="a", version="1", environment=env, artifacts=[], created_at=ts)
        assert dep.created_at == ts

    def test_to_dict_contains_all_fields(self):
        env = _make_env()
        dep = Deployment(name="app", version="2.0", environment=env, artifacts=["x"])
        d = dep.to_dict()
        expected_keys = {
            "name", "version", "environment", "artifacts", "strategy",
            "timeout", "rollback_on_failure", "status", "created_at",
            "started_at", "finished_at", "duration", "logs", "metrics",
        }
        assert set(d.keys()) == expected_keys

    def test_to_dict_status_is_string(self):
        env = _make_env()
        dep = Deployment(name="a", version="1", environment=env, artifacts=[])
        d = dep.to_dict()
        assert d["status"] == "pending"

    def test_to_dict_environment_nested(self):
        env = _make_env(name="staging", env_type=EnvironmentType.STAGING)
        dep = Deployment(name="a", version="1", environment=env, artifacts=[])
        d = dep.to_dict()
        assert d["environment"]["name"] == "staging"
        assert d["environment"]["type"] == "staging"

    def test_to_dict_timestamps_iso(self):
        env = _make_env()
        ts = datetime(2025, 6, 15, 12, 0, 0, tzinfo=UTC)
        dep = Deployment(
            name="a", version="1", environment=env, artifacts=[],
            created_at=ts, started_at=ts,
        )
        d = dep.to_dict()
        assert "2025-06-15" in d["created_at"]
        assert "2025-06-15" in d["started_at"]
        assert d["finished_at"] is None


# ---------------------------------------------------------------------------
# DeploymentOrchestrator constructor / config loading tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestOrchestratorInit:
    """Test DeploymentOrchestrator initialization and config loading."""

    def test_default_config_path(self, tmp_path):
        """When no config exists, orchestrator initializes with empty state."""
        config = str(tmp_path / "nonexistent.json")
        orch = DeploymentOrchestrator(config_path=config)
        assert orch.config_path == config
        assert orch.environments == {}
        assert orch.deployments == {}

    def test_load_json_config(self, tmp_path):
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict("dev", "development", "dev.local")]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        assert "dev" in orch.environments
        assert orch.environments["dev"].host == "dev.local"
        assert orch.environments["dev"].type == EnvironmentType.DEVELOPMENT

    def test_load_yaml_config(self, tmp_path):
        config_path = str(tmp_path / "deploy.yaml")
        envs = [_env_dict("staging", "staging", "stage.local")]
        _write_yaml_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        assert "staging" in orch.environments
        assert orch.environments["staging"].type == EnvironmentType.STAGING

    def test_load_yml_extension(self, tmp_path):
        config_path = str(tmp_path / "deploy.yml")
        envs = [_env_dict("prod", "production", "prod.local")]
        _write_yaml_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        assert "prod" in orch.environments

    def test_load_config_with_all_env_fields(self, tmp_path):
        config_path = str(tmp_path / "full.json")
        envs = [
            _env_dict(
                "prod", "production", "prod.example.com",
                port=2222,
                user="admin",
                key_path="/keys/id_rsa",
                docker_registry="registry.io",
                kubernetes_context="prod-ctx",
                variables={"APP_ENV": "production"},
                pre_deploy_hooks=["echo pre"],
                post_deploy_hooks=["echo post"],
                health_checks=[{"type": "http", "endpoint": "http://localhost/health"}],
            )
        ]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        env = orch.environments["prod"]
        assert env.port == 2222
        assert env.user == "admin"
        assert env.key_path == "/keys/id_rsa"
        assert env.docker_registry == "registry.io"
        assert env.kubernetes_context == "prod-ctx"
        assert env.variables == {"APP_ENV": "production"}
        assert env.pre_deploy_hooks == ["echo pre"]
        assert env.post_deploy_hooks == ["echo post"]
        assert len(env.health_checks) == 1

    def test_load_multiple_environments(self, tmp_path):
        config_path = str(tmp_path / "multi.json")
        envs = [
            _env_dict("dev", "development", "dev.local"),
            _env_dict("staging", "staging", "stage.local"),
            _env_dict("prod", "production", "prod.local"),
        ]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        assert len(orch.environments) == 3

    def test_corrupt_config_does_not_crash(self, tmp_path):
        config_path = str(tmp_path / "bad.json")
        with open(config_path, "w") as f:
            f.write("NOT VALID JSON {{{")
        # Should not raise -- logs a warning instead
        orch = DeploymentOrchestrator(config_path=config_path)
        assert orch.environments == {}

    def test_empty_environments_list(self, tmp_path):
        config_path = str(tmp_path / "empty.json")
        _write_json_config(config_path, [])
        orch = DeploymentOrchestrator(config_path=config_path)
        assert orch.environments == {}


# ---------------------------------------------------------------------------
# create_deployment tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCreateDeployment:
    """Test DeploymentOrchestrator.create_deployment."""

    def test_create_basic_deployment(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0.0", "staging", ["app.tar.gz"])
        assert dep.name == "app"
        assert dep.version == "1.0.0"
        assert dep.environment.name == "staging"
        assert dep.artifacts == ["app.tar.gz"]
        assert dep.status == DeploymentStatus.PENDING

    def test_create_deployment_stored(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0.0", "staging", ["app.tar.gz"])
        assert "app" in orch.deployments

    def test_create_deployment_with_strategy(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [], strategy="blue_green")
        assert dep.strategy == "blue_green"

    def test_create_deployment_with_timeout(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [], timeout=60)
        assert dep.timeout == 60

    def test_create_deployment_rollback_flag(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [], rollback_on_failure=False)
        assert dep.rollback_on_failure is False

    def test_create_deployment_unknown_env_raises(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        with pytest.raises(ValueError, match="Environment 'missing' not found"):
            orch.create_deployment("app", "1.0", "missing", [])

    def test_create_multiple_deployments(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app1", "1.0", "staging", ["a.tar.gz"])
        orch.create_deployment("app2", "2.0", "staging", ["b.tar.gz"])
        assert len(orch.deployments) == 2
        assert "app1" in orch.deployments
        assert "app2" in orch.deployments

    def test_create_deployment_overwrites_same_name(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0", "staging", ["a.tar.gz"])
        orch.create_deployment("app", "2.0", "staging", ["b.tar.gz"])
        assert orch.deployments["app"].version == "2.0"


# ---------------------------------------------------------------------------
# get_deployment_status / list / cancel
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDeploymentQueries:
    """Test status queries, listing, and cancellation."""

    def test_get_status_found(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0", "staging", [])
        result = orch.get_deployment_status("app")
        assert result is not None
        assert result.name == "app"

    def test_get_status_not_found(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        assert orch.get_deployment_status("nope") is None

    def test_list_deployments_empty(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        assert orch.list_deployments() == []

    def test_list_deployments_populated(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("a", "1", "staging", [])
        orch.create_deployment("b", "2", "staging", [])
        result = orch.list_deployments()
        assert len(result) == 2
        names = {d.name for d in result}
        assert names == {"a", "b"}

    def test_cancel_running_deployment(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        dep.status = DeploymentStatus.RUNNING
        assert orch.cancel_deployment("app") is True
        assert dep.status == DeploymentStatus.CANCELLED

    def test_cancel_pending_deployment_fails(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0", "staging", [])
        assert orch.cancel_deployment("app") is False

    def test_cancel_nonexistent_deployment(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        assert orch.cancel_deployment("ghost") is False

    def test_cancel_already_finished(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        dep.status = DeploymentStatus.SUCCESS
        assert orch.cancel_deployment("app") is False


# ---------------------------------------------------------------------------
# deploy lifecycle tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDeployLifecycle:
    """Test the deploy() method and its lifecycle transitions."""

    def test_deploy_unknown_name_raises(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        with pytest.raises(ValueError, match="Deployment 'missing' not found"):
            orch.deploy("missing")

    def test_deploy_sets_started_at(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0", "staging", [])
        before = datetime.now(UTC)
        result = orch.deploy("app")
        assert result.started_at is not None
        assert result.started_at >= before

    def test_deploy_sets_finished_at(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0", "staging", [])
        result = orch.deploy("app")
        assert result.finished_at is not None

    def test_deploy_computes_duration(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0", "staging", [])
        result = orch.deploy("app")
        assert result.duration >= 0.0

    def test_deploy_no_health_checks_succeeds(self, tmp_path):
        """With no health checks, deployment should succeed."""
        orch = _orchestrator_with_env(tmp_path)
        orch.create_deployment("app", "1.0", "staging", [])
        result = orch.deploy("app")
        assert result.status == DeploymentStatus.SUCCESS

    def test_deploy_resets_logs(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        dep.logs = ["old log entry"]
        orch.deploy("app")
        # Logs should have been reset at start (old entry gone)
        assert "old log entry" not in dep.logs


# ---------------------------------------------------------------------------
# Health check tests (unit-level, no real network)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHealthChecks:
    """Test _perform_health_checks and underlying check methods."""

    def test_no_health_checks_returns_true(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        assert orch._perform_health_checks(dep) is True

    def test_http_health_check_unreachable(self, tmp_path):
        """HTTP check against a guaranteed-bad endpoint returns False."""
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            health_checks=[{"type": "http", "endpoint": "http://127.0.0.1:1/nope", "timeout": 1}],
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        result = orch._perform_health_checks(dep)
        assert result is False
        assert any("Health check failed" in log for log in dep.logs)

    def test_tcp_health_check_unreachable(self, tmp_path):
        """TCP check against a guaranteed-bad endpoint returns False."""
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            health_checks=[{"type": "tcp", "endpoint": "127.0.0.1:1", "timeout": 1}],
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        result = orch._perform_health_checks(dep)
        assert result is False

    def test_unknown_health_check_type(self, tmp_path):
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            health_checks=[{"type": "grpc", "endpoint": "localhost:50051"}],
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        result = orch._perform_health_checks(dep)
        assert result is False

    def test_check_http_health_bad_url(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        result = orch._check_http_health("http://127.0.0.1:1/nonexistent", timeout=1)
        assert result is False

    def test_check_tcp_health_bad_port(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        result = orch._check_tcp_health("127.0.0.1:1", timeout=1)
        assert result is False

    def test_check_tcp_health_invalid_format(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        # Missing colon separator should cause ValueError -> False
        result = orch._check_tcp_health("nocolon", timeout=1)
        assert result is False


# ---------------------------------------------------------------------------
# Rollback logic tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRollback:
    """Test rollback paths in deploy()."""

    def test_deploy_with_failed_health_check_rollback(self, tmp_path):
        """When health checks fail and rollback_on_failure=True, status is ROLLED_BACK."""
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            health_checks=[{"type": "http", "endpoint": "http://127.0.0.1:1/down", "timeout": 1}],
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        orch.create_deployment("app", "1.0", "staging", [], rollback_on_failure=True)
        result = orch.deploy("app")
        assert result.status == DeploymentStatus.ROLLED_BACK

    def test_deploy_with_failed_health_check_no_rollback(self, tmp_path):
        """When health checks fail and rollback_on_failure=False, status is FAILURE."""
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            health_checks=[{"type": "http", "endpoint": "http://127.0.0.1:1/down", "timeout": 1}],
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        orch.create_deployment("app", "1.0", "staging", [], rollback_on_failure=False)
        result = orch.deploy("app")
        assert result.status == DeploymentStatus.FAILURE

    def test_rollback_rolling_no_docker(self, tmp_path):
        """Rolling rollback with no docker client is a no-op (no crash)."""
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        dep.strategy = "rolling"
        # Should not raise
        orch._rollback_deployment(dep)

    def test_rollback_blue_green_no_k8s(self, tmp_path):
        """Blue-green rollback with no k8s client is a no-op (no crash)."""
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        dep.strategy = "blue_green"
        orch._rollback_deployment(dep)

    def test_rollback_unknown_strategy(self, tmp_path):
        """Unknown rollback strategy logs a warning but does not crash."""
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        dep.strategy = "canary"
        orch._rollback_deployment(dep)


# ---------------------------------------------------------------------------
# Hooks execution tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHooksExecution:
    """Test _execute_hooks."""

    def test_pre_deploy_hook_executed(self, tmp_path):
        marker = str(tmp_path / "pre_marker.txt")
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            pre_deploy_hooks=[f"touch {marker}"],
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        orch._execute_hooks(dep, "pre_deploy")
        assert os.path.exists(marker)

    def test_post_deploy_hook_executed(self, tmp_path):
        marker = str(tmp_path / "post_marker.txt")
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            post_deploy_hooks=[f"touch {marker}"],
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        orch._execute_hooks(dep, "post_deploy")
        assert os.path.exists(marker)

    def test_hook_failure_does_not_crash(self, tmp_path):
        config_path = str(tmp_path / "deploy.json")
        envs = [_env_dict(
            "staging", "staging", "stage.local",
            pre_deploy_hooks=["false"],  # 'false' command exits 1
        )]
        _write_json_config(config_path, envs)
        orch = DeploymentOrchestrator(config_path=config_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        # Should not raise
        orch._execute_hooks(dep, "pre_deploy")

    def test_hook_unknown_type_runs_nothing(self, tmp_path):
        orch = _orchestrator_with_env(tmp_path)
        dep = orch.create_deployment("app", "1.0", "staging", [])
        # unknown hook type should do nothing
        orch._execute_hooks(dep, "unknown_phase")


# ---------------------------------------------------------------------------
# manage_deployments convenience function
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestManageDeployments:
    """Test the manage_deployments convenience function."""

    def test_returns_orchestrator(self, tmp_path):
        config = str(tmp_path / "nonexistent.json")
        orch = manage_deployments(config)
        assert isinstance(orch, DeploymentOrchestrator)

    def test_none_config_uses_default(self):
        orch = manage_deployments(None)
        assert isinstance(orch, DeploymentOrchestrator)
        assert orch.config_path.endswith("deployment_config.yaml")
