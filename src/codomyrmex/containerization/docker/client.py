"""DockerClient for interacting with Docker daemon."""

import json
import subprocess
from collections.abc import Iterator

from codomyrmex.logging_monitoring import get_logger

from .models import ContainerConfig, ContainerInfo, ImageInfo

logger = get_logger(__name__)


class DockerClient:
    """Client for interacting with Docker."""

    def __init__(self, docker_path: str = "docker") -> None:
        self.docker_path = docker_path
        self._verify_docker()

    def _verify_docker(self) -> None:
        try:
            result = subprocess.run(
                [self.docker_path, "version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError("Docker not available")
        except FileNotFoundError:
            raise RuntimeError(f"Docker not found at: {self.docker_path}") from None

    def _run_command(
        self, args: list[str], timeout: float | None = None, capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            [self.docker_path, *args], capture_output=capture_output, text=True, timeout=timeout
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

    def run(self, config: ContainerConfig, detach: bool = True, remove: bool = False) -> str:
        args = ["run"]
        if detach:
            args.append("-d")
        if remove:
            args.append("--rm")
        args.extend(config.to_run_args())
        result = self._run_command(args, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Run failed: {result.stderr}")
        return result.stdout.strip()

    def stop(self, container_id: str, timeout: int = 10) -> None:
        result = self._run_command(["stop", "-t", str(timeout), container_id])
        if result.returncode != 0:
            raise RuntimeError(f"Stop failed: {result.stderr}")

    def remove(self, container_id: str, force: bool = False) -> None:
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container_id)
        result = self._run_command(args)
        if result.returncode != 0:
            raise RuntimeError(f"Remove failed: {result.stderr}")

    def logs(self, container_id: str, follow: bool = False, tail: int | None = None) -> Iterator[str]:
        args = ["logs"]
        if tail:
            args.extend(["--tail", str(tail)])
        args.append(container_id)
        if follow:
            process = subprocess.Popen(
                [self.docker_path, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for line in process.stdout:
                yield line.rstrip()
        else:
            result = self._run_command(args)
            for line in result.stdout.split("\n"):
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

    def _parse_ports(self, ports_str: str) -> dict[str, str]:
        ports: dict[str, str] = {}
        if ports_str:
            for mapping in ports_str.split(","):
                if "->" in mapping:
                    parts = mapping.strip().split("->")
                    ports[parts[0]] = parts[1]
        return ports

    def list_containers(
        self, all_containers: bool = False, filters: dict[str, str] | None = None
    ) -> list[ContainerInfo]:
        args = ["ps", "--format", "{{json .}}"]
        if all_containers:
            args.append("-a")
        if filters:
            for key, value in filters.items():
                args.extend(["--filter", f"{key}={value}"])
        result = self._run_command(args)
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                data = json.loads(line)
                containers.append(
                    ContainerInfo(
                        id=data.get("ID", ""),
                        name=data.get("Names", ""),
                        image=data.get("Image", ""),
                        status=data.get("Status", ""),
                        ports=self._parse_ports(data.get("Ports", "")),
                        created=data.get("CreatedAt", ""),
                    )
                )
        return containers

    def list_images(self, repository: str | None = None) -> list[ImageInfo]:
        args = ["images", "--format", "{{json .}}"]
        if repository:
            args.append(repository)
        result = self._run_command(args)
        images = []
        for line in result.stdout.strip().split("\n"):
            if line:
                data = json.loads(line)
                images.append(
                    ImageInfo(
                        id=data.get("ID", ""),
                        repository=data.get("Repository", ""),
                        tag=data.get("Tag", ""),
                        created=data.get("CreatedAt", ""),
                        size=data.get("Size", ""),
                    )
                )
        return images

    def pull(self, image: str) -> None:
        result = self._run_command(["pull", image], timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Pull failed: {result.stderr}")

    def push(self, image: str) -> None:
        result = self._run_command(["push", image], timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Push failed: {result.stderr}")

    def tag(self, source: str, target: str) -> None:
        result = self._run_command(["tag", source, target])
        if result.returncode != 0:
            raise RuntimeError(f"Tag failed: {result.stderr}")
