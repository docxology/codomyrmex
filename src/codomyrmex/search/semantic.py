"""
Semantic Search Enhancements

Vector-based semantic search and hybrid retrieval.
"""

import math
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from . import Document, InMemoryIndex, SearchResult


@dataclass
class SemanticSearchResult:
    """Result from semantic search."""
    document: Document
    semantic_score: float
    keyword_score: float
    combined_score: float
    highlights: list[str] = field(default_factory=list)


class HybridSearchIndex:
    """Combine keyword and semantic search."""

    def __init__(
        self,
        embedding_fn: Callable[[str], list[float]] | None = None,
        vector_store=None,
        semantic_weight: float = 0.5,
    ):
        """Execute   Init   operations natively."""
        self._keyword_index = InMemoryIndex()
        self._embedding_fn = embedding_fn
        self._vector_store = vector_store
        self._semantic_weight = semantic_weight
        self._documents: dict[str, Document] = {}

    def index(self, document: Document) -> None:
        """Index document in both stores."""
        self._documents[document.id] = document

        # Keyword index
        self._keyword_index.index(document)

        # Semantic index
        if self._embedding_fn and self._vector_store:
            embedding = self._embedding_fn(document.content)
            self._vector_store.add(
                document.id,
                embedding,
                {"content": document.content[:200]},
            )

    def search(
        self,
        query: str,
        k: int = 10,
        semantic_weight: float | None = None,
    ) -> list[SemanticSearchResult]:
        """Hybrid search combining keyword and semantic."""
        weight = semantic_weight if semantic_weight is not None else self._semantic_weight

        # Keyword search
        keyword_results = self._keyword_index.search(query, k=k * 2)
        keyword_scores = {r.document.id: r.score for r in keyword_results}

        # Normalize keyword scores
        max_kw = max(keyword_scores.values()) if keyword_scores else 1.0
        keyword_scores = {k: v / max_kw for k, v in keyword_scores.items()}

        # Semantic search
        semantic_scores = {}
        if self._embedding_fn and self._vector_store:
            query_embedding = self._embedding_fn(query)
            vector_results = self._vector_store.search(query_embedding, k=k * 2)
            semantic_scores = {r.id: r.score for r in vector_results}

        # Combine results
        all_ids = set(keyword_scores.keys()) | set(semantic_scores.keys())
        results = []

        for doc_id in all_ids:
            if doc_id not in self._documents:
                continue

            document = self._documents[doc_id]
            kw_score = keyword_scores.get(doc_id, 0)
            sem_score = semantic_scores.get(doc_id, 0)
            combined = (1 - weight) * kw_score + weight * sem_score

            results.append(SemanticSearchResult(
                document=document,
                semantic_score=sem_score,
                keyword_score=kw_score,
                combined_score=combined,
            ))

        results.sort(key=lambda r: r.combined_score, reverse=True)
        return results[:k]

    def delete(self, doc_id: str) -> bool:
        """Delete from both stores."""
        self._keyword_index.delete(doc_id)
        if self._vector_store:
            self._vector_store.delete(doc_id)
        return self._documents.pop(doc_id, None) is not None

    def count(self) -> int:
        """Execute Count operations natively."""
        return len(self._documents)


class BM25Index:
    """BM25 ranking algorithm implementation."""

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
    ):
        """Execute   Init   operations natively."""
        self.k1 = k1
        self.b = b
        self._documents: dict[str, Document] = {}
        self._doc_lengths: dict[str, int] = {}
        self._avg_doc_length = 0.0
        self._inverted_index: dict[str, dict[str, int]] = {}
        self._doc_count = 0

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization."""
        import re
        return re.findall(r'\b\w+\b', text.lower())

    def index(self, document: Document) -> None:
        """Index a document."""
        tokens = self._tokenize(document.content)
        self._documents[document.id] = document
        self._doc_lengths[document.id] = len(tokens)

        # Update average length
        self._doc_count += 1
        total_length = sum(self._doc_lengths.values())
        self._avg_doc_length = total_length / self._doc_count

        # Build inverted index
        term_freq: dict[str, int] = {}
        for token in tokens:
            term_freq[token] = term_freq.get(token, 0) + 1

        for term, freq in term_freq.items():
            if term not in self._inverted_index:
                self._inverted_index[term] = {}
            self._inverted_index[term][document.id] = freq

    def search(self, query: str, k: int = 10) -> list[SearchResult]:
        """Search using BM25 scoring."""
        query_tokens = self._tokenize(query)
        scores: dict[str, float] = {}

        for token in query_tokens:
            if token not in self._inverted_index:
                continue

            # IDF component
            doc_freq = len(self._inverted_index[token])
            idf = math.log(
                (self._doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1
            )

            for doc_id, term_freq in self._inverted_index[token].items():
                doc_len = self._doc_lengths[doc_id]

                # BM25 term score
                numerator = term_freq * (self.k1 + 1)
                denominator = term_freq + self.k1 * (
                    1 - self.b + self.b * (doc_len / self._avg_doc_length)
                )
                score = idf * (numerator / denominator)

                scores[doc_id] = scores.get(doc_id, 0) + score

        # Sort and return top-k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

        return [
            SearchResult(
                document=self._documents[doc_id],
                score=score,
                highlights=[],
            )
            for doc_id, score in sorted_results
        ]


class AutoCompleteIndex:
    """Fast prefix-based autocomplete."""

    def __init__(self, max_suggestions: int = 10):
        """Execute   Init   operations natively."""
        self._trie: dict[str, Any] = {}
        self._max_suggestions = max_suggestions

    def add(self, term: str, weight: float = 1.0) -> None:
        """Add a term to the index."""
        node = self._trie
        for char in term.lower():
            if char not in node:
                node[char] = {}
            node = node[char]

        node["$"] = {"term": term, "weight": weight}

    def add_bulk(self, terms: list[str]) -> None:
        """Add multiple terms."""
        for term in terms:
            self.add(term)

    def suggest(self, prefix: str, limit: int | None = None) -> list[str]:
        """Get suggestions for prefix."""
        max_results = limit or self._max_suggestions

        # Navigate to prefix node
        node = self._trie
        for char in prefix.lower():
            if char not in node:
                return []
            node = node[char]

        # Collect all completions
        suggestions = []
        self._collect_completions(node, suggestions)

        # Sort by weight and return
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [term for term, _ in suggestions[:max_results]]

    def _collect_completions(
        self,
        node: dict,
        results: list,
    ) -> None:
        """Recursively collect completions from trie node."""
        if "$" in node:
            results.append((node["$"]["term"], node["$"]["weight"]))

        for char, child in node.items():
            if char != "$":
                self._collect_completions(child, results)
