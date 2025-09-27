"""
Docker Manager for Codomyrmex Containerization Module.

Provides comprehensive Docker container management and orchestration.
"""

import os
import sys
import json
import docker
import tempfile
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from codomyrmex.exceptions import CodomyrmexError

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

try:
    from logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class ContainerConfig:
    """Docker container configuration."""

    image_name: str
    tag: str = "latest"
    dockerfile_path: Optional[str] = None
    build_context: str = "."
    build_args: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    ports: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)
    networks: List[str] = field(default_factory=list)
    restart_policy: str = "no"
    labels: Dict[str, str] = field(default_factory=dict)

    def get_full_image_name(self) -> str:
        """Get the full image name with tag."""
        return f"{self.image_name}:{self.tag}"


class DockerManager:
    """
    Comprehensive Docker container manager.

    Features:
    - Container building and management
    - Multi-stage build support
    - Container networking and volumes
    - Resource management and monitoring
    - Docker Compose integration
    """

    def __init__(self, docker_host: Optional[str] = None):
        """
        Initialize the Docker manager.

        Args:
            docker_host: Docker daemon host (optional)
        """
        self.docker_host = docker_host
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Docker client."""
        try:
            if self.docker_host:
                self.client = docker.DockerClient(base_url=self.docker_host)
            else:
                self.client = docker.from_env()

            # Test connection
            self.client.ping()
            logger.info("Docker client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None

    def build_image(
        self,
        config: ContainerConfig,
        push: bool = False,
        registry_auth: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Build a Docker image from configuration.

        Args:
            config: Container configuration
            push: Whether to push the image after building
            registry_auth: Registry authentication credentials

        Returns:
            Dict containing build results
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            logger.info(f"Building Docker image: {config.get_full_image_name()}")

            # Prepare build arguments
            build_kwargs = {
                "path": config.build_context,
                "tag": config.get_full_image_name(),
                "rm": True,
                "pull": True,
            }

            # Add custom Dockerfile if specified
            if config.dockerfile_path:
                build_kwargs["dockerfile"] = config.dockerfile_path

            # Add build arguments
            if config.build_args:
                build_kwargs["buildargs"] = config.build_args

            # Build the image
            image, build_logs = self.client.images.build(**build_kwargs)

            # Collect build logs
            logs = []
            for log_line in build_logs:
                if "stream" in log_line:
                    logs.append(log_line["stream"].strip())

            result = {
                "success": True,
                "image_id": image.id,
                "image_tags": image.tags,
                "build_logs": logs,
                "build_time": datetime.now(timezone.utc).isoformat(),
            }

            # Push if requested
            if push and registry_auth:
                push_result = self.push_image(
                    config.get_full_image_name(), registry_auth
                )
                result["push_result"] = push_result

            logger.info(f"Successfully built image: {config.get_full_image_name()}")
            return result

        except Exception as e:
            logger.error(f"Failed to build image {config.get_full_image_name()}: {e}")
            return {"success": False, "error": str(e)}

    def push_image(
        self, image_name: str, auth_config: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Push a Docker image to registry.

        Args:
            image_name: Full image name with tag
            auth_config: Registry authentication credentials

        Returns:
            Dict containing push results
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            logger.info(f"Pushing image: {image_name}")

            # Push the image
            push_logs = self.client.images.push(image_name, auth_config=auth_config)

            # Parse push logs
            logs = []
            if hasattr(push_logs, "__iter__"):
                for log_line in push_logs:
                    if isinstance(log_line, dict) and "status" in log_line:
                        logs.append(log_line["status"])

            return {
                "success": True,
                "image": image_name,
                "push_logs": logs,
                "push_time": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to push image {image_name}: {e}")
            return {"success": False, "error": str(e)}

    def run_container(
        self, config: ContainerConfig, detach: bool = True
    ) -> Dict[str, Any]:
        """
        Run a Docker container.

        Args:
            config: Container configuration
            detach: Whether to run in detached mode

        Returns:
            Dict containing container run results
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            logger.info(f"Running container: {config.get_full_image_name()}")

            # Prepare run arguments
            run_kwargs = {
                "image": config.get_full_image_name(),
                "detach": detach,
                "name": f"{config.image_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            }

            # Add environment variables
            if config.environment:
                run_kwargs["environment"] = config.environment

            # Add port mappings
            if config.ports:
                run_kwargs["ports"] = config.ports

            # Add volume mappings
            if config.volumes:
                run_kwargs["volumes"] = config.volumes

            # Add network configuration
            if config.networks:
                run_kwargs["network"] = config.networks[0]

            # Add restart policy
            if config.restart_policy != "no":
                run_kwargs["restart_policy"] = {"Name": config.restart_policy}

            # Add labels
            if config.labels:
                run_kwargs["labels"] = config.labels

            # Run the container
            container = self.client.containers.run(**run_kwargs)

            return {
                "success": True,
                "container_id": container.id,
                "container_name": container.name,
                "status": container.status,
                "start_time": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to run container {config.get_full_image_name()}: {e}")
            return {"success": False, "error": str(e)}

    def list_containers(self, show_all: bool = False) -> List[Dict[str, Any]]:
        """
        List Docker containers.

        Args:
            show_all: Whether to show all containers (including stopped)

        Returns:
            List of container information
        """
        if not self.client:
            return []

        try:
            containers = self.client.containers.list(all=show_all)
            return [
                {
                    "id": container.id,
                    "name": container.name,
                    "image": (
                        container.image.tags[0]
                        if container.image.tags
                        else container.image.id
                    ),
                    "status": container.status,
                    "created": container.attrs.get("Created", ""),
                    "ports": container.attrs.get("NetworkSettings", {}).get(
                        "Ports", {}
                    ),
                }
                for container in containers
            ]

        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []

    def stop_container(self, container_id: str) -> Dict[str, Any]:
        """
        Stop a Docker container.

        Args:
            container_id: Container ID or name

        Returns:
            Dict containing stop results
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            container = self.client.containers.get(container_id)
            container.stop()

            return {
                "success": True,
                "container_id": container_id,
                "stop_time": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to stop container {container_id}: {e}")
            return {"success": False, "error": str(e)}

    def remove_container(
        self, container_id: str, force: bool = False
    ) -> Dict[str, Any]:
        """
        Remove a Docker container.

        Args:
            container_id: Container ID or name
            force: Force removal of running container

        Returns:
            Dict containing removal results
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)

            return {
                "success": True,
                "container_id": container_id,
                "removal_time": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to remove container {container_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_container_logs(self, container_id: str, tail: int = 100) -> Dict[str, Any]:
        """
        Get logs from a Docker container.

        Args:
            container_id: Container ID or name
            tail: Number of log lines to retrieve

        Returns:
            Dict containing container logs
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode("utf-8").split("\n")

            return {
                "success": True,
                "container_id": container_id,
                "logs": logs,
                "log_count": len(logs),
            }

        except Exception as e:
            logger.error(f"Failed to get logs for container {container_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """
        Get statistics for a Docker container.

        Args:
            container_id: Container ID or name

        Returns:
            Dict containing container statistics
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)

            return {
                "success": True,
                "container_id": container_id,
                "cpu_usage": stats.get("cpu_stats", {}).get("cpu_usage", {}),
                "memory_usage": stats.get("memory_stats", {}),
                "network_stats": stats.get("networks", {}),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get stats for container {container_id}: {e}")
            return {"success": False, "error": str(e)}

    def create_network(self, name: str, driver: str = "bridge") -> Dict[str, Any]:
        """
        Create a Docker network.

        Args:
            name: Network name
            driver: Network driver (default: bridge)

        Returns:
            Dict containing network creation results
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            network = self.client.networks.create(name, driver=driver)

            return {
                "success": True,
                "network_id": network.id,
                "network_name": name,
                "driver": driver,
                "creation_time": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to create network {name}: {e}")
            return {"success": False, "error": str(e)}

    def list_images(self) -> List[Dict[str, Any]]:
        """
        List Docker images.

        Returns:
            List of image information
        """
        if not self.client:
            return []

        try:
            images = self.client.images.list()
            return [
                {
                    "id": image.id,
                    "tags": image.tags,
                    "size": image.attrs.get("Size", 0),
                    "created": image.attrs.get("Created", ""),
                }
                for image in images
            ]

        except Exception as e:
            logger.error(f"Failed to list images: {e}")
            return []

    def remove_image(self, image_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Remove a Docker image.

        Args:
            image_name: Image name or ID
            force: Force removal of image

        Returns:
            Dict containing image removal results
        """
        if not self.client:
            return {"success": False, "error": "Docker client not available"}

        try:
            self.client.images.remove(image_name, force=force)

            return {
                "success": True,
                "image": image_name,
                "removal_time": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to remove image {image_name}: {e}")
            return {"success": False, "error": str(e)}

    def get_docker_info(self) -> Dict[str, Any]:
        """
        Get Docker system information.

        Returns:
            Dict containing Docker system information
        """
        if not self.client:
            return {"available": False, "error": "Docker client not available"}

        try:
            info = self.client.info()
            version = self.client.version()

            return {
                "available": True,
                "server_version": info.get("ServerVersion", ""),
                "api_version": version.get("ApiVersion", ""),
                "containers": info.get("Containers", 0),
                "containers_running": info.get("ContainersRunning", 0),
                "images": info.get("Images", 0),
                "storage_driver": info.get("Driver", ""),
                "architecture": info.get("Architecture", ""),
                "os": info.get("OSType", ""),
                "kernel_version": info.get("KernelVersion", ""),
            }

        except Exception as e:
            logger.error(f"Failed to get Docker info: {e}")
            return {"available": False, "error": str(e)}


# Convenience functions
def build_containers(
    config: ContainerConfig,
    push: bool = False,
    registry_auth: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to build containers.

    Args:
        config: Container configuration
        push: Whether to push after building
        registry_auth: Registry authentication

    Returns:
        Dict containing build results
    """
    manager = DockerManager()
    return manager.build_image(config, push, registry_auth)


def manage_containers() -> DockerManager:
    """
    Convenience function to create Docker manager.

    Returns:
        DockerManager: Configured Docker manager
    """
    return DockerManager()
