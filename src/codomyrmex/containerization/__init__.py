"""
Containerization Module for Codomyrmex.

The Containerization module provides comprehensive container management,
orchestration, and deployment capabilities for the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Integrates with `ci_cd_automation` for automated container builds and deployments.
- Works with `security_audit` for container security scanning.
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

from .docker_manager import (
    DockerManager,
    build_containers,
    manage_containers,
    ContainerConfig,
)

from .kubernetes_orchestrator import (
    KubernetesOrchestrator,
    orchestrate_kubernetes,
    KubernetesDeployment,
)

from .container_registry import (
    ContainerRegistry,
    manage_container_registry,
)

from .security_scanner import (
    ContainerSecurityScanner,
    scan_container_security,
    SecurityScanResult,
)

from .performance_optimizer import (
    ContainerOptimizer,
    optimize_containers,
    ContainerMetrics,
)

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
]
