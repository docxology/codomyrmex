"""Memory summarization and compression for context windows.

Compresses agent memory by summarizing, deduplicating,
and prioritizing memories to fit within LLM context limits.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A single memory entry."""
    content: str
    importance: float = 0.5  # 0.0 - 1.0
    category: str = "general"
    access_count: int = 0
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]

    @property
    def token_estimate(self) -> int:
        """Rough token count estimate (words * 1.3)."""
        return int(len(self.content.split()) * 1.3)


@dataclass
class CompressionResult:
    """Result of memory compression."""
    original_count: int
    compressed_count: int
    original_tokens: int
    compressed_tokens: int
    entries: list[MemoryEntry] = field(default_factory=list)

    @property
    def compression_ratio(self) -> float:
        if self.original_tokens == 0:
            return 0.0
        return 1.0 - (self.compressed_tokens / self.original_tokens)


class MemoryCompressor:
    """Compress agent memories to fit context windows.

    Strategies include deduplication, importance-based pruning,
    recency weighting, and content summarization.
    """

    def __init__(self, max_tokens: int = 4000,
                 min_importance: float = 0.2) -> None:
        self._max_tokens = max_tokens
        self._min_importance = min_importance

    def compress(self, memories: list[MemoryEntry]) -> CompressionResult:
        """Compress memories to fit within token budget."""
        original_count = len(memories)
        original_tokens = sum(m.token_estimate for m in memories)

        # Step 1: Deduplicate
        deduped = self._deduplicate(memories)
        # Step 2: Filter by minimum importance
        filtered = [m for m in deduped if m.importance >= self._min_importance]
        # Step 3: Sort by composite score (importance + recency + access)
        scored = sorted(filtered, key=self._composite_score, reverse=True)
        # Step 4: Truncate to fit token budget
        selected = self._fit_budget(scored)

        compressed_tokens = sum(m.token_estimate for m in selected)

        return CompressionResult(
            original_count=original_count,
            compressed_count=len(selected),
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            entries=selected,
        )

    def _deduplicate(self, memories: list[MemoryEntry]) -> list[MemoryEntry]:
        """Remove duplicate memories by content hash."""
        seen: dict[str, MemoryEntry] = {}
        for m in memories:
            h = m.content_hash
            if h not in seen or m.importance > seen[h].importance:
                seen[h] = m
        return list(seen.values())

    def _composite_score(self, memory: MemoryEntry) -> float:
        """Compute composite priority score for ranking."""
        importance_weight = 0.5
        access_weight = 0.2
        recency_weight = 0.3
        access_score = min(memory.access_count / 10.0, 1.0)
        recency_score = min(memory.timestamp / 1e10, 1.0) if memory.timestamp else 0.0
        return (importance_weight * memory.importance +
                access_weight * access_score +
                recency_weight * recency_score)

    def _fit_budget(self, memories: list[MemoryEntry]) -> list[MemoryEntry]:
        """Select memories that fit within token budget."""
        selected: list[MemoryEntry] = []
        total_tokens = 0
        for m in memories:
            if total_tokens + m.token_estimate <= self._max_tokens:
                selected.append(m)
                total_tokens += m.token_estimate
            elif total_tokens >= self._max_tokens:
                break
        return selected

    def merge_similar(self, memories: list[MemoryEntry],
                      similarity_threshold: float = 0.8) -> list[MemoryEntry]:
        """Merge memories with highly similar content (word overlap)."""
        merged: list[MemoryEntry] = []
        used: set[int] = set()
        for i, m1 in enumerate(memories):
            if i in used:
                continue
            group = [m1]
            words1 = set(m1.content.lower().split())
            for j, m2 in enumerate(memories[i + 1:], i + 1):
                if j in used:
                    continue
                words2 = set(m2.content.lower().split())
                overlap = len(words1 & words2) / max(len(words1 | words2), 1)
                if overlap >= similarity_threshold:
                    group.append(m2)
                    used.add(j)
            # Keep the most important from the group
            best = max(group, key=lambda x: x.importance)
            best.access_count = sum(g.access_count for g in group)
            merged.append(best)
        return merged
