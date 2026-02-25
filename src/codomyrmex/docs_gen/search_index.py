"""In-memory search index for documentation.

Builds a tokenized inverted index over docs for fast
full-text search with relevance scoring.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """A search result.

    Attributes:
        doc_id: Document identifier.
        title: Document title.
        snippet: Matching text snippet.
        score: Relevance score.
        path: Document path.
    """

    doc_id: str
    title: str = ""
    snippet: str = ""
    score: float = 0.0
    path: str = ""


@dataclass
class IndexEntry:
    """An indexed document."""

    doc_id: str
    title: str = ""
    content: str = ""
    path: str = ""
    tags: list[str] = field(default_factory=list)


class SearchIndex:
    """In-memory inverted index for doc search.

    Example::

        index = SearchIndex()
        index.add("api-ref", title="API Reference", content="...")
        results = index.search("agent")
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._docs: dict[str, IndexEntry] = {}
        self._inverted: dict[str, set[str]] = defaultdict(set)

    @property
    def doc_count(self) -> int:
        """Execute Doc Count operations natively."""
        return len(self._docs)

    def add(
        self,
        doc_id: str,
        title: str = "",
        content: str = "",
        path: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """Add a document to the index.

        Args:
            doc_id: Document identifier.
            title: Document title.
            content: Document text content.
            path: Document file path.
            tags: Optional tags.
        """
        entry = IndexEntry(
            doc_id=doc_id, title=title, content=content,
            path=path, tags=tags or [],
        )
        self._docs[doc_id] = entry

        # Tokenize and index
        tokens = self._tokenize(title + " " + content)
        for token in tokens:
            self._inverted[token].add(doc_id)

        # Index tags
        for tag in (tags or []):
            self._inverted[tag.lower()].add(doc_id)

    def remove(self, doc_id: str) -> bool:
        """Remove a document from the index."""
        if doc_id not in self._docs:
            return False
        entry = self._docs.pop(doc_id)
        tokens = self._tokenize(entry.title + " " + entry.content)
        for token in tokens:
            self._inverted[token].discard(doc_id)
        return True

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search the index.

        Args:
            query: Search query string.
            limit: Maximum results to return.

        Returns:
            Sorted list of SearchResult objects.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Score docs by token hit count
        scores: dict[str, float] = defaultdict(float)
        for token in query_tokens:
            for doc_id in self._inverted.get(token, set()):
                scores[doc_id] += 1.0

        # Title bonus
        for doc_id, score in scores.items():
            entry = self._docs[doc_id]
            title_tokens = set(self._tokenize(entry.title))
            overlap = len(title_tokens & set(query_tokens))
            scores[doc_id] += overlap * 2.0  # Title matches worth 2x

        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]

        results = []
        for doc_id, score in ranked:
            entry = self._docs[doc_id]
            snippet = self._extract_snippet(entry.content, query_tokens)
            results.append(SearchResult(
                doc_id=doc_id,
                title=entry.title,
                snippet=snippet,
                score=score,
                path=entry.path,
            ))

        return results

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into lowercase words."""
        return re.findall(r"\w{2,}", text.lower())

    def _extract_snippet(self, content: str, query_tokens: list[str], max_len: int = 200) -> str:
        """Extract a relevant snippet from content."""
        lower = content.lower()
        best_pos = 0
        for token in query_tokens:
            pos = lower.find(token)
            if pos >= 0:
                best_pos = max(0, pos - 50)
                break

        snippet = content[best_pos:best_pos + max_len]
        if best_pos > 0:
            snippet = "..." + snippet
        if best_pos + max_len < len(content):
            snippet += "..."
        return snippet


__all__ = ["IndexEntry", "SearchIndex", "SearchResult"]
