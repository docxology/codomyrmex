"""Hybrid keyword + semantic search.

Combines BM25-style keyword matching with vector similarity
for more robust search results.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    """A hybrid search result."""
    doc_id: str
    score: float
    keyword_score: float = 0.0
    semantic_score: float = 0.0
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class BM25Index:
    """Simple BM25 keyword index for hybrid search."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._docs: dict[str, list[str]] = {}
        self._doc_lengths: dict[str, int] = {}
        self._avg_dl: float = 0.0
        self._df: Counter[str] = Counter()
        self._n: int = 0

    def add_document(self, doc_id: str, text: str) -> None:
        """Add a document to the index."""
        tokens = self._tokenize(text)
        self._docs[doc_id] = tokens
        self._doc_lengths[doc_id] = len(tokens)
        self._df.update(set(tokens))
        self._n += 1
        self._avg_dl = sum(self._doc_lengths.values()) / max(self._n, 1)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Search using BM25 scoring."""
        query_tokens = self._tokenize(query)
        scores: dict[str, float] = {}
        for doc_id, doc_tokens in self._docs.items():
            score = self._bm25_score(query_tokens, doc_tokens, doc_id)
            if score > 0:
                scores[doc_id] = score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def _bm25_score(self, query_tokens: list[str], doc_tokens: list[str],
                    doc_id: str) -> float:
        """bm25 Score ."""
        tf_map = Counter(doc_tokens)
        dl = self._doc_lengths[doc_id]
        score = 0.0
        for term in query_tokens:
            if term not in tf_map:
                continue
            tf = tf_map[term]
            df = self._df.get(term, 0)
            idf = math.log((self._n - df + 0.5) / (df + 0.5) + 1)
            numerator = tf * (self._k1 + 1)
            denominator = tf + self._k1 * (1 - self._b + self._b * dl / max(self._avg_dl, 1))
            score += idf * numerator / denominator
        return score

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokenize."""
        return re.findall(r'\w+', text.lower())


class HybridSearchEngine:
    """Combine keyword (BM25) and semantic search results."""

    def __init__(self, keyword_weight: float = 0.4,
                 semantic_weight: float = 0.6) -> None:
        self._kw_weight = keyword_weight
        self._sem_weight = semantic_weight
        self._bm25 = BM25Index()
        self._documents: dict[str, str] = {}

    def add_document(self, doc_id: str, content: str,
                     metadata: dict[str, Any] | None = None) -> None:
        """Add a document for both keyword and semantic indexing."""
        self._bm25.add_document(doc_id, content)
        self._documents[doc_id] = content

    def search(self, query: str, top_k: int = 10,
               semantic_scores: dict[str, float] | None = None) -> list[SearchResult]:
        """Hybrid search combining BM25 and (optionally) semantic scores.

        Args:
            query: Search query.
            top_k: Number of results.
            semantic_scores: Pre-computed {doc_id: similarity_score} from vector store.
        """
        kw_results = dict(self._bm25.search(query, top_k=top_k * 2))
        sem_scores = semantic_scores or {}

        # Normalize scores
        max_kw = max(kw_results.values()) if kw_results else 1.0
        max_sem = max(sem_scores.values()) if sem_scores else 1.0

        all_ids = set(kw_results.keys()) | set(sem_scores.keys())
        results = []
        for doc_id in all_ids:
            kw_s = kw_results.get(doc_id, 0.0) / max(max_kw, 1e-9)
            sem_s = sem_scores.get(doc_id, 0.0) / max(max_sem, 1e-9)
            combined = self._kw_weight * kw_s + self._sem_weight * sem_s
            results.append(SearchResult(
                doc_id=doc_id,
                score=combined,
                keyword_score=kw_s,
                semantic_score=sem_s,
                content=self._documents.get(doc_id, ""),
            ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
