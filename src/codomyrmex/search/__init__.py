"""
Search Module

Full-text search, semantic search, and indexing utilities.
"""

__version__ = "0.1.0"

import math
import re
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from collections.abc import Callable


@dataclass
class Document:
    """A searchable document."""
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    indexed_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """A search result."""
    document: Document
    score: float
    highlights: list[str] = field(default_factory=list)

    def __lt__(self, other: "SearchResult") -> bool:
        return self.score < other.score


class Tokenizer(ABC):
    """Abstract tokenizer."""

    @abstractmethod
    def tokenize(self, text: str) -> list[str]:
        pass


class SimpleTokenizer(Tokenizer):
    """Simple whitespace and punctuation tokenizer."""

    def __init__(self, lowercase: bool = True, min_length: int = 2):
        self.lowercase = lowercase
        self.min_length = min_length

    def tokenize(self, text: str) -> list[str]:
        if self.lowercase:
            text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return [t for t in tokens if len(t) >= self.min_length]


class SearchIndex(ABC):
    """Abstract search index."""

    @abstractmethod
    def index(self, document: Document) -> None:
        """Index a document."""
        pass

    @abstractmethod
    def search(self, query: str, k: int = 10) -> list[SearchResult]:
        """Search for documents."""
        pass

    @abstractmethod
    def delete(self, doc_id: str) -> bool:
        """Delete a document."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get document count."""
        pass


class InMemoryIndex(SearchIndex):
    """In-memory inverted index with TF-IDF scoring."""

    def __init__(self, tokenizer: Tokenizer | None = None):
        self.tokenizer = tokenizer or SimpleTokenizer()
        self._documents: dict[str, Document] = {}
        self._inverted_index: dict[str, set[str]] = defaultdict(set)
        self._doc_term_freq: dict[str, dict[str, int]] = {}
        self._lock = threading.Lock()

    def index(self, document: Document) -> None:
        """Index a document."""
        with self._lock:
            # Remove existing if present
            if document.id in self._documents:
                self._remove_from_index(document.id)

            # Tokenize and index
            tokens = self.tokenizer.tokenize(document.content)
            term_freq: dict[str, int] = defaultdict(int)

            for token in tokens:
                term_freq[token] += 1
                self._inverted_index[token].add(document.id)

            self._documents[document.id] = document
            self._doc_term_freq[document.id] = dict(term_freq)

    def _remove_from_index(self, doc_id: str) -> None:
        """Remove document from index."""
        if doc_id in self._doc_term_freq:
            for term in self._doc_term_freq[doc_id]:
                self._inverted_index[term].discard(doc_id)
            del self._doc_term_freq[doc_id]

        if doc_id in self._documents:
            del self._documents[doc_id]

    def search(self, query: str, k: int = 10) -> list[SearchResult]:
        """Search using TF-IDF scoring."""
        tokens = self.tokenizer.tokenize(query)
        if not tokens:
            return []

        # Find candidate documents
        candidates: set[str] = set()
        for token in tokens:
            candidates.update(self._inverted_index.get(token, set()))

        if not candidates:
            return []

        # Score documents
        num_docs = len(self._documents)
        results = []

        for doc_id in candidates:
            score = 0.0
            doc_terms = self._doc_term_freq.get(doc_id, {})

            for token in tokens:
                if token in doc_terms:
                    tf = doc_terms[token]
                    df = len(self._inverted_index.get(token, set()))
                    idf = math.log(num_docs / (df + 1)) + 1
                    score += tf * idf

            doc = self._documents[doc_id]

            # Generate highlights
            highlights = []
            content_lower = doc.content.lower()
            for token in tokens:
                idx = content_lower.find(token.lower())
                if idx != -1:
                    start = max(0, idx - 30)
                    end = min(len(doc.content), idx + len(token) + 30)
                    highlight = "..." + doc.content[start:end] + "..."
                    highlights.append(highlight)

            results.append(SearchResult(
                document=doc,
                score=score,
                highlights=highlights[:3],
            ))

        results.sort(reverse=True)
        return results[:k]

    def delete(self, doc_id: str) -> bool:
        """Delete a document."""
        with self._lock:
            if doc_id in self._documents:
                self._remove_from_index(doc_id)
                return True
        return False

    def count(self) -> int:
        """Get document count."""
        return len(self._documents)

    def get(self, doc_id: str) -> Document | None:
        """Get document by ID."""
        return self._documents.get(doc_id)


class FuzzyMatcher:
    """Fuzzy string matching utilities."""

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Compute Levenshtein edit distance."""
        if len(s1) < len(s2):
            return FuzzyMatcher.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]

    @staticmethod
    def similarity_ratio(s1: str, s2: str) -> float:
        """Get similarity ratio (0-1)."""
        if not s1 or not s2:
            return 0.0
        distance = FuzzyMatcher.levenshtein_distance(s1.lower(), s2.lower())
        max_len = max(len(s1), len(s2))
        return 1.0 - (distance / max_len)

    @staticmethod
    def find_best_match(query: str, candidates: list[str], threshold: float = 0.6) -> str | None:
        """Find best matching string."""
        best_match = None
        best_score = threshold

        for candidate in candidates:
            score = FuzzyMatcher.similarity_ratio(query, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate

        return best_match


class QueryParser:
    """Parse search queries with operators."""

    def __init__(self):
        self._operators = {
            '+': 'must',
            '-': 'must_not',
            '"': 'phrase',
        }

    def parse(self, query: str) -> dict[str, Any]:
        """Parse query into structured format."""
        result = {
            'terms': [],
            'must': [],
            'must_not': [],
            'phrases': [],
        }

        # Extract phrases
        phrases = re.findall(r'"([^"]+)"', query)
        result['phrases'] = phrases

        # Remove phrases from query
        query = re.sub(r'"[^"]+"', '', query)

        # Parse remaining tokens
        tokens = query.split()
        for token in tokens:
            if token.startswith('+'):
                result['must'].append(token[1:])
            elif token.startswith('-'):
                result['must_not'].append(token[1:])
            elif token:
                result['terms'].append(token)

        return result


# Semantic search extensions
try:
    from .semantic import AutoCompleteIndex, BM25Index, HybridSearchIndex, SemanticSearchResult
except ImportError:
    pass


# Convenience functions
def create_index(
    backend: str = "memory",
    **kwargs,
) -> SearchIndex:
    """Create a search index."""
    if backend == "memory":
        return InMemoryIndex(**kwargs)
    raise ValueError(f"Unknown backend: {backend}")


def quick_search(
    documents: list[str],
    query: str,
    k: int = 5,
) -> list[SearchResult]:
    """Quick search over a list of strings."""
    index = InMemoryIndex()
    for i, content in enumerate(documents):
        index.index(Document(id=str(i), content=content))
    return index.search(query, k=k)


__all__ = [
    # Core classes
    "SearchIndex",
    "InMemoryIndex",
    "Document",
    "SearchResult",
    # Utilities
    "Tokenizer",
    "SimpleTokenizer",
    "FuzzyMatcher",
    "QueryParser",
    # Convenience
    "create_index",
    "quick_search",
    # Semantic
    "SemanticSearchResult",
    "HybridSearchIndex",
    "BM25Index",
    "AutoCompleteIndex",
]
