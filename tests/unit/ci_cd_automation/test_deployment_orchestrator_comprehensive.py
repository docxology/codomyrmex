"""Comprehensive unit tests for DeploymentOrchestrator."""

import pytest
import yaml

from codomyrmex.ci_cd_automation.deployment_orchestrator import (
    DeploymentOrchestrator,
    DeploymentStatus,
    EnvironmentType,
)


@pytest.mark.unit
class TestDeploymentOrchestrator:
    @pytest.fixture
    def config_file(self, tmp_path):
        config = {
            "environments": [
                {
                    "name": "staging",
                    "type": "staging",
                    "host": "localhost",
                    "port": 8022,
                    "variables": {"deploy_path": "/tmp/staging"},
                    "health_checks": [{"type": "tcp", "endpoint": "localhost:8000"}],
                }
            ]
        }
        config_path = tmp_path / "deploy_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        return str(config_path)

    def test_init_and_load_config(self, config_file):
        orchestrator = DeploymentOrchestrator(config_file)
        assert "staging" in orchestrator.environments
        env = orchestrator.environments["staging"]
        assert env.type == EnvironmentType.STAGING
        assert env.host == "localhost"

    def test_create_deployment(self, config_file):
        orchestrator = DeploymentOrchestrator(config_file)
        deployment = orchestrator.create_deployment(
            name="test-deploy",
            version="1.1.0",
            environment_name="staging",
            artifacts=["app.zip"],
        )
        assert deployment.name == "test-deploy"
        assert deployment.version == "1.1.0"
        assert deployment.status == DeploymentStatus.PENDING

    def test_create_deployment_invalid_env(self, config_file):
        orchestrator = DeploymentOrchestrator(config_file)
        with pytest.raises(ValueError, match="not found"):
            orchestrator.create_deployment("n", "v", "invalid", [])

    def test_deploy_failure_hooks(self, config_file, tmp_path):
        """Test deployment with a failing pre-deploy hook."""
        orchestrator = DeploymentOrchestrator(config_file)
        env = orchestrator.environments["staging"]
        env.pre_deploy_hooks = ["exit 1"]

        deployment = orchestrator.create_deployment("fail-hook", "1.0", "staging", [])
        # We don't rollback if it's not a real failure during deployment itself
        # But wait, in our implementation if hooks fail, we log warning and continue.
        # Let's see how it behaves.
        orchestrator.deploy("fail-hook")
        assert any("Hook failed" in log for log in deployment.logs)

    def test_health_check_fail(self, config_file):
        """Test that a failing health check marks deployment as failed/rolled back."""
        orchestrator = DeploymentOrchestrator(config_file)
        # tcp health check to localhost:8000 should fail if nothing is listening
        deployment = orchestrator.create_deployment(
            "hc-fail", "1.0", "staging", [], rollback_on_failure=True
        )
        # Actually it's better to ensure port is closed
        # We can't easily do it but usually it's closed in this environment
        orchestrator.deploy("hc-fail")

        # If health check fails, it should be ROLLED_BACK (since rollback_on_failure=True)
        # Or FAILURE if rollback fails.
        assert deployment.status in (
            DeploymentStatus.ROLLED_BACK,
            DeploymentStatus.FAILURE,
        )

    def test_cancel_deployment(self, config_file):
        orchestrator = DeploymentOrchestrator(config_file)
        deployment = orchestrator.create_deployment("can", "v", "staging", [])
        deployment.status = DeploymentStatus.RUNNING
        assert orchestrator.cancel_deployment("can") is True
        assert deployment.status == DeploymentStatus.CANCELLED

    def test_list_deployments(self, config_file):
        orchestrator = DeploymentOrchestrator(config_file)
        orchestrator.create_deployment("d1", "v", "staging", [])
        orchestrator.create_deployment("d2", "v", "staging", [])
        assert len(orchestrator.list_deployments()) == 2
