"""Document search operations."""

import re
from collections import Counter
from typing import List

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..models.document import Document
from .indexer import InMemoryIndex

logger = get_logger(__name__)


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    if not isinstance(text, str):
        text = str(text)
    return re.findall(r'\w+', text.lower())


def search_documents(query: str, index: InMemoryIndex) -> List[Document]:
    """
    Search documents using a query.

    Args:
        query: Search query string
        index: InMemoryIndex to search

    Returns:
        List of matching documents
    """
    terms = _tokenize(query)
    if not terms:
        return []

    doc_ids = index.search(terms)
    results = []
    for doc_id in doc_ids:
        doc = index.get_document(doc_id)
        if doc is not None:
            results.append(doc)

    return results


def search_index(query: str, index: InMemoryIndex) -> List[dict]:
    """
    Search index and return results with scores.

    Args:
        query: Search query string
        index: InMemoryIndex to search

    Returns:
        List of search result dictionaries with 'document_id', 'score', and 'document' keys
    """
    terms = _tokenize(query)
    if not terms:
        return []

    doc_ids = index.search(terms)
    results = []

    for doc_id in doc_ids:
        doc = index.get_document(doc_id)
        if doc is None:
            continue

        # Basic TF scoring: count how many times query terms appear in content
        content_tokens = _tokenize(doc.get_content_as_string())
        token_counts = Counter(content_tokens)
        score = sum(token_counts.get(t, 0) for t in terms)

        results.append({
            "document_id": doc_id,
            "score": score,
            "document": doc,
        })

    # Sort by score descending
    results.sort(key=lambda r: r["score"], reverse=True)
    return results
