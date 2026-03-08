"""
Search Module

Full-text search with TF-IDF scoring, fuzzy matching, and query parsing.
"""

# Shared schemas for cross-module interop
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

from .engine import InMemoryIndex, SearchIndex, create_index, quick_search
from .models import (
    Document,
    FuzzyMatcher,
    QueryParser,
    SearchResult,
    SimpleTokenizer,
    Tokenizer,
)


def cli_commands():
    """Return CLI commands for the search module."""
    return {
        "engines": {
            "help": "List available search engines",
            "handler": lambda **kwargs: print(
                "Search Engines:\n"
                "  - in_memory   (TF-IDF based, default)\n"
                "  - fuzzy       (fuzzy matching via FuzzyMatcher)"
            ),
        },
        "query": {
            "help": "Search the index with a query string",
            "args": {"--query": {"help": "Search query", "required": True}},
            "handler": lambda query="", **kwargs: print(
                f"Searching for: {query}\n"
                f"  (no index loaded -- use create_index() first)"
            ),
        },
    }


__all__ = [
    "Document",
    "FuzzyMatcher",
    "InMemoryIndex",
    "QueryParser",
    "SearchIndex",
    "SearchResult",
    "SimpleTokenizer",
    "Tokenizer",
    # CLI integration
    "cli_commands",
    "create_index",
    "quick_search",
]
