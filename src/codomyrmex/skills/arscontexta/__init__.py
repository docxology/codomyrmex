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

# Exceptions
from .exceptions import (
    ArsContextaError,
    PipelineError,
    PrimitiveValidationError,
    VaultNotFoundError,
)

# Types and data models (enums + dataclasses)
from .types import (
    ConfigDimension,
    DimensionSignal,
    HealthStatus,
    KernelConfig,
    KernelLayer,
    KernelPrimitive,
    PipelineStage,
    ResearchClaim,
    SkillType,
    StageResult,
    VaultConfig,
    VaultHealthReport,
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
