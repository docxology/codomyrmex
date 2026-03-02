"""Unit tests for codomyrmex.containerization.registry.container_registry.

Tests cover:
- ContainerImage dataclass construction and defaults
- RegistryCredentials dataclass and get_auth_header logic
- ContainerRegistry initialization, URL normalization, and pure-logic methods
- Simulated (no-Docker) paths for push/pull/build_and_push/list/delete/info/tag
- manage_container_registry dispatcher for all operations
- Edge cases: unknown operations, empty registry URLs, Docker Hub aliases

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
Docker-daemon-dependent tests guarded with @pytest.mark.skipif(not HAS_DOCKER).
"""

import base64
import importlib.util
import subprocess
from datetime import datetime

import pytest

# --- Skip guards -----------------------------------------------------------

_docker_spec = importlib.util.find_spec("docker")
HAS_DOCKER_SDK = _docker_spec is not None

_requests_spec = importlib.util.find_spec("requests")
HAS_REQUESTS = _requests_spec is not None

# Check for a running Docker daemon (needed for live-Docker tests only)
try:
    _docker_info = subprocess.run(
        ["docker", "info"], capture_output=True, timeout=10
    )
    HAS_DOCKER_DAEMON = _docker_info.returncode == 0
except Exception:
    HAS_DOCKER_DAEMON = False

# --- Imports ----------------------------------------------------------------

from codomyrmex.containerization.registry.container_registry import (
    ContainerImage,
    ContainerRegistry,
    RegistryCredentials,
    manage_container_registry,
)
from codomyrmex.exceptions import CodomyrmexError

# ---------------------------------------------------------------------------
# ContainerImage dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestContainerImage:
    """Tests for the ContainerImage dataclass."""

    def test_basic_construction(self):
        now = datetime.now()
        img = ContainerImage(
            name="myapp",
            tag="v1.0",
            registry_url="docker.io",
            size_mb=123.4,
            created_at=now,
        )
        assert img.name == "myapp"
        assert img.tag == "v1.0"
        assert img.registry_url == "docker.io"
        assert img.size_mb == 123.4
        assert img.created_at == now
        assert img.digest is None
        assert img.layers == []
        assert img.labels == {}
        assert img.vulnerabilities == []

    def test_construction_with_all_fields(self):
        now = datetime.now()
        img = ContainerImage(
            name="backend",
            tag="latest",
            registry_url="gcr.io/my-project",
            size_mb=456.7,
            created_at=now,
            digest="sha256:abc123",
            layers=["layer1", "layer2"],
            labels={"maintainer": "dev"},
            vulnerabilities=[{"id": "CVE-2024-1234", "severity": "HIGH"}],
        )
        assert img.digest == "sha256:abc123"
        assert len(img.layers) == 2
        assert img.labels["maintainer"] == "dev"
        assert img.vulnerabilities[0]["severity"] == "HIGH"

    def test_default_mutable_fields_are_independent(self):
        """Each instance must have its own mutable defaults."""
        a = ContainerImage(
            name="a", tag="t", registry_url="r", size_mb=0, created_at=datetime.now()
        )
        b = ContainerImage(
            name="b", tag="t", registry_url="r", size_mb=0, created_at=datetime.now()
        )
        a.layers.append("x")
        a.labels["k"] = "v"
        a.vulnerabilities.append({"id": "1"})
        assert b.layers == []
        assert b.labels == {}
        assert b.vulnerabilities == []


# ---------------------------------------------------------------------------
# RegistryCredentials dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRegistryCredentials:
    """Tests for RegistryCredentials and its auth header logic."""

    def test_basic_construction(self):
        creds = RegistryCredentials(
            username="user",
            password="pass",
            registry_url="docker.io",
        )
        assert creds.username == "user"
        assert creds.password == "pass"
        assert creds.registry_url == "docker.io"
        assert creds.token is None

    def test_get_auth_header_basic(self):
        creds = RegistryCredentials(
            username="alice",
            password="s3cret",
            registry_url="gcr.io",
        )
        header = creds.get_auth_header()
        expected_encoded = base64.b64encode(b"alice:s3cret").decode()
        assert header == f"Basic {expected_encoded}"

    def test_get_auth_header_with_token(self):
        creds = RegistryCredentials(
            username="alice",
            password="s3cret",
            registry_url="gcr.io",
            token="my-jwt-token",
        )
        header = creds.get_auth_header()
        assert header == "Bearer my-jwt-token"

    def test_basic_auth_special_characters(self):
        """Username/password with special characters should encode correctly."""
        creds = RegistryCredentials(
            username="user@domain.com",
            password="p@ss:w0rd!",
            registry_url="registry.example.com",
        )
        header = creds.get_auth_header()
        decoded = base64.b64decode(header.split(" ")[1]).decode()
        assert decoded == "user@domain.com:p@ss:w0rd!"

    def test_token_takes_precedence(self):
        """When token is set, Bearer auth is returned regardless of user/pass."""
        creds = RegistryCredentials(
            username="u", password="p", registry_url="r", token="tok"
        )
        assert creds.get_auth_header().startswith("Bearer ")


# ---------------------------------------------------------------------------
# ContainerRegistry -- initialisation and pure-logic helpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestContainerRegistryInit:
    """Tests for ContainerRegistry construction and URL normalisation."""

    def test_trailing_slash_stripped(self):
        reg = ContainerRegistry(registry_url="myregistry.io/")
        assert reg.registry_url == "myregistry.io"

    def test_multiple_trailing_slashes_stripped(self):
        reg = ContainerRegistry(registry_url="myregistry.io///")
        # rstrip('/') removes all trailing slashes
        assert not reg.registry_url.endswith("/")

    def test_credentials_stored(self):
        creds = RegistryCredentials(
            username="u", password="p", registry_url="r"
        )
        reg = ContainerRegistry(registry_url="r", credentials=creds)
        assert reg.credentials is creds

    def test_no_credentials(self):
        reg = ContainerRegistry(registry_url="r")
        assert reg.credentials is None


@pytest.mark.unit
class TestGetFullImageName:
    """Tests for _get_full_image_name helper."""

    def test_docker_hub_shorthand(self):
        reg = ContainerRegistry(registry_url="docker.io")
        assert reg._get_full_image_name("myapp", "v1") == "myapp:v1"

    def test_docker_hub_registry_hub(self):
        reg = ContainerRegistry(registry_url="registry.hub.docker.com")
        assert reg._get_full_image_name("myapp", "v1") == "myapp:v1"

    def test_empty_registry_url(self):
        reg = ContainerRegistry(registry_url="")
        assert reg._get_full_image_name("myapp", "latest") == "myapp:latest"

    def test_private_registry(self):
        reg = ContainerRegistry(registry_url="gcr.io/my-project")
        result = reg._get_full_image_name("myapp", "v2")
        assert result == "gcr.io/my-project/myapp:v2"

    def test_localhost_registry(self):
        reg = ContainerRegistry(registry_url="localhost:5000")
        result = reg._get_full_image_name("test-image", "dev")
        assert result == "localhost:5000/test-image:dev"


# ---------------------------------------------------------------------------
# ContainerRegistry -- simulated paths (no Docker daemon required)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestContainerRegistrySimulated:
    """Tests for methods when Docker daemon is NOT connected.

    The ContainerRegistry constructor tries docker.from_env(). If that fails
    (no daemon running), _docker_client is None and is_available() returns
    False. All mutating operations then return simulated results.

    If Docker IS running, we force the simulated path by creating a registry
    with a known-bad URL that will fail docker.from_env (not possible to
    force easily). Instead we test the code path by checking the contract:
    when is_available() is False, operations return simulated results.
    """

    def _make_unavailable_registry(self) -> ContainerRegistry:
        """Create a registry instance and force _docker_client to None."""
        reg = ContainerRegistry(registry_url="test.example.com")
        reg._docker_client = None  # Force unavailable
        return reg

    def test_is_available_false(self):
        reg = self._make_unavailable_registry()
        assert reg.is_available() is False

    def test_push_image_simulated(self):
        reg = self._make_unavailable_registry()
        result = reg.push_image("myapp", "v1")
        assert result["status"] == "simulated"
        assert "myapp" in result["image"]
        assert "Docker not available" in result["message"]

    def test_pull_image_simulated(self):
        reg = self._make_unavailable_registry()
        result = reg.pull_image("myapp", "v1")
        assert result["status"] == "simulated"
        assert "myapp" in result["image"]

    def test_pull_image_default_tag(self):
        reg = self._make_unavailable_registry()
        result = reg.pull_image("myapp")
        assert "latest" in result["image"]

    def test_build_and_push_simulated(self):
        reg = self._make_unavailable_registry()
        result = reg.build_and_push("/tmp/Dockerfile", "myapp", "v1")
        assert result["status"] == "simulated"

    def test_list_images_unavailable(self):
        reg = self._make_unavailable_registry()
        result = reg.list_images()
        assert result == []

    def test_delete_image_simulated(self):
        reg = self._make_unavailable_registry()
        result = reg.delete_image("myapp", "v1")
        assert result is True

    def test_get_image_info_unavailable(self):
        reg = self._make_unavailable_registry()
        result = reg.get_image_info("myapp", "v1")
        assert result is None

    def test_tag_image_simulated(self):
        reg = self._make_unavailable_registry()
        result = reg.tag_image("source:v1", "target", "v2")
        assert result is True

    def test_push_image_simulated_with_local_image(self):
        reg = self._make_unavailable_registry()
        result = reg.push_image("myapp", "v1", local_image="local:latest")
        assert result["status"] == "simulated"


# ---------------------------------------------------------------------------
# ContainerRegistry -- list_registry_images and inspect_manifest
# (HTTP-based, no Docker daemon needed, but needs requests)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestContainerRegistryHttpMethods:
    """Tests for HTTP-based registry methods when session is not available."""

    def test_list_registry_images_no_session(self):
        reg = ContainerRegistry(registry_url="test.example.com")
        reg._session = None
        result = reg.list_registry_images()
        assert result == []

    def test_inspect_manifest_no_session(self):
        reg = ContainerRegistry(registry_url="test.example.com")
        reg._session = None
        result = reg.inspect_manifest("myapp", "v1")
        assert result is None


# ---------------------------------------------------------------------------
# manage_container_registry dispatcher
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestManageContainerRegistry:
    """Tests for the manage_container_registry convenience function."""

    def test_push_operation_simulated(self):
        """Push without Docker daemon returns simulated."""
        result = manage_container_registry(
            operation="push",
            registry_url="test.example.com",
            image_name="myapp",
            image_tag="v1",
        )
        # Without a running Docker daemon this may be simulated
        # or may succeed if Docker is available -- either is valid
        assert isinstance(result, dict)
        assert "status" in result

    def test_pull_operation_simulated(self):
        result = manage_container_registry(
            operation="pull",
            registry_url="test.example.com",
            image_name="myapp",
            image_tag="v1",
        )
        assert isinstance(result, dict)
        assert "status" in result

    def test_list_operation(self):
        result = manage_container_registry(
            operation="list",
            registry_url="test.example.com",
        )
        assert isinstance(result, list)

    def test_delete_operation(self):
        result = manage_container_registry(
            operation="delete",
            registry_url="test.example.com",
            image_name="myapp",
            image_tag="v1",
        )
        assert isinstance(result, bool)

    def test_info_operation(self):
        result = manage_container_registry(
            operation="info",
            registry_url="test.example.com",
            image_name="myapp",
            image_tag="v1",
        )
        # None when Docker unavailable, dict when available
        assert result is None or isinstance(result, dict)

    def test_tag_operation(self):
        result = manage_container_registry(
            operation="tag",
            registry_url="test.example.com",
            source_image="src:v1",
            target_name="tgt",
            target_tag="v2",
        )
        assert isinstance(result, bool)

    def test_unknown_operation_raises(self):
        with pytest.raises(CodomyrmexError, match="Unknown registry operation"):
            manage_container_registry(
                operation="explode",
                registry_url="test.example.com",
            )

    def test_with_credentials(self):
        result = manage_container_registry(
            operation="list",
            registry_url="test.example.com",
            credentials={
                "username": "user",
                "password": "pass",
            },
        )
        assert isinstance(result, list)

    def test_with_credentials_and_token(self):
        result = manage_container_registry(
            operation="list",
            registry_url="test.example.com",
            credentials={
                "username": "user",
                "password": "pass",
                "token": "jwt-token",
            },
        )
        assert isinstance(result, list)

    def test_build_and_push_operation(self, tmp_path):
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("FROM alpine:latest\n")
        result = manage_container_registry(
            operation="build_and_push",
            registry_url="test.example.com",
            dockerfile_path=str(dockerfile),
            image_name="myapp",
            image_tag="v1",
        )
        assert isinstance(result, dict)
        assert "status" in result

    def test_list_registry_operation(self):
        result = manage_container_registry(
            operation="list_registry",
            registry_url="test.example.com",
        )
        assert isinstance(result, list)

    def test_manifest_operation(self):
        result = manage_container_registry(
            operation="manifest",
            registry_url="test.example.com",
            image_name="myapp",
            image_tag="v1",
        )
        # Returns None when no session or network fails
        assert result is None or isinstance(result, dict)


# ---------------------------------------------------------------------------
# Live Docker daemon tests (only run when Docker is available)
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.skipif(not HAS_DOCKER_DAEMON, reason="Requires running Docker daemon")
class TestContainerRegistryLiveDocker:
    """Tests that require a running Docker daemon.

    These tests use tiny images (hello-world, alpine) to minimize
    resource usage and test real Docker SDK interactions.
    """

    def test_is_available_true(self):
        reg = ContainerRegistry(registry_url="docker.io")
        assert reg.is_available() is True

    def test_list_images_returns_list(self):
        reg = ContainerRegistry(registry_url="docker.io")
        result = reg.list_images()
        assert isinstance(result, list)
        # Each entry should have expected keys if any images exist
        if result:
            entry = result[0]
            assert "name" in entry
            assert "tag" in entry
            assert "image_id" in entry
            assert "size_mb" in entry

    def test_get_image_info_nonexistent(self):
        reg = ContainerRegistry(registry_url="docker.io")
        result = reg.get_image_info("nonexistent-image-xyzzy-12345", "v999")
        assert result is None

    def test_tag_image_nonexistent_source(self):
        reg = ContainerRegistry(registry_url="docker.io")
        result = reg.tag_image(
            "nonexistent-image-xyzzy-12345:v999", "target", "v1"
        )
        assert result is False
