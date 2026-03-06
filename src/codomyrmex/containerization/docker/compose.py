"""DockerComposeClient for managing multi-container applications."""

import json
import subprocess

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class DockerComposeClient:
    """Client for Docker Compose operations."""

    def __init__(self, compose_file: str = "docker-compose.yml") -> None:
        self.compose_file = compose_file

    def _run_compose(
        self, args: list[str], timeout: float | None = None
    ) -> subprocess.CompletedProcess:
        cmd = ["docker", "compose", "-f", self.compose_file, *args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    def up(
        self,
        services: list[str] | None = None,
        detach: bool = True,
        build: bool = False,
    ) -> None:
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

    def down(self, volumes: bool = False, remove_orphans: bool = False) -> None:
        args = ["down"]
        if volumes:
            args.append("-v")
        if remove_orphans:
            args.append("--remove-orphans")
        result = self._run_compose(args)
        if result.returncode != 0:
            raise RuntimeError(f"Down failed: {result.stderr}")

    def ps(self) -> list[dict[str, str]]:
        result = self._run_compose(["ps", "--format", "json"])
        if result.returncode != 0:
            return []
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse docker-compose ps output: %s", e)
            return []
