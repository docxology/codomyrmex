"""Docker container and image data models."""

from dataclasses import dataclass, field


@dataclass
class ContainerConfig:
    """Configuration for a container."""

    image: str
    name: str | None = None
    command: list[str] | None = None
    entrypoint: list[str] | None = None
    environment: dict[str, str] = field(default_factory=dict)
    volumes: dict[str, str] = field(default_factory=dict)
    ports: dict[int, int] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    network: str | None = None
    working_dir: str | None = None
    user: str | None = None
    memory_limit: str | None = None
    cpu_limit: float | None = None
    restart_policy: str = "no"

    def to_run_args(self) -> list[str]:
        """Convert config to docker run arguments."""
        args: list[str] = []
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
        return "Up" in self.status
