"""KnowledgeItemIndex — incremental index wrapper over KnowledgeMemory.

Maintains a lightweight in-memory TF-IDF-like index that is updated on every
:meth:`add` call so that :meth:`KnowledgeMemory.recall` has a fast pre-filter
path even before optional Ollama embeddings are available.

Usage::

    from codomyrmex.agentic_memory.ki_index import KnowledgeItemIndex

    idx = KnowledgeItemIndex()
    idx.add(memory_id="ki-001", content="OAuth2 refresh token patterns")
    idx.add(memory_id="ki-002", content="Docker multi-stage build guide")
    results = idx.search("OAuth2 token"), limit=3)
    # → [("ki-001", 0.66), ...]
"""

from __future__ import annotations

import math
import re
from collections import defaultdict


def _tokenise(text: str) -> list[str]:
    """Lowercase tokenisation stripping punctuation."""
    return re.findall(r"[a-z0-9]+", text.lower())


class KnowledgeItemIndex:
    """Incremental TF-IDF index over KnowledgeMemory entries.

    Each :meth:`add` call updates the document-frequency table so subsequent
    :meth:`search` calls benefit from accurate IDF weighting without a full
    rebuild.  :meth:`remove` removes a document from the index.

    This is intentionally a lightweight, dependency-free implementation —
    no numpy or scikit-learn required.  When Ollama embeddings are available
    the :class:`~codomyrmex.agentic_memory.memory.KnowledgeMemory` class will
    use them for re-ranking on top of these TF-IDF candidate results.

    Example::

        idx = KnowledgeItemIndex()
        idx.add("abc", "The quick brown fox")
        idx.add("def", "Quick sort algorithm explained")
        idx.search("quick fox", limit=2)
        # → [("abc", 0.xx), ("def", 0.xx)]
    """

    def __init__(self) -> None:
        # doc_id → {token: raw_tf}
        self._tf: dict[str, dict[str, float]] = {}
        # token → number of documents containing it
        self._df: dict[str, int] = defaultdict(int)
        # doc_id → original content (for snippet extraction)
        self._content: dict[str, str] = {}
        self._n_docs: int = 0

    # ── Mutation ──────────────────────────────────────────────────────

    def add(self, memory_id: str, content: str) -> None:
        """Index a knowledge item.

        If *memory_id* was previously indexed it is replaced (the old
        document-frequency contributions are reversed first).

        Args:
            memory_id: Unique KI identifier.
            content: Full text of the KI to index.
        """
        if memory_id in self._tf:
            self.remove(memory_id)

        tokens = _tokenise(content)
        if not tokens:
            return

        freq: dict[str, int] = defaultdict(int)
        for tok in tokens:
            freq[tok] += 1

        max_freq = max(freq.values()) or 1
        tf: dict[str, float] = {tok: count / max_freq for tok, count in freq.items()}

        for tok in tf:
            self._df[tok] += 1

        self._tf[memory_id] = tf
        self._content[memory_id] = content
        self._n_docs += 1

    def remove(self, memory_id: str) -> bool:
        """Remove a document from the index.

        Args:
            memory_id: ID to remove.

        Returns:
            ``True`` if the ID was found and removed.
        """
        if memory_id not in self._tf:
            return False
        for tok in self._tf[memory_id]:
            self._df[tok] = max(0, self._df[tok] - 1)
        del self._tf[memory_id]
        del self._content[memory_id]
        self._n_docs -= 1
        return True

    # ── Query ─────────────────────────────────────────────────────────

    def search(self, query: str, limit: int = 10) -> list[tuple[str, float]]:
        """Return ranked ``(memory_id, score)`` pairs for *query*.

        Scoring follows standard TF-IDF: for each query token present in a
        document, accumulate ``tf × idf``.  Results are sorted descending by
        score and capped at *limit*.

        Args:
            query: Natural-language search string.
            limit: Maximum results to return.

        Returns:
            List of ``(memory_id, score)`` tuples, highest score first.
        """
        q_tokens = _tokenise(query)
        if not q_tokens or self._n_docs == 0:
            return []

        scores: dict[str, float] = defaultdict(float)
        for tok in q_tokens:
            if self._df[tok] == 0:
                continue
            idf = math.log((self._n_docs + 1) / (self._df[tok] + 1)) + 1.0
            for doc_id, tf_map in self._tf.items():
                if tok in tf_map:
                    scores[doc_id] += tf_map[tok] * idf

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:limit]

    # ── Introspection ─────────────────────────────────────────────────

    @property
    def size(self) -> int:
        """Number of indexed documents."""
        return self._n_docs

    def snippet(self, memory_id: str, length: int = 120) -> str:
        """Return a short text snippet for a known document.

        Args:
            memory_id: ID of the indexed document.
            length: Maximum character length of the snippet.

        Returns:
            First *length* characters of the content, or ``""`` if unknown.
        """
        content = self._content.get(memory_id, "")
        return content[:length]


__all__ = ["KnowledgeItemIndex"]
