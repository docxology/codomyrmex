"""
Docker submodule for containerization.

Provides Docker container and image management.
"""

from .docker_manager import DockerManager
from .build_generator import DockerfileGenerator, generate_dockerfile
from .image_optimizer import ImageOptimizer, optimize_image

__all__ = [
    "DockerManager",
    "DockerfileGenerator",
    "generate_dockerfile",
    "ImageOptimizer",
    "optimize_image",
]
