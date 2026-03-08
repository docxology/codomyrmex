"""Shared search implementation for VectorStore subclasses."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from .models import SearchResult


class _SearchMixin:
    """Mixin providing the default linear-scan search for vector stores.

    Requires the host class to define:
        _vectors (dict[str, VectorEntry])
        _distance_fn (Callable[[list[float], list[float]], float])
        _higher_is_better (bool)
    """

    def search(
        self,
        query: list[float],
        k: int = 10,
        filter_fn: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors using linear scan."""
        from .models import SearchResult as SR

        results = []
        for entry in self._vectors.values():  # type: ignore[attr-defined]
            if filter_fn and not filter_fn(entry.metadata):
                continue
            score = self._distance_fn(query, entry.embedding)  # type: ignore[attr-defined]
            results.append(
                SR(
                    id=entry.id,
                    score=score,
                    embedding=entry.embedding,
                    metadata=entry.metadata,
                )
            )
        results.sort(key=lambda x: x.score, reverse=self._higher_is_better)  # type: ignore[attr-defined]
        return results[:k]
