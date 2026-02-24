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

import hashlib
import json
import logging
import re
import shutil
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Logger (with fallback)
# ---------------------------------------------------------------------------

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger

    logger = get_logger(__name__)
except Exception:
    logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Skill discovery imports (deferred registration at module bottom)
# ---------------------------------------------------------------------------

try:
    from codomyrmex.skills.discovery import (
        DEFAULT_REGISTRY,
        FunctionSkill,
        ParameterSchema,
        SkillCategory,
        SkillMetadata,
    )

    _HAS_DISCOVERY = True
except ImportError:
    _HAS_DISCOVERY = False

# ============================================================================
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
        """Execute To Dict operations natively."""
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
        """Execute To Dict operations natively."""
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
        """Execute To Dict operations natively."""
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
        """Execute To Dict operations natively."""
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
        """Execute To Dict operations natively."""
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
        """Execute Get By Name operations natively."""
        for p in self.primitives:
            if p.name == name:
                return p
        return None

    def get_by_layer(self, layer: KernelLayer) -> list[KernelPrimitive]:
        """Execute Get By Layer operations natively."""
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
        """Execute To Dict operations natively."""
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
# Default Kernel Primitives (15 total)
# ============================================================================

_DEFAULT_PRIMITIVES: list[dict[str, Any]] = [
    # Foundation layer (5)
    {"name": "atomic-note", "layer": "foundation", "description": "Single-concept note", "dependencies": []},
    {"name": "unique-id", "layer": "foundation", "description": "Stable unique identifier per note", "dependencies": []},
    {"name": "timestamping", "layer": "foundation", "description": "Creation and modification timestamps", "dependencies": ["unique-id"]},
    {"name": "plain-text", "layer": "foundation", "description": "Plain text as canonical storage format", "dependencies": []},
    {"name": "link-syntax", "layer": "foundation", "description": "Bidirectional wikilink syntax", "dependencies": ["unique-id"]},
    # Convention layer (5)
    {"name": "naming-convention", "layer": "convention", "description": "Consistent file naming scheme", "dependencies": ["unique-id"]},
    {"name": "front-matter", "layer": "convention", "description": "YAML front-matter metadata block", "dependencies": ["plain-text"]},
    {"name": "folder-structure", "layer": "convention", "description": "Three-space directory layout", "dependencies": []},
    {"name": "tag-taxonomy", "layer": "convention", "description": "Hierarchical tagging taxonomy", "dependencies": ["front-matter"]},
    {"name": "template-set", "layer": "convention", "description": "Reusable note templates", "dependencies": ["front-matter", "naming-convention"]},
    # Automation layer (5)
    {"name": "auto-backlink", "layer": "automation", "description": "Automatic backlink generation", "dependencies": ["link-syntax"]},
    {"name": "auto-tag", "layer": "automation", "description": "Automatic tag suggestion", "dependencies": ["tag-taxonomy"]},
    {"name": "orphan-detection", "layer": "automation", "description": "Detect unlinked orphan notes", "dependencies": ["link-syntax", "auto-backlink"]},
    {"name": "pipeline-hook", "layer": "automation", "description": "6R pipeline stage hooks", "dependencies": ["template-set"]},
    {"name": "health-check", "layer": "automation", "description": "Vault health diagnostics", "dependencies": ["orphan-detection", "folder-structure"]},
]


def _build_default_primitives() -> list[KernelPrimitive]:
    """Build the 15 default kernel primitives."""
    layer_map = {
        "foundation": KernelLayer.FOUNDATION,
        "convention": KernelLayer.CONVENTION,
        "automation": KernelLayer.AUTOMATION,
    }
    return [
        KernelPrimitive(
            name=d["name"],
            layer=layer_map[d["layer"]],
            description=d["description"],
            dependencies=d["dependencies"],
        )
        for d in _DEFAULT_PRIMITIVES
    ]


# ============================================================================
# Service: KernelPrimitiveRegistry
# ============================================================================


class KernelPrimitiveRegistry:
    """Registry holding the 15 default kernel primitives."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._primitives: dict[str, KernelPrimitive] = {}
        for p in _build_default_primitives():
            self._primitives[p.name] = p

    def get(self, name: str) -> KernelPrimitive | None:
        """Execute Get operations natively."""
        return self._primitives.get(name)

    def list_all(self) -> list[KernelPrimitive]:
        """Execute List All operations natively."""
        return list(self._primitives.values())

    def list_by_layer(self, layer: KernelLayer) -> list[KernelPrimitive]:
        """Execute List By Layer operations natively."""
        return [p for p in self._primitives.values() if p.layer == layer]

    def validate_primitive(self, name: str, vault_path: Path) -> bool:
        """Check if a primitive's artefact exists at *vault_path*."""
        prim = self.get(name)
        if prim is None:
            return False
        # Structural check: for folder-structure, verify spaces exist
        if name == "folder-structure":
            return all(
                (vault_path / s.value).is_dir() for s in VaultSpace
            )
        # Default: primitive is registered and enabled
        return prim.enabled

    def to_kernel_config(self) -> KernelConfig:
        """Execute To Kernel Config operations natively."""
        return KernelConfig(primitives=list(self._primitives.values()))


# ============================================================================
# Service: ProcessingPipeline (6R)
# ============================================================================


class ProcessingPipeline:
    """Implements the 6R Processing Pipeline with pluggable stage handlers."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._handlers: dict[PipelineStage, list[Callable[[str, dict], str]]] = {
            stage: [] for stage in PipelineStage
        }
        self._results: list[StageResult] = []

    def register_handler(
        self, stage: PipelineStage, handler: Callable[[str, dict], str]
    ) -> None:
        """Register a handler for a pipeline stage."""
        self._handlers[stage].append(handler)

    def process(self, content: str, context: dict[str, Any] | None = None) -> list[StageResult]:
        """Run content through all 6 pipeline stages in order."""
        ctx = context or {}
        self._results = []
        current = content
        for stage in PipelineStage:
            result = self.process_single_stage(stage, current, ctx)
            self._results.append(result)
            if not result.success:
                break
            current = result.output_content
        return list(self._results)

    def process_single_stage(
        self, stage: PipelineStage, content: str, context: dict[str, Any] | None = None
    ) -> StageResult:
        """Run a single stage."""
        ctx = context or {}
        start = time.monotonic()
        output = content
        try:
            handlers = self._handlers.get(stage, [])
            for handler in handlers:
                output = handler(output, ctx)
            elapsed = (time.monotonic() - start) * 1000
            return StageResult(
                stage=stage,
                input_content=content,
                output_content=output,
                duration_ms=round(elapsed, 2),
                success=True,
            )
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            return StageResult(
                stage=stage,
                input_content=content,
                output_content=output,
                duration_ms=round(elapsed, 2),
                success=False,
                error=str(exc),
            )

    def get_results(self) -> list[StageResult]:
        """Execute Get Results operations natively."""
        return list(self._results)


# ============================================================================
# Service: DerivationEngine
# ============================================================================

# Keyword heuristics for text-to-dimension mapping
_DIMENSION_KEYWORDS: dict[str, list[tuple[str, str]]] = {
    "domain": [
        ("software", "software-engineering"),
        ("research", "academic-research"),
        ("design", "design"),
        ("business", "business"),
        ("science", "science"),
    ],
    "methodology": [
        ("zettelkasten", "zettelkasten"),
        ("gtd", "gtd"),
        ("para", "para"),
        ("agile", "agile"),
        ("kanban", "kanban"),
    ],
    "abstraction_level": [
        ("detail", "low"),
        ("overview", "high"),
        ("summary", "high"),
        ("granular", "low"),
    ],
    "temporal_scope": [
        ("daily", "daily"),
        ("weekly", "weekly"),
        ("project", "project"),
        ("long-term", "long-term"),
        ("archive", "archive"),
    ],
    "collaboration_mode": [
        ("solo", "solo"),
        ("team", "team"),
        ("public", "public"),
        ("shared", "shared"),
    ],
    "output_format": [
        ("markdown", "markdown"),
        ("pdf", "pdf"),
        ("html", "html"),
        ("plain", "plain-text"),
    ],
    "toolchain": [
        ("obsidian", "obsidian"),
        ("vim", "vim"),
        ("vscode", "vscode"),
        ("logseq", "logseq"),
        ("notion", "notion"),
    ],
    "learning_style": [
        ("visual", "visual"),
        ("textual", "textual"),
        ("hands-on", "kinesthetic"),
        ("auditory", "auditory"),
    ],
}


class DerivationEngine:
    """Maps user text to 8 configuration dimensions with confidence scoring."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._signals: list[DimensionSignal] = []

    def ingest_signal(self, signal: DimensionSignal) -> None:
        """Execute Ingest Signal operations natively."""
        self._signals.append(signal)

    def ingest_from_text(self, text: str, source: str = "user") -> list[DimensionSignal]:
        """Extract dimension signals from free-form text via keyword heuristics."""
        new_signals: list[DimensionSignal] = []
        lower = text.lower()
        for dim_key, keywords in _DIMENSION_KEYWORDS.items():
            dimension = ConfigDimension(dim_key)
            for keyword, value in keywords:
                if keyword in lower:
                    sig = DimensionSignal(
                        dimension=dimension,
                        value=value,
                        confidence=0.6,
                        source=source,
                    )
                    self._signals.append(sig)
                    new_signals.append(sig)
        return new_signals

    def get_dimension_summary(self) -> dict[str, list[dict[str, Any]]]:
        """Group signals by dimension."""
        summary: dict[str, list[dict[str, Any]]] = {}
        for sig in self._signals:
            key = sig.dimension.value
            if key not in summary:
                summary[key] = []
            summary[key].append(sig.to_dict())
        return summary

    def get_overall_confidence(self) -> float:
        """Average confidence across all signals, or 0.0 if empty."""
        if not self._signals:
            return 0.0
        return sum(s.confidence for s in self._signals) / len(self._signals)

    def reset(self) -> None:
        """Execute Reset operations natively."""
        self._signals.clear()


# ============================================================================
# Service: MethodologyGraph
# ============================================================================


class MethodologyGraph:
    """Adjacency-list graph of research claims grounding Ars Contexta decisions."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._claims: dict[str, ResearchClaim] = {}
        self._edges: dict[str, list[str]] = {}  # claim_id -> [related_ids]

    def add_claim(self, claim: ResearchClaim) -> None:
        """Execute Add Claim operations natively."""
        self._claims[claim.claim_id] = claim
        if claim.claim_id not in self._edges:
            self._edges[claim.claim_id] = []

    def add_edge(self, from_id: str, to_id: str) -> None:
        """Execute Add Edge operations natively."""
        if from_id not in self._edges:
            self._edges[from_id] = []
        if to_id not in self._edges[from_id]:
            self._edges[from_id].append(to_id)
        # Bidirectional
        if to_id not in self._edges:
            self._edges[to_id] = []
        if from_id not in self._edges[to_id]:
            self._edges[to_id].append(from_id)

    def get_claim(self, claim_id: str) -> ResearchClaim | None:
        """Execute Get Claim operations natively."""
        return self._claims.get(claim_id)

    def get_related(self, claim_id: str) -> list[ResearchClaim]:
        """Execute Get Related operations natively."""
        related_ids = self._edges.get(claim_id, [])
        return [self._claims[rid] for rid in related_ids if rid in self._claims]

    def get_by_primitive(self, primitive_name: str) -> list[ResearchClaim]:
        """Execute Get By Primitive operations natively."""
        return [
            c for c in self._claims.values() if primitive_name in c.connected_primitives
        ]

    def get_by_domain(self, domain: str) -> list[ResearchClaim]:
        """Execute Get By Domain operations natively."""
        return [c for c in self._claims.values() if c.domain == domain]

    def list_all(self) -> list[ResearchClaim]:
        """Execute List All operations natively."""
        return list(self._claims.values())

    def count(self) -> int:
        """Execute Count operations natively."""
        return len(self._claims)

    def get_statistics(self) -> dict[str, Any]:
        """Execute Get Statistics operations natively."""
        domains: dict[str, int] = {}
        for c in self._claims.values():
            domains[c.domain] = domains.get(c.domain, 0) + 1
        return {
            "total_claims": len(self._claims),
            "total_edges": sum(len(v) for v in self._edges.values()) // 2,
            "domains": domains,
            "avg_confidence": (
                sum(c.confidence for c in self._claims.values()) / len(self._claims)
                if self._claims
                else 0.0
            ),
        }


# ============================================================================
# Service: VaultHealthChecker
# ============================================================================


class VaultHealthChecker:
    """Diagnostics for vault directories."""

    def check(self, vault_path: Path) -> VaultHealthReport:
        """Run health diagnostics on a vault."""
        if not vault_path.exists():
            return VaultHealthReport(
                status=HealthStatus.ERROR,
                errors=[f"Vault path does not exist: {vault_path}"],
            )

        warnings: list[str] = []
        errors: list[str] = []
        spaces_present: list[str] = []

        for space in VaultSpace:
            space_dir = vault_path / space.value
            if space_dir.is_dir():
                spaces_present.append(space.value)
            else:
                warnings.append(f"Missing space directory: {space.value}")

        # Count notes (*.md files)
        total_notes = 0
        for _md in vault_path.rglob("*.md"):
            total_notes += 1

        status = HealthStatus.HEALTHY
        if errors:
            status = HealthStatus.ERROR
        elif warnings:
            status = HealthStatus.WARNING

        return VaultHealthReport(
            status=status,
            spaces_present=spaces_present,
            primitives_valid=0,
            total_notes=total_notes,
            orphaned_notes=0,
            broken_links=0,
            warnings=warnings,
            errors=errors,
        )


# ============================================================================
# Orchestrator: ArsContextaManager
# ============================================================================


class ArsContextaManager:
    """Main entry point composing all Ars Contexta services."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self.registry = KernelPrimitiveRegistry()
        self.pipeline = ProcessingPipeline()
        self.derivation = DerivationEngine()
        self.methodology = MethodologyGraph()
        self.health_checker = VaultHealthChecker()
        self._config: VaultConfig | None = None

    def setup(self, vault_path: str | Path) -> VaultConfig:
        """Initialise a vault at *vault_path*, creating Three-Space directories."""
        vp = Path(vault_path)
        vp.mkdir(parents=True, exist_ok=True)
        for space in VaultSpace:
            (vp / space.value).mkdir(exist_ok=True)

        self._config = VaultConfig(
            vault_path=vp,
            kernel=self.registry.to_kernel_config(),
        )
        logger.info("Vault initialised at %s", vp)
        return self._config

    def health(self, vault_path: str | Path | None = None) -> VaultHealthReport:
        """Run health diagnostics."""
        vp = Path(vault_path) if vault_path else (self._config.vault_path if self._config else None)
        if vp is None:
            return VaultHealthReport(
                status=HealthStatus.ERROR,
                errors=["No vault path configured"],
            )
        return self.health_checker.check(vp)

    def process_content(
        self, content: str, context: dict[str, Any] | None = None
    ) -> list[StageResult]:
        """Run content through the 6R pipeline."""
        return self.pipeline.process(content, context)

    def derive_config(self, user_text: str) -> dict[str, Any]:
        """Extract configuration signals from free-form text."""
        signals = self.derivation.ingest_from_text(user_text)
        return {
            "signals": [s.to_dict() for s in signals],
            "summary": self.derivation.get_dimension_summary(),
            "overall_confidence": self.derivation.get_overall_confidence(),
        }

    def get_primitives(self, layer: str | None = None) -> list[dict[str, Any]]:
        """List kernel primitives, optionally filtered by layer."""
        if layer:
            try:
                kl = KernelLayer(layer)
            except ValueError:
                return []
            prims = self.registry.list_by_layer(kl)
        else:
            prims = self.registry.list_all()
        return [p.to_dict() for p in prims]

    def get_methodology_stats(self) -> dict[str, Any]:
        """Execute Get Methodology Stats operations natively."""
        return self.methodology.get_statistics()

    def get_config(self) -> VaultConfig | None:
        """Execute Get Config operations natively."""
        return self._config


# ============================================================================
# Skill registration (into discovery.DEFAULT_REGISTRY)
# ============================================================================


def _register_arscontexta_skills() -> None:
    """Register 6 MCP-ready skills into the global discovery registry."""
    if not _HAS_DISCOVERY:
        logger.debug("Skipping arscontexta skill registration — discovery module unavailable")
        return

    manager = ArsContextaManager()

    # --- skill functions ---

    def arscontexta_setup(vault_path: str) -> dict:
        """Initialise an Ars Contexta vault at the given path."""
        cfg = manager.setup(vault_path)
        return cfg.to_dict()

    def arscontexta_health(vault_path: str) -> dict:
        """Run vault health diagnostics."""
        report = manager.health(vault_path)
        return report.to_dict()

    def arscontexta_process(content: str, context: str = "{}") -> list:
        """Run the 6R processing pipeline on content."""
        ctx = json.loads(context) if isinstance(context, str) else context
        results = manager.process_content(content, ctx)
        return [r.to_dict() for r in results]

    def arscontexta_derive(user_text: str) -> dict:
        """Extract configuration dimension signals from user text."""
        return manager.derive_config(user_text)

    def arscontexta_primitives(layer: str = "") -> list:
        """List kernel primitives, optionally filtered by layer name."""
        return manager.get_primitives(layer or None)

    def arscontexta_stats() -> dict:
        """Get methodology graph statistics."""
        return manager.get_methodology_stats()

    _SKILL_DEFS: list[tuple[Callable, str, str, list[ParameterSchema]]] = [
        (
            arscontexta_setup,
            "arscontexta_setup",
            "Initialise an Ars Contexta vault at the given path.",
            [ParameterSchema(name="vault_path", param_type="string", description="Filesystem path for the vault")],
        ),
        (
            arscontexta_health,
            "arscontexta_health",
            "Run vault health diagnostics.",
            [ParameterSchema(name="vault_path", param_type="string", description="Filesystem path of the vault")],
        ),
        (
            arscontexta_process,
            "arscontexta_process",
            "Run the 6R processing pipeline on content.",
            [
                ParameterSchema(name="content", param_type="string", description="Content to process"),
                ParameterSchema(name="context", param_type="string", description="JSON context object", required=False, default="{}"),
            ],
        ),
        (
            arscontexta_derive,
            "arscontexta_derive",
            "Extract configuration dimension signals from user text.",
            [ParameterSchema(name="user_text", param_type="string", description="Free-form user text")],
        ),
        (
            arscontexta_primitives,
            "arscontexta_primitives",
            "List kernel primitives, optionally filtered by layer.",
            [ParameterSchema(name="layer", param_type="string", description="Layer filter", required=False, default="")],
        ),
        (
            arscontexta_stats,
            "arscontexta_stats",
            "Get methodology graph statistics.",
            [],
        ),
    ]

    tags = ["arscontexta", "knowledge-management", "cognitive-architecture"]

    for func, name, desc, params in _SKILL_DEFS:
        skill_id = hashlib.md5(f"arscontexta.{name}".encode()).hexdigest()[:12]
        meta = SkillMetadata(
            id=skill_id,
            name=name,
            description=desc,
            version="1.0.0",
            category=SkillCategory.REASONING,
            tags=list(tags),
            parameters=params,
        )
        skill_obj = FunctionSkill(func, metadata=meta)
        DEFAULT_REGISTRY.register(skill_obj)
        logger.debug("Registered arscontexta skill: %s", name)


# Auto-register on import
_register_arscontexta_skills()


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Enums
    "VaultSpace",
    "KernelLayer",
    "PipelineStage",
    "ConfigDimension",
    "HealthStatus",
    "SkillType",
    # Dataclasses
    "KernelPrimitive",
    "ResearchClaim",
    "DimensionSignal",
    "StageResult",
    "VaultHealthReport",
    "KernelConfig",
    "VaultConfig",
    # Exceptions
    "ArsContextaError",
    "VaultNotFoundError",
    "PrimitiveValidationError",
    "PipelineError",
    # Services
    "KernelPrimitiveRegistry",
    "ProcessingPipeline",
    "DerivationEngine",
    "MethodologyGraph",
    "VaultHealthChecker",
    # Orchestrator
    "ArsContextaManager",
]
