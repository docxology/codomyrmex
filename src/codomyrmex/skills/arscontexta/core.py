from __future__ import annotations

import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except Exception:
    logger = logging.getLogger(__name__)
from .models import (
    ConfigDimension,
    DimensionSignal,
    HealthStatus,
    KernelConfig,
    KernelLayer,
    KernelPrimitive,
    PipelineStage,
    ResearchClaim,
    StageResult,
    VaultConfig,
    VaultHealthReport,
    VaultSpace,
)

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
        self._primitives: dict[str, KernelPrimitive] = {}
        for p in _build_default_primitives():
            self._primitives[p.name] = p

    def get(self, name: str) -> KernelPrimitive | None:
        """Return the requested value."""
        return self._primitives.get(name)

    def list_all(self) -> list[KernelPrimitive]:
        return list(self._primitives.values())

    def list_by_layer(self, layer: KernelLayer) -> list[KernelPrimitive]:
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
        return KernelConfig(primitives=list(self._primitives.values()))


# ============================================================================
# Service: ProcessingPipeline (6R)
# ============================================================================


class ProcessingPipeline:
    """Implements the 6R Processing Pipeline with pluggable stage handlers."""

    def __init__(self) -> None:
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
        self._signals: list[DimensionSignal] = []

    def ingest_signal(self, signal: DimensionSignal) -> None:
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
        """Reset the state to its initial value."""
        self._signals.clear()


# ============================================================================
# Service: MethodologyGraph
# ============================================================================


class MethodologyGraph:
    """Adjacency-list graph of research claims grounding Ars Contexta decisions."""

    def __init__(self) -> None:
        self._claims: dict[str, ResearchClaim] = {}
        self._edges: dict[str, list[str]] = {}  # claim_id -> [related_ids]

    def add_claim(self, claim: ResearchClaim) -> None:
        self._claims[claim.claim_id] = claim
        if claim.claim_id not in self._edges:
            self._edges[claim.claim_id] = []

    def add_edge(self, from_id: str, to_id: str) -> None:
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
        return self._claims.get(claim_id)

    def get_related(self, claim_id: str) -> list[ResearchClaim]:
        related_ids = self._edges.get(claim_id, [])
        return [self._claims[rid] for rid in related_ids if rid in self._claims]

    def get_by_primitive(self, primitive_name: str) -> list[ResearchClaim]:
        return [
            c for c in self._claims.values() if primitive_name in c.connected_primitives
        ]

    def get_by_domain(self, domain: str) -> list[ResearchClaim]:
        return [c for c in self._claims.values() if c.domain == domain]

    def list_all(self) -> list[ResearchClaim]:
        return list(self._claims.values())

    def count(self) -> int:
        """Count."""
        return len(self._claims)

    def get_statistics(self) -> dict[str, Any]:
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
            except ValueError as e:
                logger.debug("Invalid kernel layer %r: %s", layer, e)
                return []
            prims = self.registry.list_by_layer(kl)
        else:
            prims = self.registry.list_all()
        return [p.to_dict() for p in prims]

    def get_methodology_stats(self) -> dict[str, Any]:
        return self.methodology.get_statistics()

    def get_config(self) -> VaultConfig | None:
        return self._config


