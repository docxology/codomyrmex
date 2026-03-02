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
    # Enums
    "VaultSpace", "KernelLayer", "PipelineStage", "ConfigDimension",
    "HealthStatus", "SkillType",
    # Dataclasses
    "KernelPrimitive", "ResearchClaim", "DimensionSignal", "StageResult",
    "VaultHealthReport", "KernelConfig", "VaultConfig",
    # Exceptions
    "ArsContextaError", "VaultNotFoundError",
    "PrimitiveValidationError", "PipelineError",
    # Services
    "KernelPrimitiveRegistry", "ProcessingPipeline",
    "DerivationEngine", "MethodologyGraph", "VaultHealthChecker",
    # Core
    "ArsContextaManager",
]
