"""
Container Optimization module for Codomyrmex.

This module provides tools for analyzing and improving container images and resource usage.
Heavy dependencies (docker SDK) load only when ContainerOptimizer or ResourceTuner is accessed.
"""

from __future__ import annotations

__all__ = ["ContainerOptimizer", "ResourceTuner"]


def __getattr__(name: str):
    if name == "ContainerOptimizer":
        from codomyrmex.container_optimization.optimizer import ContainerOptimizer

        return ContainerOptimizer
    if name == "ResourceTuner":
        from codomyrmex.container_optimization.resource_tuner import ResourceTuner

        return ResourceTuner
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
