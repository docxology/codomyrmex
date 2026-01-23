"""Containerization Exception Classes.

This module defines exceptions specific to containerization operations
including Docker containers, images, networks, and volumes.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import CodomyrmexError, ContainerError as BaseContainerError


class ContainerError(BaseContainerError):
    """Base exception for container-related errors.

    Raised when container operations fail, including creation,
    start, stop, and management operations.
    """

    def __init__(
        self,
        message: str,
        container_id: str | None = None,
        container_name: str | None = None,
        **kwargs: Any
    ):
        """Initialize ContainerError.

        Args:
            message: Error description
            container_id: ID of the container
            container_name: Name of the container
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if container_id:
            self.context["container_id"] = container_id
        if container_name:
            self.context["container_name"] = container_name


class ImageBuildError(BaseContainerError):
    """Raised when container image build operations fail.

    This includes Dockerfile parsing errors, build step failures,
    and layer caching issues.
    """

    def __init__(
        self,
        message: str,
        image_name: str | None = None,
        image_tag: str | None = None,
        dockerfile_path: str | None = None,
        build_step: int | None = None,
        **kwargs: Any
    ):
        """Initialize ImageBuildError.

        Args:
            message: Error description
            image_name: Name of the image being built
            image_tag: Tag of the image
            dockerfile_path: Path to the Dockerfile
            build_step: Step number where build failed
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if image_name:
            self.context["image_name"] = image_name
        if image_tag:
            self.context["image_tag"] = image_tag
        if dockerfile_path:
            self.context["dockerfile_path"] = dockerfile_path
        if build_step is not None:
            self.context["build_step"] = build_step


class NetworkError(BaseContainerError):
    """Raised when container network operations fail.

    This includes network creation, connection, disconnection,
    and DNS resolution issues.
    """

    def __init__(
        self,
        message: str,
        network_name: str | None = None,
        network_id: str | None = None,
        driver: str | None = None,
        **kwargs: Any
    ):
        """Initialize NetworkError.

        Args:
            message: Error description
            network_name: Name of the network
            network_id: ID of the network
            driver: Network driver type
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if network_name:
            self.context["network_name"] = network_name
        if network_id:
            self.context["network_id"] = network_id
        if driver:
            self.context["driver"] = driver


class VolumeError(BaseContainerError):
    """Raised when container volume operations fail.

    This includes volume creation, mounting, unmounting,
    and data persistence issues.
    """

    def __init__(
        self,
        message: str,
        volume_name: str | None = None,
        mount_point: str | None = None,
        driver: str | None = None,
        **kwargs: Any
    ):
        """Initialize VolumeError.

        Args:
            message: Error description
            volume_name: Name of the volume
            mount_point: Mount point path in container
            driver: Volume driver type
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if volume_name:
            self.context["volume_name"] = volume_name
        if mount_point:
            self.context["mount_point"] = mount_point
        if driver:
            self.context["driver"] = driver


class RegistryError(BaseContainerError):
    """Raised when container registry operations fail.

    This includes push, pull, authentication, and
    registry communication issues.
    """

    def __init__(
        self,
        message: str,
        registry_url: str | None = None,
        image_reference: str | None = None,
        **kwargs: Any
    ):
        """Initialize RegistryError.

        Args:
            message: Error description
            registry_url: URL of the registry
            image_reference: Full image reference (registry/image:tag)
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if registry_url:
            self.context["registry_url"] = registry_url
        if image_reference:
            self.context["image_reference"] = image_reference


class KubernetesError(BaseContainerError):
    """Raised when Kubernetes operations fail.

    This includes deployment, service, pod, and
    cluster management issues.
    """

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        resource_name: str | None = None,
        namespace: str | None = None,
        **kwargs: Any
    ):
        """Initialize KubernetesError.

        Args:
            message: Error description
            resource_type: Type of Kubernetes resource (pod, deployment, etc.)
            resource_name: Name of the resource
            namespace: Kubernetes namespace
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if resource_type:
            self.context["resource_type"] = resource_type
        if resource_name:
            self.context["resource_name"] = resource_name
        if namespace:
            self.context["namespace"] = namespace


__all__ = [
    "ContainerError",
    "ImageBuildError",
    "NetworkError",
    "VolumeError",
    "RegistryError",
    "KubernetesError",
]
