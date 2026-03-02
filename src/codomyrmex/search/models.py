"""
Search Models

Data classes, tokenizers, and utilities for search.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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
        """lt ."""
        return self.score < other.score


class Tokenizer(ABC):
    """Abstract tokenizer."""

    @abstractmethod
    def tokenize(self, text: str) -> list[str]:
        """tokenize ."""
        pass


class SimpleTokenizer(Tokenizer):
    """Simple whitespace and punctuation tokenizer."""

    def __init__(self, lowercase: bool = True, min_length: int = 2):
        """Initialize this instance."""
        self.lowercase = lowercase
        self.min_length = min_length

    def tokenize(self, text: str) -> list[str]:
        """tokenize ."""
        if self.lowercase:
            text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return [t for t in tokens if len(t) >= self.min_length]


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
        """Initialize this instance."""
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
