import logging
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""Build Generator for Codomyrmex Containerization."""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

@dataclass
class BuildStage:
    """Represents a single build stage in a multi-stage build."""
    name: str
    base_image: str
    commands: list[str] = field(default_factory=list)
    copy_commands: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    working_directory: str | None = None
    user: str | None = None

    def to_dockerfile(self) -> str:
        """Convert stage to Dockerfile instructions."""
        lines = [f"FROM {self.base_image} AS {self.name}"]

        for cmd in self.commands:
            lines.append(cmd)

        for copy_cmd in self.copy_commands:
            lines.append(copy_cmd)

        for key, value in self.environment.items():
            lines.append(f"ENV {key}={value}")

        if self.working_directory:
            lines.append(f"WORKDIR {self.working_directory}")

        if self.user:
            lines.append(f"USER {self.user}")

        for key, value in self.labels.items():
            lines.append(f"LABEL {key}={value}")

        return "\n".join(lines)

@dataclass
class MultiStageBuild:
    """Represents a complete multi-stage Docker build."""
    stages: list[BuildStage] = field(default_factory=list)
    final_stage: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dockerfile(self) -> str:
        """Convert multi-stage build to complete Dockerfile."""
        lines = []

        # Add header comment
        lines.append("# Auto-generated multi-stage Dockerfile")
        lines.append(f"# Generated for: {self.metadata.get('project_name', 'unknown')}")
        lines.append("")

        # Add all stages
        for i, stage in enumerate(self.stages):
            lines.append(stage.to_dockerfile())
            if i < len(self.stages) - 1:
                lines.append("")

        # Set final stage if specified
        if self.final_stage and self.final_stage != self.stages[-1].name:
            lines.append(f"\nFROM {self.final_stage}")

        return "\n".join(lines)

@dataclass
class BuildScript:
    """Represents a build script for containerization."""
    name: str
    dockerfile_path: str
    context_path: str
    build_args: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    push_targets: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    def to_shell_script(self) -> str:
        """Convert to shell script."""
        lines = ["#!/bin/bash", "", f"# Build script for {self.name}", ""]

        # Build commands
        for tag in self.tags:
            build_cmd = f"docker build -f {self.dockerfile_path} -t {tag}"
            if self.build_args:
                args_str = " ".join(f"--build-arg {k}={v}" for k, v in self.build_args.items())
                build_cmd += f" {args_str}"
            build_cmd += f" {self.context_path}"
            lines.append(build_cmd)

        # Push commands
        if self.push_targets:
            lines.append("")
            for target in self.push_targets:
                lines.append(f"docker push {target}")

        return "\n".join(lines)

class BuildGenerator:
    """
    Advanced Dockerfile and build script generator.

    Provides intelligent generation of Dockerfiles with multi-stage builds,
    security hardening, performance optimization, and build script generation.
    """

    def __init__(self):
        """Initialize the build generator."""
        self.templates = self._load_templates()

    def create_multi_stage_build(self, config: dict[str, Any]) -> MultiStageBuild:
        """
        Create a multi-stage build configuration.

        Args:
            config: Build configuration dictionary

        Returns:
            MultiStageBuild configuration
        """
        build = MultiStageBuild()
        build.metadata = config.get("metadata", {})

        # Determine build type and create appropriate stages
        build_type = config.get("build_type", "application")

        if build_type == "python":
            build = self._create_python_multi_stage_build(config)
        elif build_type == "node":
            build = self._create_node_multi_stage_build(config)
        elif build_type == "java":
            build = self._create_java_multi_stage_build(config)
        elif build_type == "go":
            build = self._create_go_multi_stage_build(config)
        else:
            build = self._create_generic_multi_stage_build(config)

        return build

    def optimize_dockerfile(self, dockerfile_path: str) -> str:
        """
        Optimize an existing Dockerfile.

        Args:
            dockerfile_path: Path to existing Dockerfile

        Returns:
            Optimized Dockerfile content
        """
        try:
            with open(dockerfile_path) as f:
                content = f.read()

            lines = content.split('\n')
            optimized_lines = []

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Combine RUN commands where possible
                if line.startswith('RUN ') and i + 1 < len(lines):
                    combined_commands = [line]
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith('RUN '):
                        combined_commands.append(lines[j].strip()[4:])  # Remove 'RUN '
                        j += 1

                    if len(combined_commands) > 1:
                        # Combine with &&
                        combined = 'RUN ' + ' && '.join(cmd[4:] for cmd in combined_commands)
                        optimized_lines.append(combined)
                        i = j
                        continue

                # Add cache cleaning for apt
                if line.startswith('RUN ') and 'apt-get install' in line and 'rm -rf /var/lib/apt/lists/*' not in line:
                    optimized_lines.append(line + ' && rm -rf /var/lib/apt/lists/*')
                elif line.startswith('RUN ') and 'pip install' in line and '--no-cache-dir' not in line:
                    # Add --no-cache-dir to pip installs
                    if 'pip install' in line and '--no-cache-dir' not in line:
                        optimized_lines.append(line + ' --no-cache-dir')
                    else:
                        optimized_lines.append(line)
                else:
                    optimized_lines.append(line)

                i += 1

            return '\n'.join(optimized_lines)

        except Exception as e:
            logger.error(f"Error optimizing Dockerfile {dockerfile_path}: {e}")
            raise

    def generate_build_script(self, config: dict[str, Any]) -> BuildScript:
        """
        Generate a build script from configuration.

        Args:
            config: Build script configuration

        Returns:
            BuildScript instance
        """
        script = BuildScript(
            name=config.get("name", "build"),
            dockerfile_path=config.get("dockerfile", "Dockerfile"),
            context_path=config.get("context", "."),
            build_args=config.get("build_args", {}),
            tags=config.get("tags", []),
            push_targets=config.get("push_targets", []),
            dependencies=config.get("dependencies", [])
        )

        return script

    def validate_dockerfile(self, dockerfile_content: str) -> tuple[bool, list[str]]:
        """
        Validate Dockerfile content for common issues.

        Args:
            dockerfile_content: Dockerfile content to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        lines = dockerfile_content.split('\n')

        has_from = False
        has_user = False
        has_workdir = False

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            # Check for FROM instruction
            if line.upper().startswith('FROM '):
                has_from = True

                # Check for latest tag
                if ':latest' in line or ':' not in line:
                    issues.append(f"Line {line_num}: Avoid using 'latest' tag for reproducible builds")

            # Check for root user
            if line.upper().startswith('USER '):
                has_user = True
                if 'root' in line.lower():
                    issues.append(f"Line {line_num}: Avoid running as root user for security")

            # Check for WORKDIR
            if line.upper().startswith('WORKDIR '):
                has_workdir = True

            # Check for security issues
            if 'chmod 777' in line or 'chmod +x' in line:
                issues.append(f"Line {line_num}: Overly permissive file permissions")

            if 'password' in line.lower() and 'env' in line.lower():
                issues.append(f"Line {line_num}: Avoid hardcoding passwords in environment variables")

        # Required instructions
        if not has_from:
            issues.append("Missing FROM instruction")
        if not has_user:
            issues.append("Consider adding non-root USER instruction for security")

        return len(issues) == 0, issues

    def _create_python_multi_stage_build(self, config: dict[str, Any]) -> MultiStageBuild:
        """Create multi-stage build for Python applications."""
        build = MultiStageBuild()
        build.metadata = config.get("metadata", {})

        # Build stage
        build_stage = BuildStage(
            name="builder",
            base_image=config.get("base_image", "python:3.9-slim"),
            commands=[
                "RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*",
                "WORKDIR /app",
                "COPY requirements*.txt ./",
                "RUN pip install --no-cache-dir -r requirements.txt"
            ],
            copy_commands=[
                "COPY . ."
            ],
            environment={"PYTHONUNBUFFERED": "1"}
        )

        # Runtime stage
        runtime_stage = BuildStage(
            name="runtime",
            base_image="python:3.9-slim",
            commands=[
                "RUN useradd -m appuser",
                "WORKDIR /app"
            ],
            copy_commands=[
                "COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages",
                "COPY --from=builder /app ."
            ],
            environment={"PYTHONUNBUFFERED": "1"},
            user="appuser"
        )

        build.stages = [build_stage, runtime_stage]
        build.final_stage = "runtime"

        return build

    def _create_node_multi_stage_build(self, config: dict[str, Any]) -> MultiStageBuild:
        """Create multi-stage build for Node.js applications."""
        build = MultiStageBuild()
        build.metadata = config.get("metadata", {})

        # Build stage
        build_stage = BuildStage(
            name="builder",
            base_image=config.get("base_image", "node:18-alpine"),
            commands=[
                "WORKDIR /app",
                "COPY package*.json ./",
                "RUN npm ci --only=production"
            ],
            copy_commands=[
                "COPY . .",
                "RUN npm run build"
            ]
        )

        # Runtime stage
        runtime_stage = BuildStage(
            name="runtime",
            base_image="node:18-alpine",
            commands=[
                "RUN adduser -D appuser",
                "WORKDIR /app"
            ],
            copy_commands=[
                "COPY --from=builder /app/package*.json ./",
                "COPY --from=builder /app/node_modules ./node_modules",
                "COPY --from=builder /app/dist ./dist"
            ],
            environment={"NODE_ENV": "production"},
            user="appuser"
        )

        build.stages = [build_stage, runtime_stage]
        build.final_stage = "runtime"

        return build

    def _create_java_multi_stage_build(self, config: dict[str, Any]) -> MultiStageBuild:
        """Create multi-stage build for Java applications."""
        build = MultiStageBuild()
        build.metadata = config.get("metadata", {})

        # Build stage
        build_stage = BuildStage(
            name="builder",
            base_image=config.get("base_image", "openjdk:11-jdk-slim"),
            commands=[
                "WORKDIR /app",
                "COPY pom.xml .",
                "COPY src ./src"
            ],
            copy_commands=[
                "RUN ./mvnw clean package -DskipTests"
            ]
        )

        # Runtime stage
        runtime_stage = BuildStage(
            name="runtime",
            base_image="openjdk:11-jre-slim",
            commands=[
                "RUN useradd -m appuser",
                "WORKDIR /app"
            ],
            copy_commands=[
                "COPY --from=builder /app/target/*.jar ./app.jar"
            ],
            user="appuser"
        )

        build.stages = [build_stage, runtime_stage]
        build.final_stage = "runtime"

        return build

    def _create_go_multi_stage_build(self, config: dict[str, Any]) -> MultiStageBuild:
        """Create multi-stage build for Go applications."""
        build = MultiStageBuild()
        build.metadata = config.get("metadata", {})

        # Build stage
        build_stage = BuildStage(
            name="builder",
            base_image=config.get("base_image", "golang:1.19-alpine"),
            commands=[
                "WORKDIR /app",
                "COPY go.mod go.sum ./",
                "RUN go mod download"
            ],
            copy_commands=[
                "COPY . .",
                "RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ."
            ]
        )

        # Runtime stage
        runtime_stage = BuildStage(
            name="runtime",
            base_image="alpine:latest",
            commands=[
                "RUN adduser -D appuser",
                "WORKDIR /app"
            ],
            copy_commands=[
                "COPY --from=builder /app/main ."
            ],
            user="appuser"
        )

        build.stages = [build_stage, runtime_stage]
        build.final_stage = "runtime"

        return build

    def _create_generic_multi_stage_build(self, config: dict[str, Any]) -> MultiStageBuild:
        """Create generic multi-stage build."""
        build = MultiStageBuild()
        build.metadata = config.get("metadata", {})

        # Build stage
        build_stage = BuildStage(
            name="builder",
            base_image=config.get("base_image", "ubuntu:20.04"),
            commands=config.get("build_commands", []),
            copy_commands=["COPY . /app"],
            working_directory="/app"
        )

        # Runtime stage
        runtime_stage = BuildStage(
            name="runtime",
            base_image=config.get("runtime_base_image", "ubuntu:20.04"),
            commands=config.get("runtime_commands", []),
            copy_commands=["COPY --from=builder /app /app"],
            working_directory="/app",
            user="appuser"
        )

        build.stages = [build_stage, runtime_stage]
        build.final_stage = "runtime"

        return build

    def _load_templates(self) -> dict[str, str]:
        """Load Dockerfile templates."""
        templates = {
            "python_basic": """FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]""",

            "node_basic": """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["npm", "start"]""",

            "security_hardened": """FROM base_image
RUN useradd -m appuser && \\
    apt-get update && \\
    apt-get install -y --no-install-recommends packages && \\
    rm -rf /var/lib/apt/lists/*
USER appuser
WORKDIR /app"""
        }

        return templates
