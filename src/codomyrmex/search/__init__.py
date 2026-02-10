"""
Search Module

Full-text search with TF-IDF scoring, fuzzy matching, and query parsing.
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .models import (
    Document,
    FuzzyMatcher,
    QueryParser,
    SearchResult,
    SimpleTokenizer,
    Tokenizer,
)
from .engine import InMemoryIndex, SearchIndex, create_index, quick_search

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
    # CLI integration
    "cli_commands",
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
