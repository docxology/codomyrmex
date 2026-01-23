"""
Kubernetes submodule for containerization.

Provides Kubernetes orchestration and deployment.
"""

from .kubernetes_orchestrator import KubernetesOrchestrator

__all__ = [
    "KubernetesOrchestrator",
]
