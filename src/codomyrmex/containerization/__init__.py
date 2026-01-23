"""
Containerization Module for Codomyrmex.

The Containerization module provides container management,
orchestration, and deployment capabilities for the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Integrates with `ci_cd_automation` for automated container builds and deployments.
- Works with `security` for container security scanning.
- Supports `environment_setup` for container environment configuration.

Available functions:
- build_containers: Build Docker containers from source
- manage_containers: Container lifecycle management
- orchestrate_kubernetes: Kubernetes orchestration and management
- scan_container_security: Container security scanning and vulnerability assessment
- deploy_containers: Automated container deployment
- monitor_containers: Container health monitoring and logging
- manage_container_registry: Container registry operations
- optimize_containers: Container performance optimization

Data structures:
- ContainerConfig: Container configuration and build settings
- KubernetesDeployment: Kubernetes deployment configuration
- ContainerRegistry: Container registry connection and management
- ContainerMetrics: Container performance and resource metrics
- SecurityScanResult: Container security scan results
"""

# Import from new submodule structure
from .registry.container_registry import (
    ContainerRegistry,
    manage_container_registry,
)
from .docker.docker_manager import (
    ContainerConfig,
    DockerManager,
    build_containers,
    manage_containers,
)
from .kubernetes.kubernetes_orchestrator import (
    KubernetesDeployment,
    KubernetesOrchestrator,
    orchestrate_kubernetes,
)
from .security.performance_optimizer import (
    ContainerMetrics,
    ContainerOptimizer,
    optimize_containers,
)
from .security.security_scanner import (
    ContainerSecurityScanner,
    SecurityScanResult,
    scan_container_security,
)
from .exceptions import (
    ContainerError,
    ImageBuildError,
    NetworkError,
    VolumeError,
    RegistryError,
    KubernetesError,
)

# Submodule exports
from . import docker
from . import kubernetes
from . import registry
from . import security

__all__ = [
    # Docker management
    "DockerManager",
    "build_containers",
    "manage_containers",
    "ContainerConfig",
    # Kubernetes orchestration
    "KubernetesOrchestrator",
    "orchestrate_kubernetes",
    "KubernetesDeployment",
    # Container registry
    "ContainerRegistry",
    "manage_container_registry",
    # Security scanning
    "ContainerSecurityScanner",
    "scan_container_security",
    "SecurityScanResult",
    # Performance optimization
    "ContainerOptimizer",
    "optimize_containers",
    "ContainerMetrics",
    # Exceptions
    "ContainerError",
    "ImageBuildError",
    "NetworkError",
    "VolumeError",
    "RegistryError",
    "KubernetesError",
]
