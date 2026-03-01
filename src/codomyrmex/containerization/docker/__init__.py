"""
Docker container management utilities.

Provides utilities for building, managing, and running Docker containers.
"""

import json
import logging
import os
import subprocess
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContainerConfig:
    """Configuration for a container."""
    image: str
    name: str | None = None
    command: list[str] | None = None
    entrypoint: list[str] | None = None
    environment: dict[str, str] = field(default_factory=dict)
    volumes: dict[str, str] = field(default_factory=dict)  # host:container
    ports: dict[int, int] = field(default_factory=dict)    # container:host
    labels: dict[str, str] = field(default_factory=dict)
    network: str | None = None
    working_dir: str | None = None
    user: str | None = None
    memory_limit: str | None = None  # e.g., "512m"
    cpu_limit: float | None = None   # e.g., 0.5
    restart_policy: str = "no"          # no, always, unless-stopped, on-failure

    def to_run_args(self) -> list[str]:
        """Convert config to docker run arguments."""
        args = []

        if self.name:
            args.extend(["--name", self.name])

        for key, value in self.environment.items():
            args.extend(["-e", f"{key}={value}"])

        for host_path, container_path in self.volumes.items():
            args.extend(["-v", f"{host_path}:{container_path}"])

        for container_port, host_port in self.ports.items():
            args.extend(["-p", f"{host_port}:{container_port}"])

        for key, value in self.labels.items():
            args.extend(["--label", f"{key}={value}"])

        if self.network:
            args.extend(["--network", self.network])

        if self.working_dir:
            args.extend(["-w", self.working_dir])

        if self.user:
            args.extend(["-u", self.user])

        if self.memory_limit:
            args.extend(["--memory", self.memory_limit])

        if self.cpu_limit:
            args.extend(["--cpus", str(self.cpu_limit)])

        args.extend(["--restart", self.restart_policy])

        if self.entrypoint:
            args.extend(["--entrypoint", self.entrypoint[0]])

        args.append(self.image)

        if self.command:
            args.extend(self.command)

        return args


@dataclass
class ImageInfo:
    """Information about a Docker image."""
    id: str
    repository: str
    tag: str
    created: str
    size: str

    @property
    def full_name(self) -> str:
        """Execute Full Name operations natively."""
        return f"{self.repository}:{self.tag}"


@dataclass
class ContainerInfo:
    """Information about a running container."""
    id: str
    name: str
    image: str
    status: str
    ports: dict[str, str]
    created: str

    @property
    def is_running(self) -> bool:
        """Execute Is Running operations natively."""
        return "Up" in self.status


class DockerClient:
    """Client for interacting with Docker."""

    def __init__(self, docker_path: str = "docker"):
        """Execute   Init   operations natively."""
        self.docker_path = docker_path
        self._verify_docker()

    def _verify_docker(self) -> None:
        """Verify Docker is available."""
        try:
            result = subprocess.run(
                [self.docker_path, "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError("Docker not available")
        except FileNotFoundError:
            raise RuntimeError(f"Docker not found at: {self.docker_path}")

    def _run_command(
        self,
        args: list[str],
        timeout: float | None = None,
        capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a docker command."""
        cmd = [self.docker_path] + args
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )

    def build(
        self,
        path: str = ".",
        dockerfile: str | None = None,
        tag: str | None = None,
        build_args: dict[str, str] | None = None,
        no_cache: bool = False,
        target: str | None = None,
    ) -> str:
        """Build a Docker image."""
        args = ["build"]

        if dockerfile:
            args.extend(["-f", dockerfile])

        if tag:
            args.extend(["-t", tag])

        if build_args:
            for key, value in build_args.items():
                args.extend(["--build-arg", f"{key}={value}"])

        if no_cache:
            args.append("--no-cache")

        if target:
            args.extend(["--target", target])

        args.append(path)

        result = self._run_command(args, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"Build failed: {result.stderr}")

        return result.stdout

    def run(
        self,
        config: ContainerConfig,
        detach: bool = True,
        remove: bool = False,
    ) -> str:
        """Run a container."""
        args = ["run"]

        if detach:
            args.append("-d")

        if remove:
            args.append("--rm")

        args.extend(config.to_run_args())

        result = self._run_command(args)
        if result.returncode != 0:
            raise RuntimeError(f"Run failed: {result.stderr}")

        return result.stdout.strip()

    def stop(self, container_id: str, timeout: int = 10) -> None:
        """Stop a container."""
        result = self._run_command(["stop", "-t", str(timeout), container_id])
        if result.returncode != 0:
            raise RuntimeError(f"Stop failed: {result.stderr}")

    def remove(self, container_id: str, force: bool = False) -> None:
        """Remove a container."""
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container_id)

        result = self._run_command(args)
        if result.returncode != 0:
            raise RuntimeError(f"Remove failed: {result.stderr}")

    def logs(
        self,
        container_id: str,
        follow: bool = False,
        tail: int | None = None,
    ) -> Iterator[str]:
        """Get container logs."""
        args = ["logs"]

        if tail:
            args.extend(["--tail", str(tail)])

        args.append(container_id)

        if follow:
            process = subprocess.Popen(
                [self.docker_path] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in process.stdout:
                yield line.rstrip()
        else:
            result = self._run_command(args)
            for line in result.stdout.split('\n'):
                if line:
                    yield line

    def exec(
        self,
        container_id: str,
        command: list[str],
        interactive: bool = False,
        user: str | None = None,
        workdir: str | None = None,
    ) -> str:
        """Execute a command in a running container."""
        args = ["exec"]

        if interactive:
            args.extend(["-i", "-t"])

        if user:
            args.extend(["-u", user])

        if workdir:
            args.extend(["-w", workdir])

        args.append(container_id)
        args.extend(command)

        result = self._run_command(args)
        if result.returncode != 0:
            raise RuntimeError(f"Exec failed: {result.stderr}")

        return result.stdout

    def list_containers(
        self,
        all_containers: bool = False,
        filters: dict[str, str] | None = None,
    ) -> list[ContainerInfo]:
        """List containers."""
        args = ["ps", "--format", "{{json .}}"]

        if all_containers:
            args.append("-a")

        if filters:
            for key, value in filters.items():
                args.extend(["--filter", f"{key}={value}"])

        result = self._run_command(args)

        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                containers.append(ContainerInfo(
                    id=data.get("ID", ""),
                    name=data.get("Names", ""),
                    image=data.get("Image", ""),
                    status=data.get("Status", ""),
                    ports=self._parse_ports(data.get("Ports", "")),
                    created=data.get("CreatedAt", ""),
                ))

        return containers

    def _parse_ports(self, ports_str: str) -> dict[str, str]:
        """Parse port mapping string."""
        ports = {}
        if ports_str:
            for mapping in ports_str.split(","):
                if "->" in mapping:
                    parts = mapping.strip().split("->")
                    ports[parts[0]] = parts[1]
        return ports

    def list_images(
        self,
        repository: str | None = None,
    ) -> list[ImageInfo]:
        """List Docker images."""
        args = ["images", "--format", "{{json .}}"]

        if repository:
            args.append(repository)

        result = self._run_command(args)

        images = []
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                images.append(ImageInfo(
                    id=data.get("ID", ""),
                    repository=data.get("Repository", ""),
                    tag=data.get("Tag", ""),
                    created=data.get("CreatedAt", ""),
                    size=data.get("Size", ""),
                ))

        return images

    def pull(self, image: str) -> None:
        """Pull an image from a registry."""
        result = self._run_command(["pull", image], timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Pull failed: {result.stderr}")

    def push(self, image: str) -> None:
        """Push an image to a registry."""
        result = self._run_command(["push", image], timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Push failed: {result.stderr}")

    def tag(self, source: str, target: str) -> None:
        """Tag an image."""
        result = self._run_command(["tag", source, target])
        if result.returncode != 0:
            raise RuntimeError(f"Tag failed: {result.stderr}")


class DockerComposeClient:
    """Client for Docker Compose operations."""

    def __init__(self, compose_file: str = "docker-compose.yml"):
        """Execute   Init   operations natively."""
        self.compose_file = compose_file

    def _run_compose(
        self,
        args: list[str],
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess:
        """Run a docker-compose command."""
        cmd = ["docker", "compose", "-f", self.compose_file] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def up(
        self,
        services: list[str] | None = None,
        detach: bool = True,
        build: bool = False,
    ) -> None:
        """Start services."""
        args = ["up"]

        if detach:
            args.append("-d")

        if build:
            args.append("--build")

        if services:
            args.extend(services)

        result = self._run_compose(args, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Up failed: {result.stderr}")

    def down(
        self,
        volumes: bool = False,
        remove_orphans: bool = False,
    ) -> None:
        """Stop and remove services."""
        args = ["down"]

        if volumes:
            args.append("-v")

        if remove_orphans:
            args.append("--remove-orphans")

        result = self._run_compose(args)
        if result.returncode != 0:
            raise RuntimeError(f"Down failed: {result.stderr}")

    def ps(self) -> list[dict[str, str]]:
        """List running services."""
        result = self._run_compose(["ps", "--format", "json"])
        if result.returncode != 0:
            return []

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse docker-compose ps output: %s", e)
            return []


__all__ = [
    "ContainerConfig",
    "ImageInfo",
    "ContainerInfo",
    "DockerClient",
    "DockerComposeClient",
]
