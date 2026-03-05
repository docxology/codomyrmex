"""Document search and indexing operations."""

from .indexer import InMemoryIndex, create_index, index_document
from .query_builder import QueryBuilder, build_query
from .searcher import search_documents, search_index

__all__ = [
    "InMemoryIndex",
    "QueryBuilder",
    "build_query",
    "create_index",
    "index_document",
    "search_documents",
    "search_index",
]
