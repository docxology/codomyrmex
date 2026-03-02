"""Arscontexta service classes: KernelPrimitiveRegistry, ProcessingPipeline, DerivationEngine."""

from __future__ import annotations

import hashlib
import json
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
    DEFAULT_REGISTRY = None  # type: ignore[assignment]
    FunctionSkill = None  # type: ignore[assignment,misc]
    ParameterSchema = None  # type: ignore[assignment,misc]
    SkillCategory = None  # type: ignore[assignment,misc]
    SkillMetadata = None  # type: ignore[assignment,misc]

from .core import ArsContextaManager, _DEFAULT_PRIMITIVES, _DIMENSION_KEYWORDS
from .models import VaultSpace
from .types import (
    ConfigDimension,
    DimensionSignal,
    KernelConfig,
    KernelLayer,
    KernelPrimitive,
    PipelineStage,
    StageResult,
)


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
