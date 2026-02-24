"""
Search Engine

Search index implementations with TF-IDF scoring.
"""

import math
import threading
from abc import ABC, abstractmethod
from collections import defaultdict

from .models import Document, SearchResult, SimpleTokenizer, Tokenizer


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
        """Execute   Init   operations natively."""
        self.tokenizer = tokenizer or SimpleTokenizer()
        self._documents: dict[str, Document] = {}
        self._inverted_index: dict[str, set[str]] = defaultdict(set)
        self._doc_term_freq: dict[str, dict[str, int]] = {}
        self._lock = threading.Lock()

    def index(self, document: Document) -> None:
        """Index a document."""
        with self._lock:
            if document.id in self._documents:
                self._remove_from_index(document.id)
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

        candidates: set[str] = set()
        for token in tokens:
            candidates.update(self._inverted_index.get(token, set()))
        if not candidates:
            return []

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
                document=doc, score=score, highlights=highlights[:3],
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


def create_index(backend: str = "memory", **kwargs) -> SearchIndex:
    """Create a search index."""
    if backend == "memory":
        return InMemoryIndex(**kwargs)
    raise ValueError(f"Unknown backend: {backend}")


def quick_search(documents: list[str], query: str, k: int = 5) -> list[SearchResult]:
    """Quick search over a list of strings."""
    index = InMemoryIndex()
    for i, content in enumerate(documents):
        index.index(Document(id=str(i), content=content))
    return index.search(query, k=k)
