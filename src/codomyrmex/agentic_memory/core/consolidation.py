"""Memory → Case consolidation.

Converts a batch of ``Memory`` objects into lightweight ``Case``
records suitable for case-based reasoning, filtering by importance
and content length.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from codomyrmex.agentic_memory.core.models import Memory, MemoryImportance

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.rules.engine import RuleEngine


@dataclass
class Case:
    """A distilled memory case with features and context."""

    case_id: str
    features: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsolidationConfig:
    """Tuneable knobs for the consolidation filter."""

    min_importance: MemoryImportance = MemoryImportance.MEDIUM
    min_content_length: int = 20
    batch_size: int = 50
    rule_engine: RuleEngine | None = None
    #: Optional stigmergic ledger (:class:`~codomyrmex.agentic_memory.stigmergy.field.TraceField` or :class:`~codomyrmex.agentic_memory.stigmergy.sqlite_ledger.SqliteTraceLedger`).
    trace_field: Any | None = None
    #: Map memory → trace key (default: memory id).
    trace_key_for_memory: Callable[[Memory], str] | None = None


class MemoryConsolidator:
    """Convert ``Memory`` entries into ``Case`` objects.

    Applies importance and content-length filters and avoids
    duplicate consolidation.
    """

    def __init__(self, config: ConsolidationConfig | None = None) -> None:
        self.config = config or ConsolidationConfig()
        self._seen: set[str] = set()

    def consolidate(self, memories: list[Memory]) -> list[Case]:
        """Return at most ``batch_size`` cases, skipping duplicates and
        entries below the configured thresholds."""
        from codomyrmex.agentic_memory.stigmergy.policy import boost_importance_value

        cases: list[Case] = []
        for mem in memories:
            if len(cases) >= self.config.batch_size:
                break
            if mem.id in self._seen:
                continue
            # Rule-aware importance boost
            if self.config.rule_engine is not None and (
                "file_path" in mem.metadata or "module_name" in mem.metadata
            ):
                rules = self.config.rule_engine.get_applicable_rules(
                    file_path=mem.metadata.get("file_path"),
                    module_name=mem.metadata.get("module_name"),
                )
                if list(rules.resolved()):
                    # If rules apply, treat it as at least MEDIUM importance to avoid getting filtered
                    effective_importance = max(
                        mem.importance.value, MemoryImportance.MEDIUM.value
                    )
                else:
                    effective_importance = mem.importance.value
            else:
                effective_importance = mem.importance.value

            if self.config.trace_field is not None:
                key_fn = self.config.trace_key_for_memory
                tkey = key_fn(mem) if key_fn is not None else mem.id
                marker = self.config.trace_field.sense(tkey)
                if marker is not None:
                    effective_importance = boost_importance_value(
                        effective_importance,
                        marker.strength,
                    )

            if effective_importance < self.config.min_importance.value:
                continue
            if len(mem.content) < self.config.min_content_length:
                continue

            self._seen.add(mem.id)
            cases.append(
                Case(
                    case_id=f"memory-{mem.id}",
                    features={
                        "content_summary": mem.content[:120],
                        "memory_type": mem.memory_type.value,
                        "importance": mem.importance.value,
                    },
                    context={"full_content": mem.content},
                    metadata={
                        "source": "consolidation",
                        "memory_id": mem.id,
                    },
                )
            )
        return cases
