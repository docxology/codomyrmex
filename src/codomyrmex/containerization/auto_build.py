"""Auto-generate optimized Dockerfiles from project metadata.

Produces multi-stage Dockerfile content from pyproject.toml analysis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class DockerStage:
    """A stage in a multi-stage Dockerfile.

    Attributes:
        name: Stage name (e.g. ``builder``, ``runtime``).
        base_image: Base image for this stage.
        commands: Dockerfile commands for this stage.
    """

    name: str
    base_image: str = "python:3.12-slim"
    commands: list[str] = field(default_factory=list)

    def render(self) -> str:
        """Execute Render operations natively."""
        lines = [f"FROM {self.base_image} AS {self.name}"]
        lines.extend(self.commands)
        return "\n".join(lines)


@dataclass
class DockerfileSpec:
    """Complete Dockerfile specification.

    Attributes:
        project_name: Project name.
        python_version: Python version to use.
        stages: Dockerfile stages.
        labels: OCI labels.
    """

    project_name: str = ""
    python_version: str = "3.12"
    stages: list[DockerStage] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)

    def render(self) -> str:
        """Render the complete Dockerfile content."""
        parts = []
        for stage in self.stages:
            parts.append(stage.render())
        if self.labels:
            label_lines = [f'LABEL {k}="{v}"' for k, v in self.labels.items()]
            parts.append("\n".join(label_lines))
        return "\n\n".join(parts) + "\n"

    @property
    def stage_count(self) -> int:
        """Execute Stage Count operations natively."""
        return len(self.stages)


class AutoBuilder:
    """Auto-generate optimized Dockerfiles.

    Usage::

        builder = AutoBuilder()
        spec = builder.from_pyproject("pyproject.toml")
        print(spec.render())
    """

    def from_pyproject(self, pyproject_path: str | Path) -> DockerfileSpec:
        """Generate Dockerfile from pyproject.toml.

        Args:
            pyproject_path: Path to pyproject.toml.

        Returns:
            ``DockerfileSpec`` with multi-stage build.
        """
        path = Path(pyproject_path)
        if not path.exists():
            return self.default_spec()

        content = path.read_text()
        name = self._extract(content, "name") or "app"
        version = self._extract(content, "version") or "0.0.0"
        python_req = self._extract(content, "requires-python") or ">=3.12"

        # Determine Python version
        py_match = re.search(r"(\d+\.\d+)", python_req)
        py_version = py_match.group(1) if py_match else "3.12"

        return self._build_spec(name, version, py_version)

    def default_spec(self) -> DockerfileSpec:
        """Generate a default Dockerfile spec."""
        return self._build_spec("app", "0.0.0", "3.12")

    def from_config(
        self,
        project_name: str,
        python_version: str = "3.12",
        entrypoint: str = "main.py",
    ) -> DockerfileSpec:
        """Generate Dockerfile from explicit config."""
        return self._build_spec(project_name, "latest", python_version, entrypoint)

    def _build_spec(
        self,
        name: str,
        version: str,
        py_version: str,
        entrypoint: str = "main.py",
    ) -> DockerfileSpec:
        """Execute  Build Spec operations natively."""
        base = f"python:{py_version}-slim"

        builder = DockerStage(
            name="builder",
            base_image=base,
            commands=[
                "WORKDIR /build",
                "RUN pip install --no-cache-dir uv",
                "COPY pyproject.toml uv.lock* ./",
                "RUN uv pip install --system --no-cache -r pyproject.toml || true",
                "COPY . .",
                "RUN uv pip install --system --no-cache .",
            ],
        )

        runtime = DockerStage(
            name="runtime",
            base_image=base,
            commands=[
                "WORKDIR /app",
                "COPY --from=builder /usr/local/lib/python*/site-packages /usr/local/lib/python*/site-packages",
                "COPY --from=builder /usr/local/bin /usr/local/bin",
                "COPY --from=builder /build /app",
                "RUN useradd -r -s /bin/false appuser && chown -R appuser /app",
                "USER appuser",
                "EXPOSE 8000",
                f'ENTRYPOINT ["python", "{entrypoint}"]',
            ],
        )

        spec = DockerfileSpec(
            project_name=name,
            python_version=py_version,
            stages=[builder, runtime],
            labels={
                "org.opencontainers.image.title": name,
                "org.opencontainers.image.version": version,
            },
        )

        logger.info("Dockerfile generated", extra={"project": name, "stages": spec.stage_count})
        return spec

    @staticmethod
    def _extract(content: str, field_name: str) -> str:
        """Execute  Extract operations natively."""
        pattern = re.compile(rf'^{field_name}\s*=\s*"([^"]*)"', re.MULTILINE)
        match = pattern.search(content)
        return match.group(1) if match else ""


__all__ = ["AutoBuilder", "DockerStage", "DockerfileSpec"]
