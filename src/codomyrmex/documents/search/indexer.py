"""Document indexing operations."""

import json
import re
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..models.document import Document

logger = get_logger(__name__)


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    if not isinstance(text, str):
        text = str(text)
    return re.findall(r'\w+', text.lower())


class InMemoryIndex:
    """In-memory inverted index for document search."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._index: dict[str, set[str]] = {}
        self._documents: dict[str, Document] = {}

    def add(self, document: Document) -> None:
        """Add a document to the index."""
        doc_id = document.id
        self._documents[doc_id] = document

        content_str = document.get_content_as_string()
        tokens = _tokenize(content_str)

        for token in tokens:
            if token not in self._index:
                self._index[token] = set()
            self._index[token].add(doc_id)

        logger.debug(f"Indexed document {doc_id} with {len(tokens)} tokens")

    def remove(self, doc_id: str) -> None:
        """Remove a document from the index."""
        if doc_id not in self._documents:
            return

        del self._documents[doc_id]

        # Remove doc_id from all term sets
        empty_terms = []
        for term, doc_ids in self._index.items():
            doc_ids.discard(doc_id)
            if not doc_ids:
                empty_terms.append(term)

        for term in empty_terms:
            del self._index[term]

    def search(self, terms: list[str]) -> list[str]:
        """Search index for documents matching all given terms."""
        if not terms:
            return []

        normalized = [t.lower() for t in terms]
        result_sets = []
        for term in normalized:
            if term in self._index:
                result_sets.append(self._index[term])
            else:
                return []  # Term not found, intersection will be empty

        if not result_sets:
            return []

        result = result_sets[0]
        for s in result_sets[1:]:
            result = result & s

        return list(result)

    def get_document(self, doc_id: str) -> Document | None:
        """Retrieve a document by ID."""
        return self._documents.get(doc_id)

    @property
    def document_count(self) -> int:
        """Number of indexed documents."""
        return len(self._documents)

    def save(self, path: Path) -> None:
        """Save index to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        serializable_index = {
            term: list(doc_ids) for term, doc_ids in self._index.items()
        }
        documents = {
            doc_id: doc.to_dict() for doc_id, doc in self._documents.items()
        }

        data = {"index": serializable_index, "documents": documents}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        logger.debug(f"Saved index to {path}")

    @classmethod
    def load(cls, path: Path) -> "InMemoryIndex":
        """Load index from a JSON file (index only, documents are metadata)."""
        path = Path(path)
        with open(path, encoding='utf-8') as f:
            data = json.load(f)

        instance = cls()
        instance._index = {
            term: set(doc_ids) for term, doc_ids in data.get("index", {}).items()
        }
        # Note: loaded documents are dicts (metadata only), not full Document objects
        return instance


def index_document(document: Document, index: InMemoryIndex | None = None) -> InMemoryIndex:
    """
    Index a document for search.

    Args:
        document: Document to index
        index: Optional existing index to add to. Creates new one if None.

    Returns:
        The index with the document added.
    """
    if index is None:
        index = InMemoryIndex()

    index.add(document)
    return index


def create_index() -> InMemoryIndex:
    """
    Create a new empty search index.

    Returns:
        New InMemoryIndex instance.
    """
    return InMemoryIndex()
