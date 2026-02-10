"""
Search Module

Full-text search with TF-IDF scoring, fuzzy matching, and query parsing.
"""

from .models import (
    Document,
    FuzzyMatcher,
    QueryParser,
    SearchResult,
    SimpleTokenizer,
    Tokenizer,
)
from .engine import InMemoryIndex, SearchIndex, create_index, quick_search

__all__ = [
    "Document",
    "SearchResult",
    "Tokenizer",
    "SimpleTokenizer",
    "FuzzyMatcher",
    "QueryParser",
    "SearchIndex",
    "InMemoryIndex",
    "create_index",
    "quick_search",
]
