"""Memory → Case consolidation.

Converts a batch of ``Memory`` objects into lightweight ``Case``
records suitable for case-based reasoning, filtering by importance
and content length.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.agentic_memory.models import Memory, MemoryImportance


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
        cases: list[Case] = []
        for mem in memories:
            if len(cases) >= self.config.batch_size:
                break
            if mem.id in self._seen:
                continue
            if mem.importance.value < self.config.min_importance.value:
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
