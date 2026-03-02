"""
Ars Contexta — Personalized Knowledge Management Architecture.

Implements the Three-Space Architecture (self/notes/ops), 15 Kernel Primitives
across 3 layers, a 6R Processing Pipeline (Record-Reduce-Reflect-Reweave-Verify-
Rethink), a Derivation Engine mapping user signals to 8 configuration dimensions,
and a Methodology Graph of 249 research claims grounding decisions in cognitive
science.

Based on https://github.com/agenticnotetaking/arscontexta
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Enums
# ============================================================================


class VaultSpace(Enum):
    """Three-Space Architecture directories."""

    SELF = "self"
    NOTES = "notes"
    OPS = "ops"


class KernelLayer(Enum):
    """Kernel primitive organisational layers."""

    FOUNDATION = "foundation"
    CONVENTION = "convention"
    AUTOMATION = "automation"


class PipelineStage(Enum):
    """6R Processing Pipeline stages."""

    RECORD = "record"
    REDUCE = "reduce"
    REFLECT = "reflect"
    REWEAVE = "reweave"
    VERIFY = "verify"
    RETHINK = "rethink"


class ConfigDimension(Enum):
    """Derivation engine configuration dimensions."""

    DOMAIN = "domain"
    METHODOLOGY = "methodology"
    ABSTRACTION_LEVEL = "abstraction_level"
    TEMPORAL_SCOPE = "temporal_scope"
    COLLABORATION_MODE = "collaboration_mode"
    OUTPUT_FORMAT = "output_format"
    TOOLCHAIN = "toolchain"
    LEARNING_STYLE = "learning_style"


class HealthStatus(Enum):
    """Vault health status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


class SkillType(Enum):
    """Skill registration type."""

    PLUGIN = "plugin"
    GENERATED = "generated"
    HOOK = "hook"


# ============================================================================
# Dataclasses
# ============================================================================


@dataclass
class KernelPrimitive:
    """A single kernel primitive definition."""

    name: str
    layer: KernelLayer
    description: str
    dependencies: list[str] = field(default_factory=list)
    validation_rule: str = ""
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "layer": self.layer.value,
            "description": self.description,
            "dependencies": self.dependencies,
            "validation_rule": self.validation_rule,
            "enabled": self.enabled,
        }


@dataclass
class ResearchClaim:
    """A methodology graph research claim."""

    claim_id: str
    statement: str
    source: str
    domain: str
    connected_primitives: list[str] = field(default_factory=list)
    confidence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "source": self.source,
            "domain": self.domain,
            "connected_primitives": self.connected_primitives,
            "confidence": self.confidence,
        }


@dataclass
class DimensionSignal:
    """A signal mapping to a configuration dimension."""

    dimension: ConfigDimension
    value: str
    confidence: float = 0.5
    source: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "dimension": self.dimension.value,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
        }


@dataclass
class StageResult:
    """Result of a single pipeline stage execution."""

    stage: PipelineStage
    input_content: str
    output_content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "stage": self.stage.value,
            "input_content": self.input_content,
            "output_content": self.output_content,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class VaultHealthReport:
    """Vault health diagnostics report."""

    status: HealthStatus
    spaces_present: list[str] = field(default_factory=list)
    primitives_valid: int = 0
    total_notes: int = 0
    orphaned_notes: int = 0
    broken_links: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "status": self.status.value,
            "spaces_present": self.spaces_present,
            "primitives_valid": self.primitives_valid,
            "total_notes": self.total_notes,
            "orphaned_notes": self.orphaned_notes,
            "broken_links": self.broken_links,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class KernelConfig:
    """Configuration holder for kernel primitives."""

    primitives: list[KernelPrimitive] = field(default_factory=list)

    def get_by_name(self, name: str) -> KernelPrimitive | None:
        """get By Name ."""
        for p in self.primitives:
            if p.name == name:
                return p
        return None

    def get_by_layer(self, layer: KernelLayer) -> list[KernelPrimitive]:
        """get By Layer ."""
        return [p for p in self.primitives if p.layer == layer]

    def validate_dependencies(self) -> list[str]:
        """Return list of unresolved dependency names."""
        names = {p.name for p in self.primitives}
        missing: list[str] = []
        for p in self.primitives:
            for dep in p.dependencies:
                if dep not in names:
                    missing.append(dep)
        return missing


@dataclass
class VaultConfig:
    """Configuration for a vault instance."""

    vault_path: Path
    kernel: KernelConfig = field(default_factory=KernelConfig)
    active_spaces: list[VaultSpace] = field(
        default_factory=lambda: [VaultSpace.SELF, VaultSpace.NOTES, VaultSpace.OPS]
    )
    derivation_signals: list[DimensionSignal] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "vault_path": str(self.vault_path),
            "kernel": {
                "primitives": [p.to_dict() for p in self.kernel.primitives]
            },
            "active_spaces": [s.value for s in self.active_spaces],
            "derivation_signals": [s.to_dict() for s in self.derivation_signals],
            "prerequisites": self.prerequisites,
            "created_at": self.created_at,
        }


# ============================================================================
# Exceptions
# ============================================================================


class ArsContextaError(Exception):
    """Base exception for arscontexta module."""


class VaultNotFoundError(ArsContextaError):
    """Raised when a vault path does not exist."""


class PrimitiveValidationError(ArsContextaError):
    """Raised when a kernel primitive fails validation."""


class PipelineError(ArsContextaError):
    """Raised when the processing pipeline encounters an error."""


# ============================================================================
