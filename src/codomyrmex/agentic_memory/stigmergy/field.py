"""In-memory stigmergic trace field (pheromone-like ledger)."""

from __future__ import annotations

import time
from typing import Any

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig, TraceMarker


class TraceField:
    """Dict-backed traces: deposit, reinforce, sense, evaporate (tick), top_k."""

    def __init__(self, config: StigmergyConfig | None = None) -> None:
        self.config = config or StigmergyConfig()
        self._markers: dict[str, TraceMarker] = {}

    def _clamp(self, strength: float) -> float:
        return max(
            self.config.min_strength,
            min(self.config.max_strength, strength),
        )

    def deposit(
        self,
        key: str,
        initial: float = 1.0,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> TraceMarker:
        """Create or add strength at *key* (environmental mark)."""
        now = time.time()
        if key in self._markers:
            m = self._markers[key]
            m.strength = self._clamp(m.strength + initial)
            m.updated_at = now
            if metadata:
                m.metadata.update(metadata)
            return m
        m = TraceMarker(
            key=key,
            strength=self._clamp(initial),
            updated_at=now,
            metadata=dict(metadata or {}),
        )
        self._markers[key] = m
        return m

    def reinforce(self, key: str) -> TraceMarker | None:
        """Strengthen an existing trace (e.g. after successful recall)."""
        m = self._markers.get(key)
        if m is None:
            return None
        m.strength = self._clamp(m.strength + self.config.reinforce_on_read_delta)
        m.updated_at = time.time()
        return m

    def sense(self, key: str, *, reinforce: bool = False) -> TraceMarker | None:
        """Read trace at *key*; optionally reinforce (quantitative stigmergy on read)."""
        m = self._markers.get(key)
        if m is None:
            return None
        if reinforce:
            return self.reinforce(key)
        return TraceMarker(
            key=m.key,
            strength=m.strength,
            updated_at=m.updated_at,
            metadata=dict(m.metadata),
        )

    def tick(self) -> int:
        """Apply evaporation to all traces; remove at or below min_strength.

        Returns:
            Number of keys removed.
        """
        removed = 0
        to_del: list[str] = []
        for key, m in self._markers.items():
            m.strength -= self.config.evaporation_per_tick
            if m.strength <= self.config.min_strength:
                to_del.append(key)
        for key in to_del:
            del self._markers[key]
            removed += 1
        return removed

    def top_k(self, k: int = 10) -> list[TraceMarker]:
        """Strongest traces first."""
        ranked = sorted(
            self._markers.values(),
            key=lambda x: x.strength,
            reverse=True,
        )
        return ranked[:k]

    def __len__(self) -> int:
        return len(self._markers)
