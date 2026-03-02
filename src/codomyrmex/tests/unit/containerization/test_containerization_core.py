"""Comprehensive tests for containerization core: dataclasses, specs, config logic.

Tests cover:
- Docker ContainerConfig (docker/__init__.py) to_run_args generation
- Docker ImageInfo and ContainerInfo dataclasses
- Docker DockerManager ContainerConfig (docker_manager.py) get_full_image_name
- Docker DockerManager optimize_container_image (pure logic, no daemon)
- Kubernetes KubernetesDeployment dataclass construction and defaults
- Kubernetes KubernetesService dataclass construction and types
- Containerization exception classes with context metadata
- Module __init__.py availability flags and cli_commands
- BuildGenerator Dockerfile validation edge cases
- BuildStage / MultiStageBuild serialization to Dockerfile
- BuildScript shell script generation with build args
- Port mapping, volume mount, environment variable injection

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
All tests are @pytest.mark.unit and do NOT require Docker to be running.
"""

from datetime import datetime

import pytest

# ---------------------------------------------------------------------------
# Imports from containerization __init__.py
# ---------------------------------------------------------------------------
import codomyrmex.containerization as containerization_pkg

# ---------------------------------------------------------------------------
# Imports from docker/__init__.py (CLI-based ContainerConfig)
# ---------------------------------------------------------------------------
from codomyrmex.containerization.docker import (
    ContainerConfig as DockerCliContainerConfig,
)
from codomyrmex.containerization.docker import (
    ContainerInfo,
    ImageInfo,
)

# ---------------------------------------------------------------------------
# Imports from docker/build_generator.py
# ---------------------------------------------------------------------------
from codomyrmex.containerization.docker.build_generator import (
    BuildGenerator,
    BuildScript,
    BuildStage,
    MultiStageBuild,
)

# ---------------------------------------------------------------------------
# Imports from docker/docker_manager.py (SDK-based ContainerConfig)
# ---------------------------------------------------------------------------
from codomyrmex.containerization.docker.docker_manager import (
    ContainerConfig as DockerSdkContainerConfig,
)

# ---------------------------------------------------------------------------
# Imports from exceptions.py
# ---------------------------------------------------------------------------
from codomyrmex.containerization.exceptions import (
    ContainerError,
    ImageBuildError,
    KubernetesError,
    NetworkError,
    RegistryError,
    VolumeError,
)

# ---------------------------------------------------------------------------
# Imports from kubernetes/kubernetes_orchestrator.py
# ---------------------------------------------------------------------------
from codomyrmex.containerization.kubernetes.kubernetes_orchestrator import (
    KubernetesDeployment,
    KubernetesService,
)

# ===========================================================================
# Docker CLI ContainerConfig (docker/__init__.py)
# ===========================================================================

@pytest.mark.unit
class TestDockerCliContainerConfig:
    """Tests for the CLI-based ContainerConfig dataclass and to_run_args."""

    def test_minimal_config_to_run_args(self):
        """Minimal config produces image name and default restart policy."""
        cfg = DockerCliContainerConfig(image="alpine:3.18")
        args = cfg.to_run_args()
        assert "alpine:3.18" in args
        assert "--restart" in args
        idx = args.index("--restart")
        assert args[idx + 1] == "no"

    def test_named_container(self):
        cfg = DockerCliContainerConfig(image="nginx:latest", name="web-server")
        args = cfg.to_run_args()
        assert "--name" in args
        idx = args.index("--name")
        assert args[idx + 1] == "web-server"

    def test_environment_variables_injected(self):
        cfg = DockerCliContainerConfig(
            image="myapp:v1",
            environment={"DB_HOST": "localhost", "DB_PORT": "5432"},
        )
        args = cfg.to_run_args()
        assert "-e" in args
        env_pairs = [args[i + 1] for i, v in enumerate(args) if v == "-e"]
        assert "DB_HOST=localhost" in env_pairs
        assert "DB_PORT=5432" in env_pairs

    def test_port_mapping(self):
        cfg = DockerCliContainerConfig(
            image="myapp:v1",
            ports={8080: 80, 443: 8443},
        )
        args = cfg.to_run_args()
        port_pairs = [args[i + 1] for i, v in enumerate(args) if v == "-p"]
        assert "80:8080" in port_pairs
        assert "8443:443" in port_pairs

    def test_volume_mounts(self):
        cfg = DockerCliContainerConfig(
            image="myapp:v1",
            volumes={"/host/data": "/container/data", "/host/config": "/etc/app"},
        )
        args = cfg.to_run_args()
        vol_pairs = [args[i + 1] for i, v in enumerate(args) if v == "-v"]
        assert "/host/data:/container/data" in vol_pairs
        assert "/host/config:/etc/app" in vol_pairs

    def test_labels(self):
        cfg = DockerCliContainerConfig(
            image="myapp:v1",
            labels={"maintainer": "team-a", "version": "1.0"},
        )
        args = cfg.to_run_args()
        label_pairs = [args[i + 1] for i, v in enumerate(args) if v == "--label"]
        assert "maintainer=team-a" in label_pairs
        assert "version=1.0" in label_pairs

    def test_network_specification(self):
        cfg = DockerCliContainerConfig(image="myapp:v1", network="my-bridge")
        args = cfg.to_run_args()
        assert "--network" in args
        idx = args.index("--network")
        assert args[idx + 1] == "my-bridge"

    def test_working_dir(self):
        cfg = DockerCliContainerConfig(image="myapp:v1", working_dir="/app")
        args = cfg.to_run_args()
        assert "-w" in args
        idx = args.index("-w")
        assert args[idx + 1] == "/app"

    def test_user_specification(self):
        cfg = DockerCliContainerConfig(image="myapp:v1", user="appuser")
        args = cfg.to_run_args()
        assert "-u" in args
        idx = args.index("-u")
        assert args[idx + 1] == "appuser"

    def test_memory_limit(self):
        cfg = DockerCliContainerConfig(image="myapp:v1", memory_limit="512m")
        args = cfg.to_run_args()
        assert "--memory" in args
        idx = args.index("--memory")
        assert args[idx + 1] == "512m"

    def test_cpu_limit(self):
        cfg = DockerCliContainerConfig(image="myapp:v1", cpu_limit=0.5)
        args = cfg.to_run_args()
        assert "--cpus" in args
        idx = args.index("--cpus")
        assert args[idx + 1] == "0.5"

    def test_restart_policy_always(self):
        cfg = DockerCliContainerConfig(image="myapp:v1", restart_policy="always")
        args = cfg.to_run_args()
        idx = args.index("--restart")
        assert args[idx + 1] == "always"

    def test_entrypoint(self):
        cfg = DockerCliContainerConfig(
            image="myapp:v1", entrypoint=["/bin/sh", "-c"]
        )
        args = cfg.to_run_args()
        assert "--entrypoint" in args
        idx = args.index("--entrypoint")
        assert args[idx + 1] == "/bin/sh"

    def test_command_appended_after_image(self):
        cfg = DockerCliContainerConfig(
            image="python:3.12", command=["python", "-m", "http.server"]
        )
        args = cfg.to_run_args()
        img_idx = args.index("python:3.12")
        # Command args come after the image
        assert args[img_idx + 1:] == ["python", "-m", "http.server"]

    @pytest.mark.parametrize(
        "restart_policy",
        ["no", "always", "unless-stopped", "on-failure"],
    )
    def test_restart_policy_variants(self, restart_policy):
        cfg = DockerCliContainerConfig(
            image="myapp:v1", restart_policy=restart_policy
        )
        args = cfg.to_run_args()
        idx = args.index("--restart")
        assert args[idx + 1] == restart_policy

    def test_full_config_to_run_args(self):
        """A fully populated config should produce a valid args list."""
        cfg = DockerCliContainerConfig(
            image="myapp:v2",
            name="production-app",
            command=["gunicorn", "app:main"],
            entrypoint=["/bin/sh"],
            environment={"ENV": "prod"},
            volumes={"/data": "/app/data"},
            ports={8000: 80},
            labels={"env": "prod"},
            network="prod-net",
            working_dir="/app",
            user="www",
            memory_limit="1g",
            cpu_limit=2.0,
            restart_policy="unless-stopped",
        )
        args = cfg.to_run_args()
        # Verify image is present
        assert "myapp:v2" in args
        # Verify all flags present
        for flag in ["--name", "-e", "-v", "-p", "--label", "--network",
                      "-w", "-u", "--memory", "--cpus", "--restart", "--entrypoint"]:
            assert flag in args


# ===========================================================================
# Docker ImageInfo and ContainerInfo (docker/__init__.py)
# ===========================================================================

@pytest.mark.unit
class TestImageInfo:
    """Tests for the ImageInfo dataclass."""

    def test_full_name_property(self):
        img = ImageInfo(
            id="sha256:abc123",
            repository="myapp",
            tag="v1.0",
            created="2024-01-01",
            size="150MB",
        )
        assert img.full_name == "myapp:v1.0"

    def test_full_name_latest(self):
        img = ImageInfo(
            id="sha256:def456",
            repository="nginx",
            tag="latest",
            created="2024-06-15",
            size="50MB",
        )
        assert img.full_name == "nginx:latest"


@pytest.mark.unit
class TestContainerInfo:
    """Tests for the ContainerInfo dataclass."""

    def test_is_running_true(self):
        ci = ContainerInfo(
            id="abc123",
            name="web",
            image="nginx:latest",
            status="Up 5 minutes",
            ports={"80/tcp": "0.0.0.0:8080"},
            created="2024-01-01",
        )
        assert ci.is_running is True

    def test_is_running_false_when_exited(self):
        ci = ContainerInfo(
            id="abc123",
            name="web",
            image="nginx:latest",
            status="Exited (0) 5 minutes ago",
            ports={},
            created="2024-01-01",
        )
        assert ci.is_running is False

    def test_is_running_false_when_created(self):
        ci = ContainerInfo(
            id="abc123",
            name="web",
            image="nginx:latest",
            status="Created",
            ports={},
            created="2024-01-01",
        )
        assert ci.is_running is False


# ===========================================================================
# Docker SDK ContainerConfig (docker_manager.py)
# ===========================================================================

@pytest.mark.unit
class TestDockerSdkContainerConfig:
    """Tests for the SDK-based ContainerConfig from docker_manager.py."""

    def test_get_full_image_name_with_tag(self):
        cfg = DockerSdkContainerConfig(image_name="myapp", tag="v2.1")
        assert cfg.get_full_image_name() == "myapp:v2.1"

    def test_get_full_image_name_default_tag(self):
        cfg = DockerSdkContainerConfig(image_name="nginx")
        assert cfg.get_full_image_name() == "nginx:latest"

    def test_default_values(self):
        cfg = DockerSdkContainerConfig(image_name="alpine")
        assert cfg.tag == "latest"
        assert cfg.dockerfile_path is None
        assert cfg.build_context == "."
        assert cfg.build_args == {}
        assert cfg.environment == {}
        assert cfg.ports == {}
        assert cfg.volumes == {}
        assert cfg.networks == []
        assert cfg.restart_policy == "no"
        assert cfg.labels == {}

    def test_full_construction(self):
        cfg = DockerSdkContainerConfig(
            image_name="myapp",
            tag="v3",
            dockerfile_path="docker/Dockerfile.prod",
            build_context="./src",
            build_args={"VERSION": "3.0"},
            environment={"ENV": "production"},
            ports={"8080": "80"},
            volumes={"/data": "/app/data"},
            networks=["frontend", "backend"],
            restart_policy="always",
            labels={"team": "platform"},
        )
        assert cfg.get_full_image_name() == "myapp:v3"
        assert cfg.build_args["VERSION"] == "3.0"
        assert len(cfg.networks) == 2

    @pytest.mark.parametrize(
        "image,tag,expected",
        [
            ("nginx", "1.25", "nginx:1.25"),
            ("registry.io/myapp", "sha-abc", "registry.io/myapp:sha-abc"),
            ("localhost:5000/test", "dev", "localhost:5000/test:dev"),
        ],
    )
    def test_full_image_name_parametrized(self, image, tag, expected):
        cfg = DockerSdkContainerConfig(image_name=image, tag=tag)
        assert cfg.get_full_image_name() == expected


# ===========================================================================
# DockerManager.optimize_container_image (pure logic, no daemon needed)
# ===========================================================================

@pytest.mark.unit
class TestDockerManagerOptimizeImage:
    """Tests for optimize_container_image -- pure logic, no Docker daemon."""

    def _get_optimize_fn(self):
        """Import and instantiate DockerManager, extract the optimize method.

        DockerManager.__init__ tries to connect to Docker daemon. If the
        daemon is unavailable, self.client will be None, but the pure
        optimize_container_image method works regardless.
        """
        from codomyrmex.containerization.docker.docker_manager import DockerManager
        manager = DockerManager()
        return manager.optimize_container_image

    def test_python_requirements_returns_slim(self):
        fn = self._get_optimize_fn()
        result = fn("ubuntu:20.04", ["python3", "flask"])
        assert result == "python:3.9-slim"

    def test_node_requirements(self):
        fn = self._get_optimize_fn()
        result = fn("ubuntu:20.04", ["node", "express"])
        assert result == "node:18-slim"

    def test_npm_requirement_returns_node(self):
        fn = self._get_optimize_fn()
        result = fn("ubuntu:20.04", ["npm", "webpack"])
        assert result == "node:18-slim"

    def test_ubuntu_without_compilation_returns_alpine(self):
        fn = self._get_optimize_fn()
        result = fn("ubuntu:20.04", ["curl", "wget"])
        assert result == "alpine:latest"

    def test_python_with_compilation_returns_original(self):
        """If compilation tools are needed, keep the original image."""
        fn = self._get_optimize_fn()
        result = fn("python:3.9", ["python", "gcc", "numpy"])
        # has_python=True but needs_compilation=True => returns original
        assert result == "python:3.9"

    def test_unknown_base_returns_original(self):
        fn = self._get_optimize_fn()
        result = fn("custom-base:latest", ["java", "maven"])
        assert result == "custom-base:latest"

    def test_empty_requirements(self):
        fn = self._get_optimize_fn()
        result = fn("centos:8", [])
        assert result == "centos:8"


# ===========================================================================
# Kubernetes Dataclasses
# ===========================================================================

@pytest.mark.unit
class TestKubernetesDeployment:
    """Tests for KubernetesDeployment dataclass."""

    def test_defaults(self):
        dep = KubernetesDeployment(name="my-app", image="nginx:1.25")
        assert dep.name == "my-app"
        assert dep.image == "nginx:1.25"
        assert dep.namespace == "default"
        assert dep.replicas == 1
        assert dep.port == 80
        assert dep.container_port == 80
        assert dep.environment_variables == {}
        assert dep.volumes == []
        assert dep.volume_mounts == []
        assert dep.config_maps == []
        assert dep.secrets == []
        assert dep.labels == {}
        assert dep.annotations == {}
        assert dep.resources == {}

    def test_full_construction(self):
        dep = KubernetesDeployment(
            name="api-server",
            image="myapp:v2",
            namespace="production",
            replicas=3,
            port=8080,
            container_port=8000,
            environment_variables={"ENV": "prod", "LOG_LEVEL": "info"},
            labels={"app": "api", "tier": "backend"},
            annotations={"prometheus.io/scrape": "true"},
            resources={
                "limits": {"cpu": "500m", "memory": "512Mi"},
                "requests": {"cpu": "250m", "memory": "256Mi"},
            },
        )
        assert dep.replicas == 3
        assert dep.namespace == "production"
        assert dep.resources["limits"]["cpu"] == "500m"
        assert dep.environment_variables["LOG_LEVEL"] == "info"

    def test_created_at_auto_populated(self):
        dep = KubernetesDeployment(name="test", image="nginx")
        assert isinstance(dep.created_at, datetime)

    def test_mutable_defaults_independent(self):
        a = KubernetesDeployment(name="a", image="img")
        b = KubernetesDeployment(name="b", image="img")
        a.environment_variables["KEY"] = "val"
        a.labels["x"] = "y"
        assert b.environment_variables == {}
        assert b.labels == {}


@pytest.mark.unit
class TestKubernetesService:
    """Tests for KubernetesService dataclass."""

    def test_defaults(self):
        svc = KubernetesService(name="my-svc")
        assert svc.name == "my-svc"
        assert svc.namespace == "default"
        assert svc.type == "ClusterIP"
        assert svc.port == 80
        assert svc.target_port == 80
        assert svc.node_port is None
        assert svc.selector == {}
        assert svc.labels == {}

    @pytest.mark.parametrize(
        "svc_type", ["ClusterIP", "NodePort", "LoadBalancer"]
    )
    def test_service_types(self, svc_type):
        svc = KubernetesService(name="svc", type=svc_type)
        assert svc.type == svc_type

    def test_nodeport_construction(self):
        svc = KubernetesService(
            name="nodeport-svc",
            type="NodePort",
            port=80,
            target_port=8080,
            node_port=30080,
            selector={"app": "web"},
        )
        assert svc.node_port == 30080
        assert svc.selector["app"] == "web"

    def test_mutable_defaults_independent(self):
        a = KubernetesService(name="a")
        b = KubernetesService(name="b")
        a.selector["app"] = "a"
        a.labels["env"] = "dev"
        assert b.selector == {}
        assert b.labels == {}


# ===========================================================================
# Containerization Exceptions
# ===========================================================================

@pytest.mark.unit
class TestContainerizationExceptions:
    """Tests for containerization exception classes and their context metadata."""

    def test_container_error_with_context(self):
        err = ContainerError(
            "container failed",
            container_id="abc123",
            container_name="web-server",
        )
        assert "container failed" in str(err)
        assert err.context["container_id"] == "abc123"
        assert err.context["container_name"] == "web-server"

    def test_container_error_minimal(self):
        err = ContainerError("simple error")
        assert "simple error" in str(err)
        assert "container_id" not in err.context

    def test_image_build_error_with_full_context(self):
        err = ImageBuildError(
            "build step failed",
            image_name="myapp",
            image_tag="v1",
            dockerfile_path="/path/to/Dockerfile",
            build_step=5,
        )
        assert err.context["image_name"] == "myapp"
        assert err.context["image_tag"] == "v1"
        assert err.context["dockerfile_path"] == "/path/to/Dockerfile"
        assert err.context["build_step"] == 5

    def test_network_error_context(self):
        err = NetworkError(
            "network unreachable",
            network_name="my-network",
            network_id="net123",
            driver="bridge",
        )
        assert err.context["network_name"] == "my-network"
        assert err.context["driver"] == "bridge"

    def test_volume_error_context(self):
        err = VolumeError(
            "mount failed",
            volume_name="data-vol",
            mount_point="/mnt/data",
            driver="local",
        )
        assert err.context["volume_name"] == "data-vol"
        assert err.context["mount_point"] == "/mnt/data"

    def test_registry_error_context(self):
        err = RegistryError(
            "authentication failed",
            registry_url="https://registry.example.com",
            image_reference="registry.example.com/myapp:v1",
        )
        assert err.context["registry_url"] == "https://registry.example.com"
        assert err.context["image_reference"] == "registry.example.com/myapp:v1"

    def test_kubernetes_error_context(self):
        err = KubernetesError(
            "deployment failed",
            resource_type="Deployment",
            resource_name="my-app",
            namespace="production",
        )
        assert err.context["resource_type"] == "Deployment"
        assert err.context["resource_name"] == "my-app"
        assert err.context["namespace"] == "production"

    def test_all_exceptions_are_base_container_error_subclass(self):
        from codomyrmex.exceptions import ContainerError as BaseContainerError
        for exc_cls in [ContainerError, ImageBuildError, NetworkError,
                        VolumeError, RegistryError, KubernetesError]:
            assert issubclass(exc_cls, BaseContainerError)


# ===========================================================================
# Module __init__.py Flags and CLI Commands
# ===========================================================================

@pytest.mark.unit
class TestContainerizationModuleInit:
    """Tests for containerization package __init__.py exports and flags."""

    def test_has_exceptions_flag(self):
        assert containerization_pkg.HAS_EXCEPTIONS is True

    def test_cli_commands_returns_dict(self):
        cmds = containerization_pkg.cli_commands()
        assert isinstance(cmds, dict)
        assert "images" in cmds
        assert "status" in cmds

    def test_cli_commands_have_help_and_handler(self):
        cmds = containerization_pkg.cli_commands()
        for name, cmd in cmds.items():
            assert "help" in cmd, f"CLI command '{name}' missing 'help'"
            assert "handler" in cmd, f"CLI command '{name}' missing 'handler'"
            assert callable(cmd["handler"])

    def test_version_exists(self):
        assert hasattr(containerization_pkg, "__version__")
        assert isinstance(containerization_pkg.__version__, str)

    def test_all_exports_list(self):
        assert isinstance(containerization_pkg.__all__, list)
        assert "cli_commands" in containerization_pkg.__all__


# ===========================================================================
# BuildGenerator Dockerfile Validation Edge Cases
# ===========================================================================

@pytest.mark.unit
class TestBuildGeneratorDockerfileValidation:
    """Additional edge-case tests for Dockerfile validation logic."""

    def setup_method(self):
        self.generator = BuildGenerator()

    def test_valid_pinned_dockerfile(self):
        content = (
            "FROM python:3.12-slim\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "RUN pip install -r requirements.txt\n"
            "USER appuser\n"
            'CMD ["python", "main.py"]\n'
        )
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert is_valid is True
        assert issues == []

    def test_missing_from_instruction(self):
        content = "RUN echo hello\nCMD ['hello']\n"
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert is_valid is False
        assert any("Missing FROM" in i for i in issues)

    def test_latest_tag_warning(self):
        content = "FROM ubuntu:latest\nUSER appuser\n"
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert any("latest" in i.lower() for i in issues)

    def test_no_tag_treated_as_latest(self):
        content = "FROM ubuntu\nUSER appuser\n"
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert any("latest" in i.lower() for i in issues)

    def test_chmod_777_flagged(self):
        content = "FROM python:3.12\nRUN chmod 777 /app\nUSER user\n"
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert any("permissive" in i.lower() for i in issues)

    def test_password_in_env_flagged(self):
        content = "FROM python:3.12\nENV PASSWORD=secret\nUSER user\n"
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert any("password" in i.lower() for i in issues)

    def test_no_user_instruction_suggestion(self):
        content = "FROM python:3.12-slim\nCOPY . .\n"
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert any("USER" in i for i in issues)

    def test_comments_and_blank_lines_ignored(self):
        content = (
            "# This is a comment\n"
            "\n"
            "FROM python:3.12\n"
            "# Another comment\n"
            "USER appuser\n"
        )
        is_valid, issues = self.generator.validate_dockerfile(content)
        assert is_valid is True

    @pytest.mark.parametrize(
        "dockerfile,expected_issue_substring",
        [
            ("FROM ubuntu:latest\nUSER root\n", "root"),
            ("FROM ubuntu:20.04\nRUN chmod +x /entrypoint.sh\n", "permissive"),
        ],
    )
    def test_security_issues_parametrized(self, dockerfile, expected_issue_substring):
        is_valid, issues = self.generator.validate_dockerfile(dockerfile)
        assert any(expected_issue_substring in i.lower() for i in issues)


# ===========================================================================
# BuildStage Dockerfile Serialization
# ===========================================================================

@pytest.mark.unit
class TestBuildStageSerialization:
    """Tests for BuildStage to_dockerfile output."""

    def test_basic_stage(self):
        stage = BuildStage(name="base", base_image="ubuntu:22.04")
        output = stage.to_dockerfile()
        assert "FROM ubuntu:22.04 AS base" in output

    def test_stage_with_environment(self):
        stage = BuildStage(
            name="build",
            base_image="node:18",
            environment={"NODE_ENV": "production", "CI": "true"},
        )
        output = stage.to_dockerfile()
        assert "ENV NODE_ENV=production" in output
        assert "ENV CI=true" in output

    def test_stage_with_workdir_and_user(self):
        stage = BuildStage(
            name="runtime",
            base_image="alpine:3.18",
            working_directory="/app",
            user="nobody",
        )
        output = stage.to_dockerfile()
        assert "WORKDIR /app" in output
        assert "USER nobody" in output

    def test_stage_with_labels(self):
        stage = BuildStage(
            name="final",
            base_image="scratch",
            labels={"version": "1.0", "maintainer": "ops"},
        )
        output = stage.to_dockerfile()
        assert "LABEL version=1.0" in output
        assert "LABEL maintainer=ops" in output


# ===========================================================================
# MultiStageBuild Dockerfile Serialization
# ===========================================================================

@pytest.mark.unit
class TestMultiStageBuildSerialization:
    """Tests for MultiStageBuild to_dockerfile."""

    def test_two_stage_build(self):
        build = MultiStageBuild(
            stages=[
                BuildStage(name="builder", base_image="golang:1.21"),
                BuildStage(name="runtime", base_image="alpine:3.18"),
            ],
            final_stage="runtime",
            metadata={"project_name": "myservice"},
        )
        dockerfile = build.to_dockerfile()
        assert "FROM golang:1.21 AS builder" in dockerfile
        assert "FROM alpine:3.18 AS runtime" in dockerfile
        assert "myservice" in dockerfile

    def test_single_stage_build(self):
        build = MultiStageBuild(
            stages=[BuildStage(name="app", base_image="python:3.12")],
            final_stage="app",
        )
        dockerfile = build.to_dockerfile()
        assert "FROM python:3.12 AS app" in dockerfile


# ===========================================================================
# BuildScript Shell Script Generation
# ===========================================================================

@pytest.mark.unit
class TestBuildScriptGeneration:
    """Tests for BuildScript to_shell_script output."""

    def test_basic_script(self):
        script = BuildScript(
            name="api",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["api:v1"],
        )
        shell = script.to_shell_script()
        assert "#!/bin/bash" in shell
        assert "docker build" in shell
        assert "-t api:v1" in shell

    def test_script_with_build_args(self):
        script = BuildScript(
            name="api",
            dockerfile_path="Dockerfile.prod",
            context_path="./src",
            build_args={"VERSION": "2.0", "GIT_SHA": "abc123"},
            tags=["api:2.0"],
        )
        shell = script.to_shell_script()
        assert "--build-arg VERSION=2.0" in shell
        assert "--build-arg GIT_SHA=abc123" in shell
        assert "-f Dockerfile.prod" in shell

    def test_script_with_push_targets(self):
        script = BuildScript(
            name="web",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["web:latest"],
            push_targets=["registry.io/web:latest", "ghcr.io/org/web:latest"],
        )
        shell = script.to_shell_script()
        assert "docker push registry.io/web:latest" in shell
        assert "docker push ghcr.io/org/web:latest" in shell

    def test_multiple_tags(self):
        script = BuildScript(
            name="app",
            dockerfile_path="Dockerfile",
            context_path=".",
            tags=["app:v1", "app:latest"],
        )
        shell = script.to_shell_script()
        assert "-t app:v1" in shell
        assert "-t app:latest" in shell


# ===========================================================================
# BuildGenerator Multi-Stage Build Templates
# ===========================================================================

@pytest.mark.unit
class TestBuildGeneratorTemplates:
    """Tests for BuildGenerator multi-stage build template creation."""

    def setup_method(self):
        self.generator = BuildGenerator()

    def test_templates_loaded(self):
        assert isinstance(self.generator.templates, dict)
        assert "python_basic" in self.generator.templates
        assert "node_basic" in self.generator.templates
        assert "security_hardened" in self.generator.templates

    @pytest.mark.parametrize(
        "build_type,expected_base_substring",
        [
            ("python", "python"),
            ("node", "node"),
            ("java", "openjdk"),
            ("go", "golang"),
        ],
    )
    def test_multi_stage_build_types(self, build_type, expected_base_substring):
        build = self.generator.create_multi_stage_build(
            {"build_type": build_type}
        )
        assert isinstance(build, MultiStageBuild)
        assert len(build.stages) >= 2
        assert build.final_stage == "runtime"
        # The builder stage should reference the expected base
        builder_dockerfile = build.stages[0].to_dockerfile()
        assert expected_base_substring in builder_dockerfile.lower()

    def test_generic_build_type(self):
        build = self.generator.create_multi_stage_build(
            {"build_type": "unknown-type"}
        )
        assert isinstance(build, MultiStageBuild)
        assert len(build.stages) >= 1


# ===========================================================================
# Dockerfile Optimization (file-based)
# ===========================================================================

@pytest.mark.unit
class TestDockerfileOptimization:
    """Tests for BuildGenerator.optimize_dockerfile."""

    def setup_method(self):
        self.generator = BuildGenerator()

    def test_combines_consecutive_run_commands(self, tmp_path):
        content = "FROM ubuntu:22.04\nRUN apt-get update\nRUN apt-get install -y curl\nRUN echo done\n"
        path = tmp_path / "Dockerfile"
        path.write_text(content)
        optimized = self.generator.optimize_dockerfile(str(path))
        # Consecutive RUN commands should be combined
        assert "&&" in optimized

    def test_adds_cache_cleanup_to_apt(self, tmp_path):
        content = "FROM ubuntu:22.04\nRUN apt-get install -y python3\n"
        path = tmp_path / "Dockerfile"
        path.write_text(content)
        optimized = self.generator.optimize_dockerfile(str(path))
        assert "rm -rf /var/lib/apt/lists/*" in optimized

    def test_adds_no_cache_dir_to_pip(self, tmp_path):
        content = "FROM python:3.12\nRUN pip install flask\n"
        path = tmp_path / "Dockerfile"
        path.write_text(content)
        optimized = self.generator.optimize_dockerfile(str(path))
        assert "--no-cache-dir" in optimized

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            self.generator.optimize_dockerfile(str(tmp_path / "nonexistent"))
