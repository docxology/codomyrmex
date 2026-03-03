import re
from dataclasses import dataclass, field
from typing import Any

import docker
from loguru import logger


@dataclass
class OptimizationSuggestion:
    """A specific optimization suggestion."""
    category: str
    description: str
    impact: str  # "high", "medium", "low"
    effort: str  # "easy", "medium", "hard"
    dockerfile_changes: list[str] = field(default_factory=list)
    size_reduction_mb: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "description": self.description,
            "impact": self.impact,
            "effort": self.effort,
            "dockerfile_changes": self.dockerfile_changes,
            "size_reduction_mb": self.size_reduction_mb
        }

@dataclass
class ImageAnalysis:
    """Analysis results for a Docker image."""
    image_name: str
    size_bytes: int
    layers_count: int
    base_image: str
    exposed_ports: list[str]
    volumes: list[str]
    environment_vars: list[str]
    commands: list[str]
    user: str
    potential_optimizations: list[str] = field(default_factory=list)
    optimization_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "image_name": self.image_name,
            "size_mb": self.size_bytes / (1024 * 1024),
            "layers_count": self.layers_count,
            "base_image": self.base_image,
            "exposed_ports": self.exposed_ports,
            "volumes": self.volumes,
            "environment_vars": self.environment_vars,
            "commands": self.commands,
            "user": self.user,
            "potential_optimizations": self.potential_optimizations,
            "optimization_score": self.optimization_score
        }

class ContainerOptimizer:
    """
    Docker image optimizer with comprehensive analysis and optimization capabilities.
    """

    def __init__(self, client: docker.DockerClient | None = None):
        """Initialize the image optimizer."""
        try:
            self.client = client or docker.from_env()
        except Exception as e:
            logger.warning(f"Could not connect to Docker: {e}")
            self.client = None

    def analyze_image(self, image_name: str) -> ImageAnalysis:
        """
        Analyze a Docker image for optimization opportunities.
        """
        if not self.client:
            raise RuntimeError("Docker client not available")

        try:
            image = self.client.images.get(image_name)
            attrs = image.attrs

            size_bytes = attrs.get("Size", 0)
            layers = attrs.get("RootFS", {}).get("Layers", [])
            config = attrs.get("Config", {})

            exposed_ports = list(config.get("ExposedPorts", {}).keys()) if config.get("ExposedPorts") else []
            volumes = list(config.get("Volumes", {}).keys()) if config.get("Volumes") else []
            env_vars = config.get("Env", [])
            commands = config.get("Cmd", []) or []
            user = config.get("User", "")

            base_image = self._extract_base_image(image)

            analysis = ImageAnalysis(
                image_name=image_name,
                size_bytes=size_bytes,
                layers_count=len(layers),
                base_image=base_image,
                exposed_ports=exposed_ports,
                volumes=volumes,
                environment_vars=env_vars,
                commands=commands,
                user=user
            )

            analysis.potential_optimizations = self._analyze_optimizations(analysis)
            analysis.optimization_score = self._calculate_score(analysis)

            return analysis
        except docker.errors.ImageNotFound as exc:
            raise ValueError(f"Image '{image_name}' not found") from exc
        except Exception as e:
            logger.error(f"Failed to analyze image {image_name}: {e}")
            raise

    def suggest_optimizations(self, image_name: str) -> list[OptimizationSuggestion]:
        """Generate specific optimization suggestions."""
        analysis = self.analyze_image(image_name)
        suggestions = []

        if analysis.size_bytes > 500 * 1024 * 1024:
            suggestions.append(OptimizationSuggestion(
                category="size",
                description="Large image size detected. Consider multi-stage builds.",
                impact="high",
                effort="medium",
                dockerfile_changes=["FROM builder AS build", "COPY --from=build /src /app"],
                size_reduction_mb=analysis.size_bytes * 0.4 / (1024 * 1024)
            ))

        if analysis.layers_count > 20:
            suggestions.append(OptimizationSuggestion(
                category="layers",
                description="High number of layers. Combine RUN commands.",
                impact="medium",
                effort="easy",
                dockerfile_changes=["RUN apt-get update && apt-get install -y pkg1 pkg2 && rm -rf /var/lib/apt/lists/*"]
            ))

        if not analysis.user or analysis.user == "root":
             suggestions.append(OptimizationSuggestion(
                category="security",
                description="Image likely runs as root. Use a non-root user.",
                impact="high",
                effort="easy",
                dockerfile_changes=["RUN useradd -m appuser", "USER appuser"]
            ))

        return suggestions

    def get_optimization_report(self, image_name: str) -> dict[str, Any]:
        """Generate a complete optimization report."""
        analysis = self.analyze_image(image_name)
        suggestions = self.suggest_optimizations(image_name)

        return {
            "analysis": analysis.to_dict(),
            "suggestions": [s.to_dict() for s in suggestions],
            "score": analysis.optimization_score,
            "status": "needs_improvement" if analysis.optimization_score < 80 else "optimized"
        }

    def _extract_base_image(self, image: docker.models.images.Image) -> str:
        """Extract base image from history."""
        try:
            history = image.history()
            for entry in history:
                cmd = entry.get("CreatedBy", "")
                if "FROM" in cmd.upper():
                    match = re.search(r'FROM\s+([^\s\n]+)', cmd, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
        except Exception as e:
            logger.debug(f"Failed to extract base image from history: {e}")
        return "unknown"

    def _analyze_optimizations(self, analysis: ImageAnalysis) -> list[str]:
        """
        Analyze the image and return a list of optimization suggestions.

        Args:
            analysis: The ImageAnalysis object containing details.

        Returns:
            A list of optimization description strings.
        """
        opts = []
        if analysis.size_bytes > 500 * 1024 * 1024:
            opts.append("Use multi-stage builds")
        if analysis.layers_count > 20:
            opts.append("Combine RUN commands")
        if not analysis.user or analysis.user == "root":
            opts.append("Use a non-root user")
        return opts

    def _calculate_score(self, analysis: ImageAnalysis) -> float:
        """
        Calculate an optimization score based on image analysis.

        Args:
            analysis: The ImageAnalysis object.

        Returns:
            A score between 0.0 and 100.0 representing the optimization level.
        """
        score = 100.0
        if analysis.size_bytes > 1024 * 1024 * 1024:
            score -= 30
        elif analysis.size_bytes > 500 * 1024 * 1024:
            score -= 15

        if analysis.layers_count > 30:
            score -= 20
        elif analysis.layers_count > 15:
            score -= 10

        if not analysis.user or analysis.user == "root":
            score -= 10

        return max(0.0, score)
