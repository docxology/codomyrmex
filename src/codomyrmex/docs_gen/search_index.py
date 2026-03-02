"""In-memory search index for documentation.

Builds a tokenized inverted index over docs for fast
full-text search with relevance scoring.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

# Basic English stopwords
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he",
    "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "were",
    "will", "with",
}


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
        self._docs: dict[str, IndexEntry] = {}
        self._inverted: dict[str, set[str]] = defaultdict(set)

    @property
    def doc_count(self) -> int:
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
            for t in self._tokenize(tag):
                self._inverted[t].add(doc_id)

    def remove(self, doc_id: str) -> bool:
        """Remove a document from the index."""
        if doc_id not in self._docs:
            return False
        entry = self._docs.pop(doc_id)
        tokens = self._tokenize(entry.title + " " + entry.content)
        for token in tokens:
            self._inverted[token].discard(doc_id)
        for tag in entry.tags:
            for t in self._tokenize(tag):
                self._inverted[t].discard(doc_id)
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
        for doc_id, _score in scores.items():
            entry = self._docs[doc_id]
            title_tokens = set(self._tokenize(entry.title))
            overlap = len(title_tokens & set(query_tokens))
            scores[doc_id] += overlap * 2.0  # Title matches worth 2x extra

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
        """Tokenize text into lowercase words, splitting CamelCase and snake_case."""
        # Split CamelCase
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
        # Split snake_case and non-alphanumeric
        tokens = re.findall(r"[a-z0-9]{2,}", text.lower())
        # Filter stopwords
        return [t for t in tokens if t not in STOPWORDS]

    def _extract_snippet(self, content: str, query_tokens: list[str], max_len: int = 200) -> str:
        """Extract a relevant snippet from content."""
        lower = content.lower()
        best_pos = -1

        # Find the first occurrence of any query token
        for token in query_tokens:
            pos = lower.find(token)
            if pos >= 0:
                if best_pos == -1 or pos < best_pos:
                    best_pos = pos

        if best_pos == -1:
            snippet = content[:max_len]
            if len(content) > max_len:
                snippet += "..."
            return snippet

        # Try to center around the match, but stay within bounds
        start = max(0, best_pos - max_len // 2)
        end = min(len(content), start + max_len)

        # Adjust start if end hit the limit
        if end == len(content):
            start = max(0, end - max_len)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet.lstrip()
        if end < len(content):
            snippet = snippet.rstrip() + "..."

        return snippet


__all__ = ["IndexEntry", "SearchIndex", "SearchResult"]
