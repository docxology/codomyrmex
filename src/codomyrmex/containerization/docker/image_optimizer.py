import logging
import re
from dataclasses import dataclass, field
from typing import Any

import docker

from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""Image Optimizer for Codomyrmex Containerization."""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# Import Docker client
try:
    HAS_DOCKER = True
except ImportError:
    docker = None
    HAS_DOCKER = False

@dataclass
class ImageAnalysis:
    """Analysis results for a Docker image."""
    image_name: str
    size_bytes: int
    layers: list[dict[str, Any]]
    base_image: str
    exposed_ports: list[str]
    volumes: list[str]
    environment_vars: list[str]
    commands: list[str]
    potential_optimizations: list[str] = field(default_factory=list)
    optimization_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "image_name": self.image_name,
            "size_mb": self.size_bytes / (1024 * 1024),
            "layers_count": len(self.layers),
            "base_image": self.base_image,
            "exposed_ports": self.exposed_ports,
            "volumes": self.volumes,
            "environment_vars": self.environment_vars,
            "commands": self.commands,
            "potential_optimizations": self.potential_optimizations,
            "optimization_score": self.optimization_score
        }

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

class ImageOptimizer:
    """
    Docker image optimizer with comprehensive analysis and optimization capabilities.

    Provides intelligent image analysis, optimization suggestions, and automated
    Dockerfile improvements for better image efficiency and security.
    """

    def __init__(self):
        """Initialize the image optimizer."""
        self.client = docker.from_env() if HAS_DOCKER else None
        if not HAS_DOCKER:
            logger.warning("Docker library not available, image optimization features will be limited")

    def analyze_image(self, image_name: str) -> ImageAnalysis:
        """
        Analyze a Docker image for optimization opportunities.

        Args:
            image_name: Name of the Docker image to analyze

        Returns:
            ImageAnalysis with detailed image information and optimization suggestions
        """
        if not self.client:
            raise RuntimeError("Docker client not available")

        try:
            # Get image information
            image = self.client.images.get(image_name)
            image_attrs = image.attrs

            # Extract basic information
            size_bytes = image_attrs.get("Size", 0)
            layers = image_attrs.get("RootFS", {}).get("Layers", [])
            config = image_attrs.get("Config", {})

            # Extract configuration details
            exposed_ports = list(config.get("ExposedPorts", {}).keys())
            volumes = list(config.get("Volumes", {}).keys()) if config.get("Volumes") else []
            environment_vars = config.get("Env", [])
            commands = config.get("Cmd", [])

            # Try to determine base image (this is approximate)
            base_image = self._extract_base_image(image_attrs)

            analysis = ImageAnalysis(
                image_name=image_name,
                size_bytes=size_bytes,
                layers=[{"digest": layer, "size": 0} for layer in layers],  # Size info limited
                base_image=base_image,
                exposed_ports=exposed_ports,
                volumes=volumes,
                environment_vars=environment_vars,
                commands=commands
            )

            # Generate optimization suggestions
            analysis.potential_optimizations = self._analyze_optimizations(analysis)
            analysis.optimization_score = self._calculate_optimization_score(analysis)

            return analysis

        except docker.errors.ImageNotFound:
            raise ValueError(f"Image '{image_name}' not found")
        except Exception as e:
            logger.error(f"Error analyzing image {image_name}: {e}")
            raise

    def optimize_image(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Optimize an image configuration.

        Args:
            config: Image configuration dictionary

        Returns:
            Optimized configuration with improvements
        """
        optimized = config.copy()

        # Apply various optimizations
        optimized = self._optimize_base_image(optimized)
        optimized = self._optimize_package_management(optimized)
        optimized = self._optimize_layer_caching(optimized)
        optimized = self._optimize_security(optimized)
        optimized = self._optimize_size(optimized)

        return optimized

    def suggest_optimizations(self, image_name: str) -> list[OptimizationSuggestion]:
        """
        Generate specific optimization suggestions for an image.

        Args:
            image_name: Name of the image to analyze

        Returns:
            List of optimization suggestions
        """
        try:
            analysis = self.analyze_image(image_name)
            return self._generate_suggestions(analysis)
        except Exception as e:
            logger.error(f"Error generating suggestions for {image_name}: {e}")
            return []

    def compare_images(self, image1: str, image2: str) -> dict[str, Any]:
        """
        Compare two images and provide detailed comparison.

        Args:
            image1: First image name
            image2: Second image name

        Returns:
            Comparison results
        """
        try:
            analysis1 = self.analyze_image(image1)
            analysis2 = self.analyze_image(image2)

            comparison = {
                "image1": analysis1.to_dict(),
                "image2": analysis2.to_dict(),
                "size_difference_mb": (analysis2.size_bytes - analysis1.size_bytes) / (1024 * 1024),
                "size_reduction_percentage": (
                    (analysis1.size_bytes - analysis2.size_bytes) / analysis1.size_bytes * 100
                    if analysis1.size_bytes > 0 else 0
                ),
                "recommendations": []
            }

            # Generate comparison-based recommendations
            if analysis2.size_bytes < analysis1.size_bytes:
                comparison["recommendations"].append(
                    f"Image '{image2}' is {comparison['size_difference_mb']:.1f}MB smaller than '{image1}'"
                )

            if analysis2.optimization_score > analysis1.optimization_score:
                comparison["recommendations"].append(
                    f"Image '{image2}' has better optimization score ({analysis2.optimization_score:.1f} vs {analysis1.optimization_score:.1f})"
                )

            return comparison

        except Exception as e:
            logger.error(f"Error comparing images {image1} and {image2}: {e}")
            return {"error": str(e)}

    def get_optimization_report(self, image_name: str) -> dict[str, Any]:
        """
        Generate a comprehensive optimization report for an image.

        Args:
            image_name: Image to analyze

        Returns:
            Detailed optimization report
        """
        try:
            analysis = self.analyze_image(image_name)
            suggestions = self._generate_suggestions(analysis)

            report = {
                "image_analysis": analysis.to_dict(),
                "optimization_suggestions": [s.to_dict() for s in suggestions],
                "summary": {
                    "total_suggestions": len(suggestions),
                    "high_impact_suggestions": len([s for s in suggestions if s.impact == "high"]),
                    "easy_improvements": len([s for s in suggestions if s.effort == "easy"]),
                    "estimated_savings_mb": sum(s.size_reduction_mb or 0 for s in suggestions)
                },
                "implementation_plan": self._create_implementation_plan(suggestions)
            }

            return report

        except Exception as e:
            logger.error(f"Error generating optimization report for {image_name}: {e}")
            return {"error": str(e)}

    def _extract_base_image(self, image_attrs: dict[str, Any]) -> str:
        """Extract base image information from image attributes."""
        try:
            # Look for base image in history
            history = image_attrs.get("History", [])
            for entry in history:
                created_by = entry.get("CreatedBy", "")
                if created_by and "FROM" in created_by.upper():
                    # Extract FROM instruction
                    match = re.search(r'FROM\s+([^\s\n]+)', created_by, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
        except Exception:
            pass

        return "unknown"

    def _analyze_optimizations(self, analysis: ImageAnalysis) -> list[str]:
        """Analyze an image and return potential optimizations."""
        optimizations = []

        # Size-based optimizations
        if analysis.size_bytes > 500 * 1024 * 1024:  # > 500MB
            optimizations.append("Consider using a smaller base image")
            optimizations.append("Use multi-stage builds to reduce final image size")

        # Layer-based optimizations
        if len(analysis.layers) > 20:
            optimizations.append("Reduce number of layers by combining RUN commands")

        # Security optimizations
        if "root" in analysis.environment_vars or not analysis.environment_vars:
            optimizations.append("Create non-root user for security")

        # Package management optimizations
        optimizations.extend(self._check_package_optimizations(analysis))

        return optimizations

    def _check_package_optimizations(self, analysis: ImageAnalysis) -> list[str]:
        """Check for package management optimizations."""
        optimizations = []

        # Check for common package managers
        has_apt = any("apt" in cmd.lower() for cmd in analysis.commands)
        has_pip = any("pip" in cmd.lower() for cmd in analysis.commands)
        has_npm = any("npm" in cmd.lower() for cmd in analysis.commands)

        if has_apt:
            optimizations.append("Clean apt cache with 'rm -rf /var/lib/apt/lists/*'")
            optimizations.append("Combine apt commands to reduce layer count")

        if has_pip:
            optimizations.append("Use --no-cache-dir with pip install")
            optimizations.append("Use requirements.txt instead of individual pip installs")

        if has_npm:
            optimizations.append("Use npm ci instead of npm install for production")
            optimizations.append("Clean npm cache after installation")

        return optimizations

    def _calculate_optimization_score(self, analysis: ImageAnalysis) -> float:
        """Calculate an optimization score (0-100) for the image."""
        score = 100.0

        # Size penalties
        if analysis.size_bytes > 1000 * 1024 * 1024:  # > 1GB
            score -= 30
        elif analysis.size_bytes > 500 * 1024 * 1024:  # > 500MB
            score -= 15

        # Layer penalties
        if len(analysis.layers) > 30:
            score -= 20
        elif len(analysis.layers) > 15:
            score -= 10

        # Security bonus
        if analysis.environment_vars and "USER" in str(analysis.environment_vars):
            score += 10

        # Package management bonus
        has_good_practices = (
            any("rm -rf /var/lib/apt/lists/*" in cmd for cmd in analysis.commands) or
            any("--no-cache-dir" in cmd for cmd in analysis.commands) or
            any("npm ci" in cmd for cmd in analysis.commands)
        )
        if has_good_practices:
            score += 15

        return max(0.0, min(100.0, score))

    def _generate_suggestions(self, analysis: ImageAnalysis) -> list[OptimizationSuggestion]:
        """Generate detailed optimization suggestions."""
        suggestions = []

        # Size-based suggestions
        if analysis.size_bytes > 500 * 1024 * 1024:
            suggestions.append(OptimizationSuggestion(
                category="size",
                description="Use multi-stage build to reduce final image size",
                impact="high",
                effort="medium",
                dockerfile_changes=[
                    "# Multi-stage build example",
                    "FROM builder AS build-stage",
                    "# Build commands here",
                    "FROM runtime-image AS production",
                    "COPY --from=build-stage /app/build /app"
                ],
                size_reduction_mb=analysis.size_bytes * 0.3 / (1024 * 1024)  # Estimate 30% reduction
            ))

        # Layer optimization
        if len(analysis.layers) > 15:
            suggestions.append(OptimizationSuggestion(
                category="layers",
                description="Combine RUN commands to reduce layer count",
                impact="medium",
                effort="easy",
                dockerfile_changes=[
                    "# Instead of multiple RUN commands:",
                    "# RUN apt-get update",
                    "# RUN apt-get install -y package1",
                    "# RUN apt-get install -y package2",
                    "# Use:",
                    "# RUN apt-get update && apt-get install -y package1 package2"
                ]
            ))

        # Package manager optimizations
        if any("apt" in str(analysis.commands).lower()):
            suggestions.append(OptimizationSuggestion(
                category="packages",
                description="Clean apt cache to reduce image size",
                impact="medium",
                effort="easy",
                dockerfile_changes=[
                    "RUN apt-get update && apt-get install -y packages && rm -rf /var/lib/apt/lists/*"
                ],
                size_reduction_mb=50.0  # Estimate 50MB reduction
            ))

        if any("pip" in str(analysis.commands).lower()):
            suggestions.append(OptimizationSuggestion(
                category="packages",
                description="Use pip --no-cache-dir to avoid cache in image",
                impact="low",
                effort="easy",
                dockerfile_changes=[
                    "RUN pip install --no-cache-dir -r requirements.txt"
                ],
                size_reduction_mb=20.0  # Estimate 20MB reduction
            ))

        # Security suggestions
        if not any("USER" in str(analysis.environment_vars).upper()):
            suggestions.append(OptimizationSuggestion(
                category="security",
                description="Create non-root user for better security",
                impact="high",
                effort="easy",
                dockerfile_changes=[
                    "RUN useradd -m appuser",
                    "USER appuser"
                ]
            ))

        return suggestions

    def _optimize_base_image(self, config: dict[str, Any]) -> dict[str, Any]:
        """Optimize base image selection."""
        # Suggest smaller base images
        base_image = config.get("base_image", "").lower()

        if "python:3" in base_image and "slim" not in base_image:
            config["suggested_base_image"] = base_image.replace("python:3", "python:3-slim")
            config["optimization_notes"] = config.get("optimization_notes", [])
            config["optimization_notes"].append("Consider using python:3-slim for smaller size")

        return config

    def _optimize_package_management(self, config: dict[str, Any]) -> dict[str, Any]:
        """Optimize package management commands."""
        # Add cache cleaning for apt
        if "apt-get" in str(config.get("commands", [])):
            config["optimization_notes"] = config.get("optimization_notes", [])
            config["optimization_notes"].append("Add 'rm -rf /var/lib/apt/lists/*' after apt commands")

        return config

    def _optimize_layer_caching(self, config: dict[str, Any]) -> dict[str, Any]:
        """Optimize Docker layer caching."""
        # Suggest ordering commands for better caching
        config["optimization_notes"] = config.get("optimization_notes", [])
        config["optimization_notes"].append("Order commands to maximize layer caching (frequent changes last)")

        return config

    def _optimize_security(self, config: dict[str, Any]) -> dict[str, Any]:
        """Add security optimizations."""
        if not config.get("user"):
            config["optimization_notes"] = config.get("optimization_notes", [])
            config["optimization_notes"].append("Create non-root user for security")

        return config

    def _optimize_size(self, config: dict[str, Any]) -> dict[str, Any]:
        """Optimize for size reduction."""
        config["optimization_notes"] = config.get("optimization_notes", [])
        config["optimization_notes"].append("Use .dockerignore to exclude unnecessary files")

        return config

    def _create_implementation_plan(self, suggestions: list[OptimizationSuggestion]) -> list[dict[str, Any]]:
        """Create an implementation plan from suggestions."""
        # Sort by impact and effort
        priority_order = {"high": 3, "medium": 2, "low": 1}
        effort_order = {"easy": 3, "medium": 2, "hard": 1}

        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: (priority_order.get(s.impact, 0), effort_order.get(s.effort, 0)),
            reverse=True
        )

        plan = []
        for i, suggestion in enumerate(sorted_suggestions, 1):
            plan.append({
                "priority": i,
                "suggestion": suggestion.to_dict(),
                "implementation_order": "immediate" if suggestion.effort == "easy" else "planned"
            })

        return plan
