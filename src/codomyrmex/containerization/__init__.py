"""
Containerization Module for Codomyrmex.

The Containerization module provides container management,
orchestration, and deployment capabilities for the Codomyrmex ecosystem.
"""

# Shared schemas for cross-module interop
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

# Submodule exports - import first
try:
    from . import docker, kubernetes, registry, security
except ImportError:
    docker = kubernetes = registry = security = None  # type: ignore

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .registry.container_registry import (
        ContainerRegistry,
        manage_container_registry,
    )

    HAS_REGISTRY = True
except ImportError:
    HAS_REGISTRY = False

try:
    from .docker.docker_manager import (
        ContainerConfig,
        DockerManager,
        build_containers,
        manage_containers,
    )

    HAS_DOCKER_MANAGER = True
except ImportError:
    HAS_DOCKER_MANAGER = False

try:
    from .kubernetes.kubernetes_orchestrator import (
        KubernetesDeployment,
        KubernetesOrchestrator,
        orchestrate_kubernetes,
    )

    HAS_K8S = True
except ImportError:
    HAS_K8S = False

try:
    from .security.performance_optimizer import (
        ContainerMetrics,
        ContainerOptimizer,
        optimize_containers,
    )

    HAS_OPTIMIZER = True
except ImportError:
    HAS_OPTIMIZER = False

try:
    from .security.security_scanner import (
        ContainerSecurityScanner,
        SecurityScanResult,
        scan_container_security,
    )

    HAS_SCANNER = True
except ImportError:
    HAS_SCANNER = False

try:
    from .exceptions import (
        ContainerError,
        ImageBuildError,
        KubernetesError,
        NetworkError,
        RegistryError,
        VolumeError,
    )

    HAS_EXCEPTIONS = True
except ImportError:
    HAS_EXCEPTIONS = False


def cli_commands():
    """Return CLI commands for the containerization module."""
    return {
        "images": {
            "help": "list container images",
            "handler": lambda **kwargs: print(
                "Container Images:\n"
                + (
                    "\n".join(
                        f"  - {img}" for img in ["codomyrmex:latest", "codomyrmex:dev"]
                    )
                    if HAS_DOCKER_MANAGER
                    else "  (no Docker manager available)"
                )
            ),
        },
        "status": {
            "help": "Show container runtime status",
            "handler": lambda **kwargs: print(
                "Container Status:\n"
                f"  Docker     : {'available' if HAS_DOCKER_MANAGER else 'not available'}\n"
                f"  Kubernetes : {'available' if HAS_K8S else 'not available'}\n"
                f"  Registry   : {'available' if HAS_REGISTRY else 'not available'}"
            ),
        },
    }


__all__ = [
    # CLI integration
    "cli_commands",
    "docker",
    "kubernetes",
    "registry",
    "security",
]

if HAS_DOCKER_MANAGER:
    __all__.extend(
        ["ContainerConfig", "DockerManager", "build_containers", "manage_containers"]
    )
if HAS_REGISTRY:
    __all__.extend(["ContainerRegistry", "manage_container_registry"])
if HAS_K8S:
    __all__.extend(
        ["KubernetesDeployment", "KubernetesOrchestrator", "orchestrate_kubernetes"]
    )
if HAS_SCANNER:
    __all__.extend(
        ["ContainerSecurityScanner", "SecurityScanResult", "scan_container_security"]
    )
if HAS_OPTIMIZER:
    __all__.extend(["ContainerMetrics", "ContainerOptimizer", "optimize_containers"])
if HAS_EXCEPTIONS:
    __all__.extend(
        [
            "ContainerError",
            "ImageBuildError",
            "KubernetesError",
            "NetworkError",
            "RegistryError",
            "VolumeError",
        ]
    )

__version__ = "0.1.0"
