"""Memory consolidation — short-term conversations to long-term cases.

Converts recent agent conversation entries (from ``agentic_memory``)
into structured ``Case`` objects for the ``CaseBase``.  This enables
long-term learning from agent interactions.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from codomyrmex.agentic_memory.models import Memory, MemoryImportance, MemoryType
from codomyrmex.cerebrum.core.cases import Case, CaseBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ConsolidationConfig:
    """Configuration for memory consolidation.

    Attributes:
        min_importance: Minimum memory importance for consolidation.
        min_content_length: Minimum content length to consolidate.
        batch_size: How many memories to consolidate per call.
    """

    min_importance: MemoryImportance = MemoryImportance.MEDIUM
    min_content_length: int = 20
    batch_size: int = 50


class MemoryConsolidator:
    """Consolidates short-term memories into long-term cases.

    Filters memories by importance and content quality, then
    converts qualifying entries into ``Case`` objects.

    Usage::

        consolidator = MemoryConsolidator()
        memories = memory_store.get_recent(100)
        cases = consolidator.consolidate(memories)
        for case in cases:
            case_base.add_case(case)
    """

    def __init__(
        self,
        config: ConsolidationConfig | None = None,
    ) -> None:
        self._config = config or ConsolidationConfig()
        self._consolidated_ids: set[str] = set()

    def consolidate(
        self,
        memories: list[Memory],
    ) -> list[Case]:
        """Consolidate a batch of memories into cases.

        Args:
            memories: List of memories to process.

        Returns:
            List of ``Case`` objects qualifying for long-term storage.
        """
        qualifying = [
            m for m in memories
            if self._should_consolidate(m)
        ]

        # Respect batch size
        batch = qualifying[:self._config.batch_size]
        cases: list[Case] = []

        for memory in batch:
            case = self._memory_to_case(memory)
            cases.append(case)
            self._consolidated_ids.add(memory.id)

        logger.info(
            "Memory consolidation complete",
            extra={
                "memories_in": len(memories),
                "qualifying": len(qualifying),
                "cases_out": len(cases),
            },
        )

        return cases

    def _should_consolidate(self, memory: Memory) -> bool:
        """Check if a memory qualifies for consolidation."""
        if memory.id in self._consolidated_ids:
            return False

        if memory.importance.value < self._config.min_importance.value:
            return False

        if len(memory.content) < self._config.min_content_length:
            return False

        return True

    def _memory_to_case(self, memory: Memory) -> Case:
        """Convert a single memory to a Case."""
        features: dict[str, Any] = {
            "content_summary": memory.content[:200],
            "memory_type": memory.memory_type.value,
            "importance": memory.importance.value,
            "access_count": memory.access_count,
        }

        context: dict[str, Any] = {
            "full_content": memory.content,
            "created_at": memory.created_at.isoformat(),
            "accessed_at": memory.accessed_at.isoformat(),
        }

        outcome: dict[str, Any] = memory.metadata.copy()

        return Case(
            case_id=f"memory-{memory.id}",
            features=features,
            context=context,
            outcome=outcome,
            metadata={
                "source": "consolidation",
                "memory_id": memory.id,
                "memory_type": memory.memory_type.value,
            },
        )


__all__ = [
    "ConsolidationConfig",
    "MemoryConsolidator",
]
