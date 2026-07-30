"""
Ars Contexta — Personalized Knowledge Management Architecture.

Implements the Three-Space Architecture, 15 Kernel Primitives,
6R Processing Pipeline, and Derivation Engine.
"""

from __future__ import annotations

# Core services (all live in core.py)
from .core import (
    ArsContextaManager,
    DerivationEngine,
    KernelPrimitiveRegistry,
    MethodologyGraph,
    ProcessingPipeline,
    VaultHealthChecker,
)

# Exceptions and data models
from .models import (
    ArsContextaError,
    ConfigDimension,
    DimensionSignal,
    HealthStatus,
    KernelConfig,
    KernelLayer,
    KernelPrimitive,
    PipelineError,
    PipelineStage,
    PrimitiveValidationError,
    ResearchClaim,
    SkillType,
    StageResult,
    VaultConfig,
    VaultHealthReport,
    VaultNotFoundError,
    VaultSpace,
)

__all__ = [
    # Exceptions
    "ArsContextaError",
    # Core
    "ArsContextaManager",
    "ConfigDimension",
    "DerivationEngine",
    "DimensionSignal",
    "HealthStatus",
    "KernelConfig",
    "KernelLayer",
    # Dataclasses
    "KernelPrimitive",
    # Services
    "KernelPrimitiveRegistry",
    "MethodologyGraph",
    "PipelineError",
    "PipelineStage",
    "PrimitiveValidationError",
    "ProcessingPipeline",
    "ResearchClaim",
    "SkillType",
    "StageResult",
    "VaultConfig",
    "VaultHealthChecker",
    "VaultHealthReport",
    "VaultNotFoundError",
    # Enums
    "VaultSpace",
]
