"""
Containerization Module for Codomyrmex.

The Containerization module provides container management,
orchestration, and deployment capabilities for the Codomyrmex ecosystem.
"""

# Submodule exports - import first
try:
    from . import docker, kubernetes, registry, security
except ImportError:
    docker = kubernetes = registry = security = None

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .registry.container_registry import (
        ContainerRegistry,
        manage_container_registry,
    )
    HAS_REGISTRY = True
except ImportError:
    HAS_REGISTRY = False
    ContainerRegistry = None

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
    DockerManager = None
    ContainerConfig = None

try:
    from .kubernetes.kubernetes_orchestrator import (
        KubernetesDeployment,
        KubernetesOrchestrator,
        orchestrate_kubernetes,
    )
    HAS_K8S = True
except ImportError:
    HAS_K8S = False
    KubernetesOrchestrator = None

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
    SecurityScanResult = None

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

__all__ = [
    "docker",
    "kubernetes",
    "registry",
    "security",
]

if HAS_DOCKER_MANAGER:
    __all__.extend(["DockerManager", "ContainerConfig", "build_containers", "manage_containers"])
if HAS_REGISTRY:
    __all__.extend(["ContainerRegistry", "manage_container_registry"])
if HAS_K8S:
    __all__.extend(["KubernetesOrchestrator", "KubernetesDeployment", "orchestrate_kubernetes"])
if HAS_SCANNER:
    __all__.extend(["ContainerSecurityScanner", "SecurityScanResult", "scan_container_security"])
if HAS_OPTIMIZER:
    __all__.extend(["ContainerOptimizer", "ContainerMetrics", "optimize_containers"])
if HAS_EXCEPTIONS:
    __all__.extend(["ContainerError", "ImageBuildError", "NetworkError", "VolumeError", "RegistryError", "KubernetesError"])

__version__ = "0.1.0"
