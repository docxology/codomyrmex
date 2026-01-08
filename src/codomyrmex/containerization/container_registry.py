from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import os
import subprocess

from dataclasses import dataclass, field
from docker.errors import APIError, DockerException, ImageNotFound
import base64
import docker
import hashlib
import requests

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger




























#!/usr/bin/env python3
"""
Container Registry Module for Codomyrmex Containerization.

This module provides container registry management, image storage,
and distribution capabilities using Docker SDK and registry APIs.
"""



logger = get_logger(__name__)

# Try to import Docker SDK
try:
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    APIError = Exception
    DockerException = Exception
    ImageNotFound = Exception
    DOCKER_AVAILABLE = False
    logger.warning("Docker SDK not available. Install with: pip install docker")

# Try to import requests for registry API calls
try:
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False


@dataclass
class ContainerImage:
    """Container image information."""
    name: str
    tag: str
    registry_url: str
    size_mb: float
    created_at: datetime
    digest: Optional[str] = None
    layers: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    vulnerabilities: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RegistryCredentials:
    """Container registry credentials."""
    username: str
    password: str
    registry_url: str
    token: Optional[str] = None

    def get_auth_header(self) -> str:
        """Get authorization header value."""
        if self.token:
            return f"Bearer {self.token}"
        auth_string = f"{self.username}:{self.password}"
        encoded = base64.b64encode(auth_string.encode()).decode()
        return f"Basic {encoded}"


class ContainerRegistry:
    """Container registry management system.

    Supports Docker Hub, private registries, and OCI-compliant registries.
    """

    def __init__(
        self,
        registry_url: str,
        credentials: Optional[RegistryCredentials] = None
    ):
        """Initialize container registry manager.

        Args:
            registry_url: URL of the container registry (e.g., docker.io, gcr.io)
            credentials: Registry authentication credentials
        """
        self.registry_url = registry_url.rstrip('/')
        self.credentials = credentials
        self._docker_client = None
        self._session = None

        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize Docker client and HTTP session."""
        # Initialize Docker client
        if DOCKER_AVAILABLE:
            try:
                self._docker_client = docker.from_env()
                logger.info("Docker client initialized")
            except DockerException as e:
                logger.warning(f"Failed to initialize Docker client: {e}")
                self._docker_client = None
        else:
            logger.warning("Docker SDK not available")

        # Initialize HTTP session for registry API
        if REQUESTS_AVAILABLE:
            self._session = requests.Session()
            if self.credentials:
                self._session.headers["Authorization"] = self.credentials.get_auth_header()

    def is_available(self) -> bool:
        """Check if Docker is available."""
        return self._docker_client is not None

    def _get_full_image_name(self, image_name: str, image_tag: str) -> str:
        """Get full image name including registry."""
        if self.registry_url in ["docker.io", "registry.hub.docker.com", ""]:
            return f"{image_name}:{image_tag}"
        return f"{self.registry_url}/{image_name}:{image_tag}"

    def push_image(
        self,
        image_name: str,
        image_tag: str,
        local_image: Optional[str] = None
    ) -> dict[str, Any]:
        """Push container image to registry.

        Args:
            image_name: Name of the image in the registry
            image_tag: Image tag
            local_image: Local image name (if different from remote name)

        Returns:
            Push result with status and details

        Raises:
            CodomyrmexError: If push fails
        """
        full_name = self._get_full_image_name(image_name, image_tag)
        local_name = local_image or f"{image_name}:{image_tag}"

        if not self.is_available():
            logger.info(f"[SIMULATED] Push image: {full_name}")
            return {
                "status": "simulated",
                "image": full_name,
                "message": "Docker not available - operation simulated"
            }

        start_time = datetime.now()

        try:
            # Get local image
            try:
                image = self._docker_client.images.get(local_name)
            except ImageNotFound:
                raise CodomyrmexError(f"Local image not found: {local_name}")

            # Tag image for the registry
            image.tag(self.registry_url + "/" + image_name if self.registry_url else image_name, image_tag)

            # Login to registry if credentials provided
            if self.credentials:
                self._docker_client.login(
                    username=self.credentials.username,
                    password=self.credentials.password,
                    registry=self.registry_url or "https://index.docker.io/v1/"
                )

            # Push image
            push_result = self._docker_client.images.push(
                repository=self.registry_url + "/" + image_name if self.registry_url else image_name,
                tag=image_tag,
                stream=True,
                decode=True
            )

            # Parse push output
            digest = None
            size = 0
            for line in push_result:
                if "digest" in line:
                    digest = line.get("digest")
                if "size" in line:
                    size = line.get("size", 0)
                if "error" in line:
                    raise CodomyrmexError(f"Push failed: {line['error']}")

            duration = (datetime.now() - start_time).total_seconds()

            logger.info(f"Pushed image {full_name} in {duration:.2f}s")

            return {
                "status": "success",
                "image": full_name,
                "digest": digest,
                "size_bytes": size,
                "duration_seconds": duration
            }

        except DockerException as e:
            raise CodomyrmexError(f"Failed to push image: {e}")

    def pull_image(
        self,
        image_name: str,
        image_tag: str = "latest"
    ) -> dict[str, Any]:
        """Pull container image from registry.

        Args:
            image_name: Name of the image
            image_tag: Image tag

        Returns:
            Pull result with local image ID

        Raises:
            CodomyrmexError: If pull fails
        """
        full_name = self._get_full_image_name(image_name, image_tag)

        if not self.is_available():
            logger.info(f"[SIMULATED] Pull image: {full_name}")
            return {
                "status": "simulated",
                "image": full_name,
                "message": "Docker not available - operation simulated"
            }

        start_time = datetime.now()

        try:
            # Login if credentials provided
            if self.credentials:
                self._docker_client.login(
                    username=self.credentials.username,
                    password=self.credentials.password,
                    registry=self.registry_url or "https://index.docker.io/v1/"
                )

            # Pull image
            image = self._docker_client.images.pull(
                repository=self.registry_url + "/" + image_name if self.registry_url not in ["docker.io", ""] else image_name,
                tag=image_tag
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Get image info
            size_mb = sum(layer.get("Size", 0) for layer in image.history()) / (1024 * 1024)

            logger.info(f"Pulled image {full_name} in {duration:.2f}s")

            return {
                "status": "success",
                "image": full_name,
                "image_id": image.id,
                "size_mb": round(size_mb, 2),
                "duration_seconds": duration,
                "tags": image.tags
            }

        except ImageNotFound:
            raise CodomyrmexError(f"Image not found in registry: {full_name}")
        except DockerException as e:
            raise CodomyrmexError(f"Failed to pull image: {e}")

    def build_and_push(
        self,
        dockerfile_path: str,
        image_name: str,
        image_tag: str,
        build_args: Optional[dict[str, str]] = None,
        no_cache: bool = False
    ) -> dict[str, Any]:
        """Build and push an image to the registry.

        Args:
            dockerfile_path: Path to Dockerfile or directory containing it
            image_name: Name for the image
            image_tag: Tag for the image
            build_args: Build arguments
            no_cache: Whether to disable cache

        Returns:
            Build and push result
        """
        full_name = self._get_full_image_name(image_name, image_tag)

        if not self.is_available():
            logger.info(f"[SIMULATED] Build and push: {full_name}")
            return {
                "status": "simulated",
                "image": full_name,
                "message": "Docker not available - operation simulated"
            }

        path = Path(dockerfile_path)
        if path.is_file():
            context_path = str(path.parent)
            dockerfile = path.name
        else:
            context_path = str(path)
            dockerfile = "Dockerfile"

        start_time = datetime.now()

        try:
            # Build image
            image, build_logs = self._docker_client.images.build(
                path=context_path,
                dockerfile=dockerfile,
                tag=full_name,
                buildargs=build_args,
                nocache=no_cache,
                rm=True
            )

            build_duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Built image {full_name} in {build_duration:.2f}s")

            # Push image
            push_result = self.push_image(image_name, image_tag, full_name)

            total_duration = (datetime.now() - start_time).total_seconds()

            return {
                "status": "success",
                "image": full_name,
                "image_id": image.id,
                "build_duration_seconds": build_duration,
                "total_duration_seconds": total_duration,
                "push_result": push_result
            }

        except DockerException as e:
            raise CodomyrmexError(f"Failed to build and push image: {e}")

    def list_images(
        self,
        repository: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """List images in the local Docker cache or registry.

        Args:
            repository: Filter by repository name

        Returns:
            List of image information
        """
        if not self.is_available():
            return []

        try:
            images = self._docker_client.images.list()
            result = []

            for image in images:
                for tag in image.tags:
                    if repository and not tag.startswith(repository):
                        continue

                    # Parse name and tag
                    if ":" in tag:
                        name, img_tag = tag.rsplit(":", 1)
                    else:
                        name, img_tag = tag, "latest"

                    result.append({
                        "name": name,
                        "tag": img_tag,
                        "image_id": image.short_id,
                        "size_mb": round(image.attrs.get("Size", 0) / (1024 * 1024), 2),
                        "created": image.attrs.get("Created"),
                        "labels": image.labels
                    })

            return result

        except DockerException as e:
            logger.error(f"Failed to list images: {e}")
            return []

    def list_registry_images(
        self,
        repository: Optional[str] = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """List images directly from the registry API.

        Args:
            repository: Repository name to list
            limit: Maximum number of images to return

        Returns:
            List of image information from registry
        """
        if not REQUESTS_AVAILABLE or not self._session:
            logger.warning("Requests not available for registry API calls")
            return []

        try:
            # Docker Registry API v2
            catalog_url = f"https://{self.registry_url}/v2/_catalog"
            response = self._session.get(catalog_url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                repositories = data.get("repositories", [])

                if repository:
                    repositories = [r for r in repositories if repository in r]

                result = []
                for repo in repositories[:limit]:
                    # Get tags for each repository
                    tags_url = f"https://{self.registry_url}/v2/{repo}/tags/list"
                    tags_response = self._session.get(tags_url, timeout=30)

                    if tags_response.status_code == 200:
                        tags_data = tags_response.json()
                        for tag in tags_data.get("tags", []):
                            result.append({
                                "name": repo,
                                "tag": tag,
                                "registry_url": self.registry_url
                            })

                return result

            logger.warning(f"Registry API returned status {response.status_code}")
            return []

        except Exception as e:
            logger.error(f"Failed to list registry images: {e}")
            return []

    def delete_image(
        self,
        image_name: str,
        image_tag: str,
        local_only: bool = False
    ) -> bool:
        """Delete image from local cache or registry.

        Args:
            image_name: Name of the image
            image_tag: Image tag
            local_only: If True, only delete from local cache

        Returns:
            True if deleted successfully
        """
        full_name = self._get_full_image_name(image_name, image_tag)

        if not self.is_available():
            logger.info(f"[SIMULATED] Delete image: {full_name}")
            return True

        try:
            # Delete from local Docker
            self._docker_client.images.remove(full_name, force=True)
            logger.info(f"Deleted local image: {full_name}")

            if not local_only and REQUESTS_AVAILABLE and self._session:
                # Try to delete from registry (requires delete enabled on registry)
                try:
                    # Get manifest digest
                    manifest_url = f"https://{self.registry_url}/v2/{image_name}/manifests/{image_tag}"
                    response = self._session.head(
                        manifest_url,
                        headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"},
                        timeout=30
                    )

                    if response.status_code == 200:
                        digest = response.headers.get("Docker-Content-Digest")
                        if digest:
                            delete_url = f"https://{self.registry_url}/v2/{image_name}/manifests/{digest}"
                            delete_response = self._session.delete(delete_url, timeout=30)
                            if delete_response.status_code in [200, 202]:
                                logger.info(f"Deleted image from registry: {full_name}")
                except Exception as e:
                    logger.warning(f"Could not delete from registry: {e}")

            return True

        except ImageNotFound:
            logger.warning(f"Image not found: {full_name}")
            return False
        except DockerException as e:
            logger.error(f"Failed to delete image: {e}")
            return False

    def get_image_info(
        self,
        image_name: str,
        image_tag: str
    ) -> Optional[dict[str, Any]]:
        """Get detailed information about an image.

        Args:
            image_name: Name of the image
            image_tag: Image tag

        Returns:
            Image information or None if not found
        """
        full_name = self._get_full_image_name(image_name, image_tag)

        if not self.is_available():
            return None

        try:
            image = self._docker_client.images.get(full_name)

            return {
                "name": image_name,
                "tag": image_tag,
                "registry_url": self.registry_url,
                "image_id": image.id,
                "short_id": image.short_id,
                "size_mb": round(image.attrs.get("Size", 0) / (1024 * 1024), 2),
                "created": image.attrs.get("Created"),
                "architecture": image.attrs.get("Architecture"),
                "os": image.attrs.get("Os"),
                "layers": [layer["Id"] for layer in image.history() if layer.get("Id")],
                "labels": image.labels,
                "tags": image.tags,
                "config": {
                    "env": image.attrs.get("Config", {}).get("Env", []),
                    "cmd": image.attrs.get("Config", {}).get("Cmd"),
                    "entrypoint": image.attrs.get("Config", {}).get("Entrypoint"),
                    "exposed_ports": list(image.attrs.get("Config", {}).get("ExposedPorts", {}).keys())
                }
            }

        except ImageNotFound:
            return None
        except DockerException as e:
            logger.error(f"Failed to get image info: {e}")
            return None

    def tag_image(
        self,
        source_image: str,
        target_name: str,
        target_tag: str
    ) -> bool:
        """Tag an image for the registry.

        Args:
            source_image: Source image name
            target_name: Target repository name
            target_tag: Target tag

        Returns:
            True if tagged successfully
        """
        if not self.is_available():
            logger.info(f"[SIMULATED] Tag image: {source_image} -> {target_name}:{target_tag}")
            return True

        try:
            image = self._docker_client.images.get(source_image)
            full_target = self._get_full_image_name(target_name, target_tag)
            image.tag(full_target)
            logger.info(f"Tagged {source_image} as {full_target}")
            return True

        except ImageNotFound:
            logger.error(f"Source image not found: {source_image}")
            return False
        except DockerException as e:
            logger.error(f"Failed to tag image: {e}")
            return False

    def inspect_manifest(
        self,
        image_name: str,
        image_tag: str
    ) -> Optional[dict[str, Any]]:
        """Inspect image manifest from registry.

        Args:
            image_name: Image name
            image_tag: Image tag

        Returns:
            Manifest information
        """
        if not REQUESTS_AVAILABLE or not self._session:
            return None

        try:
            manifest_url = f"https://{self.registry_url}/v2/{image_name}/manifests/{image_tag}"
            response = self._session.get(
                manifest_url,
                headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            logger.error(f"Failed to inspect manifest: {e}")
            return None


def manage_container_registry(
    operation: str,
    registry_url: str,
    credentials: Optional[dict[str, str]] = None,
    **kwargs: Any
) -> Any:
    """Manage container registry operations.

    Args:
        operation: Operation to perform ('push', 'pull', 'list', 'delete', 'info', 'tag')
        registry_url: URL of the container registry
        credentials: Optional credentials dict with 'username' and 'password'
        **kwargs: Operation-specific arguments

    Returns:
        Operation result
    """
    creds = None
    if credentials:
        creds = RegistryCredentials(
            username=credentials.get("username", ""),
            password=credentials.get("password", ""),
            registry_url=registry_url,
            token=credentials.get("token")
        )

    registry = ContainerRegistry(registry_url, credentials=creds)

    if operation == "push":
        return registry.push_image(
            kwargs.get("image_name"),
            kwargs.get("image_tag"),
            kwargs.get("local_image")
        )
    elif operation == "pull":
        return registry.pull_image(
            kwargs.get("image_name"),
            kwargs.get("image_tag", "latest")
        )
    elif operation == "build_and_push":
        return registry.build_and_push(
            kwargs.get("dockerfile_path"),
            kwargs.get("image_name"),
            kwargs.get("image_tag"),
            kwargs.get("build_args"),
            kwargs.get("no_cache", False)
        )
    elif operation == "list":
        return registry.list_images(kwargs.get("repository"))
    elif operation == "list_registry":
        return registry.list_registry_images(
            kwargs.get("repository"),
            kwargs.get("limit", 100)
        )
    elif operation == "delete":
        return registry.delete_image(
            kwargs.get("image_name"),
            kwargs.get("image_tag"),
            kwargs.get("local_only", False)
        )
    elif operation == "info":
        return registry.get_image_info(
            kwargs.get("image_name"),
            kwargs.get("image_tag")
        )
    elif operation == "tag":
        return registry.tag_image(
            kwargs.get("source_image"),
            kwargs.get("target_name"),
            kwargs.get("target_tag")
        )
    elif operation == "manifest":
        return registry.inspect_manifest(
            kwargs.get("image_name"),
            kwargs.get("image_tag")
        )
    else:
        raise CodomyrmexError(f"Unknown registry operation: {operation}")
