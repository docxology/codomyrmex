"""
Unit tests for containerization.exceptions — Zero-Mock compliant.

Covers: ContainerError, ImageBuildError, NetworkError, VolumeError,
RegistryError, KubernetesError — context field storage,
inheritance from BaseContainerError, raise/catch.
"""

import pytest

from codomyrmex.containerization.exceptions import (
    ContainerError,
    ImageBuildError,
    KubernetesError,
    NetworkError,
    RegistryError,
    VolumeError,
)
from codomyrmex.exceptions import ContainerError as BaseContainerError

# ── ContainerError ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestContainerError:
    def test_is_base_container_error(self):
        e = ContainerError("failed")
        assert isinstance(e, BaseContainerError)

    def test_message_stored(self):
        e = ContainerError("container failed")
        assert "container failed" in str(e)

    def test_container_id_stored(self):
        e = ContainerError("failed", container_id="abc123")
        assert e.context["container_id"] == "abc123"

    def test_container_id_none_not_in_context(self):
        e = ContainerError("failed")
        assert "container_id" not in e.context

    def test_container_name_stored(self):
        e = ContainerError("failed", container_name="my-app")
        assert e.context["container_name"] == "my-app"

    def test_container_name_none_not_in_context(self):
        e = ContainerError("failed")
        assert "container_name" not in e.context

    def test_both_fields_stored(self):
        e = ContainerError("failed", container_id="id1", container_name="n1")
        assert e.context["container_id"] == "id1"
        assert e.context["container_name"] == "n1"

    def test_raise_and_catch(self):
        with pytest.raises(ContainerError, match="failed"):
            raise ContainerError("failed")

    def test_catch_as_base(self):
        with pytest.raises(BaseContainerError):
            raise ContainerError("failed")


# ── ImageBuildError ────────────────────────────────────────────────────


@pytest.mark.unit
class TestImageBuildError:
    def test_is_base_container_error(self):
        e = ImageBuildError("build failed")
        assert isinstance(e, BaseContainerError)

    def test_image_name_stored(self):
        e = ImageBuildError("failed", image_name="myapp")
        assert e.context["image_name"] == "myapp"

    def test_image_name_none_not_in_context(self):
        e = ImageBuildError("failed")
        assert "image_name" not in e.context

    def test_image_tag_stored(self):
        e = ImageBuildError("failed", image_tag="v1.0")
        assert e.context["image_tag"] == "v1.0"

    def test_dockerfile_path_stored(self):
        e = ImageBuildError("failed", dockerfile_path="./Dockerfile")
        assert e.context["dockerfile_path"] == "./Dockerfile"

    def test_build_step_stored(self):
        e = ImageBuildError("failed", build_step=5)
        assert e.context["build_step"] == 5

    def test_build_step_zero_stored(self):
        """build_step=0 uses 'is not None' guard → stored."""
        e = ImageBuildError("failed", build_step=0)
        assert "build_step" in e.context
        assert e.context["build_step"] == 0

    def test_build_step_none_not_in_context(self):
        e = ImageBuildError("failed")
        assert "build_step" not in e.context

    def test_none_fields_not_in_context(self):
        e = ImageBuildError("failed")
        assert "image_name" not in e.context
        assert "image_tag" not in e.context
        assert "dockerfile_path" not in e.context

    def test_all_fields_stored(self):
        e = ImageBuildError(
            "failed",
            image_name="app",
            image_tag="latest",
            dockerfile_path="./Dockerfile",
            build_step=3,
        )
        assert e.context["image_name"] == "app"
        assert e.context["image_tag"] == "latest"
        assert e.context["dockerfile_path"] == "./Dockerfile"
        assert e.context["build_step"] == 3

    def test_raise_and_catch(self):
        with pytest.raises(ImageBuildError):
            raise ImageBuildError("build failed", image_name="myapp", build_step=2)


# ── NetworkError ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestNetworkError:
    def test_is_base_container_error(self):
        e = NetworkError("net failed")
        assert isinstance(e, BaseContainerError)

    def test_network_name_stored(self):
        e = NetworkError("failed", network_name="app-network")
        assert e.context["network_name"] == "app-network"

    def test_network_id_stored(self):
        e = NetworkError("failed", network_id="net-xyz")
        assert e.context["network_id"] == "net-xyz"

    def test_driver_stored(self):
        e = NetworkError("failed", driver="bridge")
        assert e.context["driver"] == "bridge"

    def test_none_fields_not_in_context(self):
        e = NetworkError("failed")
        assert "network_name" not in e.context
        assert "network_id" not in e.context
        assert "driver" not in e.context

    def test_all_fields_stored(self):
        e = NetworkError("failed", network_name="n", network_id="id1", driver="host")
        assert e.context["network_name"] == "n"
        assert e.context["network_id"] == "id1"
        assert e.context["driver"] == "host"

    def test_raise_and_catch(self):
        with pytest.raises(NetworkError):
            raise NetworkError("net error", network_name="my-net")


# ── VolumeError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestVolumeError:
    def test_is_base_container_error(self):
        e = VolumeError("vol failed")
        assert isinstance(e, BaseContainerError)

    def test_volume_name_stored(self):
        e = VolumeError("failed", volume_name="app-data")
        assert e.context["volume_name"] == "app-data"

    def test_mount_point_stored(self):
        e = VolumeError("failed", mount_point="/var/data")
        assert e.context["mount_point"] == "/var/data"

    def test_driver_stored(self):
        e = VolumeError("failed", driver="local")
        assert e.context["driver"] == "local"

    def test_none_fields_not_in_context(self):
        e = VolumeError("failed")
        assert "volume_name" not in e.context
        assert "mount_point" not in e.context
        assert "driver" not in e.context

    def test_all_fields_stored(self):
        e = VolumeError("failed", volume_name="v1", mount_point="/data", driver="nfs")
        assert e.context["volume_name"] == "v1"
        assert e.context["mount_point"] == "/data"
        assert e.context["driver"] == "nfs"

    def test_raise_and_catch(self):
        with pytest.raises(VolumeError):
            raise VolumeError("volume failed", volume_name="data")


# ── RegistryError ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestRegistryError:
    def test_is_base_container_error(self):
        e = RegistryError("reg failed")
        assert isinstance(e, BaseContainerError)

    def test_registry_url_stored(self):
        e = RegistryError("failed", registry_url="registry.example.com")
        assert e.context["registry_url"] == "registry.example.com"

    def test_registry_url_none_not_in_context(self):
        e = RegistryError("failed")
        assert "registry_url" not in e.context

    def test_image_reference_stored(self):
        e = RegistryError("failed", image_reference="registry.example.com/app:latest")
        assert e.context["image_reference"] == "registry.example.com/app:latest"

    def test_image_reference_none_not_in_context(self):
        e = RegistryError("failed")
        assert "image_reference" not in e.context

    def test_both_fields_stored(self):
        e = RegistryError(
            "failed",
            registry_url="reg.io",
            image_reference="reg.io/app:v1",
        )
        assert e.context["registry_url"] == "reg.io"
        assert e.context["image_reference"] == "reg.io/app:v1"

    def test_raise_and_catch(self):
        with pytest.raises(RegistryError):
            raise RegistryError("push failed", registry_url="registry.io")


# ── KubernetesError ────────────────────────────────────────────────────


@pytest.mark.unit
class TestKubernetesError:
    def test_is_base_container_error(self):
        e = KubernetesError("k8s failed")
        assert isinstance(e, BaseContainerError)

    def test_resource_type_stored(self):
        e = KubernetesError("failed", resource_type="deployment")
        assert e.context["resource_type"] == "deployment"

    def test_resource_type_none_not_in_context(self):
        e = KubernetesError("failed")
        assert "resource_type" not in e.context

    def test_resource_name_stored(self):
        e = KubernetesError("failed", resource_name="my-app")
        assert e.context["resource_name"] == "my-app"

    def test_namespace_stored(self):
        e = KubernetesError("failed", namespace="production")
        assert e.context["namespace"] == "production"

    def test_none_fields_not_in_context(self):
        e = KubernetesError("failed")
        assert "resource_type" not in e.context
        assert "resource_name" not in e.context
        assert "namespace" not in e.context

    def test_all_fields_stored(self):
        e = KubernetesError(
            "failed",
            resource_type="pod",
            resource_name="my-pod",
            namespace="default",
        )
        assert e.context["resource_type"] == "pod"
        assert e.context["resource_name"] == "my-pod"
        assert e.context["namespace"] == "default"

    def test_raise_and_catch(self):
        with pytest.raises(KubernetesError):
            raise KubernetesError("k8s error", resource_type="pod", namespace="prod")
