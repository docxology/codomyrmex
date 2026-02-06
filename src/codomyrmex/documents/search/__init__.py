"""Document search and indexing operations."""

from .indexer import InMemoryIndex, create_index, index_document
from .query_builder import QueryBuilder, build_query
from .searcher import search_documents, search_index

__all__ = [
    "InMemoryIndex",
    "index_document",
    "create_index",
    "search_documents",
    "search_index",
    "QueryBuilder",
    "build_query",
]
