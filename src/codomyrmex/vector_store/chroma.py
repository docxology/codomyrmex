"""ChromaDB vector store backend."""

from collections.abc import Callable
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.vector_store import (
    DistanceMetric,
    SearchResult,
    VectorEntry,
    VectorStore,
)

logger = get_logger(__name__)

try:
    import chromadb
except ImportError:
    chromadb = None


class ChromaVectorStore(VectorStore):
    """Vector store backed by ChromaDB.

    Provides true K-nearest-neighbor semantic search using
    an embedded or persistent Chroma client.
    """

    def __init__(
        self,
        collection_name: str = "agentic_memory",
        persist_directory: str | None = None,
        distance_metric: str = "cosine",
    ):
        if chromadb is None:
            raise ImportError(
                "chromadb is not installed. Please install it using `uv pip install chromadb` "
                "or add it to dependencies to use ChromaVectorStore."
            )

        if persist_directory:
            self._client = chromadb.PersistentClient(path=persist_directory)
        else:
            self._client = chromadb.EphemeralClient()

        # Chroma distance mapping: "cosine", "l2", "ip"
        # We default to cosine.
        metadata = {"hnsw:space": distance_metric}
        self._collection = self._client.get_or_create_collection(
            name=collection_name, metadata=metadata
        )
        self._distance_metric = distance_metric

    def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a vector to Chroma."""
        self._collection.upsert(
            ids=[id], embeddings=[embedding], metadatas=[metadata] if metadata else [{}]
        )

    def get(self, id: str) -> VectorEntry | None:
        """Get a vector by ID."""
        result = self._collection.get(ids=[id], include=["embeddings", "metadatas"])
        if not result["ids"]:
            return None

        return VectorEntry(
            id=result["ids"][0],
            embedding=result["embeddings"][0],
            metadata=result["metadatas"][0] if result["metadatas"] else {},
        )

    def delete(self, id: str) -> bool:
        """Delete a vector. Returns True if successfully deleted (or not present).
        Chroma delete doesn't return boolean success natively without checking first."""
        try:
            # Check if exists to return accurate bool
            exists = self.get(id) is not None
            if exists:
                self._collection.delete(ids=[id])
                return True
            return False
        except Exception as e:
            logger.warning("Failed to delete from chroma collection: %s", e)
            return False

    def search(
        self,
        query: list[float],
        k: int = 10,
        filter_fn: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors.

        Note: `filter_fn` requires pulling all metadata and discarding results
        if evaluated purely in Python. Chroma accepts a `where` dict for meta filtering,
        but for compatibility with VectorStore ABC, we will over-fetch and filter in memory,
        or just apply it if small.
        """
        # If we have a filter_fn, we might need to fetch more than k.
        fetch_k = max(k * 5, 100) if filter_fn else k

        # Determine total items to avoid querying more than what's available
        item_count = self.count()
        if item_count == 0:
            return []

        fetch_k = min(fetch_k, item_count)

        results = self._collection.query(
            query_embeddings=[query],
            n_results=fetch_k,
            include=["embeddings", "metadatas", "distances"],
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        search_results = []
        ids = results["ids"][0]
        embeddings = results["embeddings"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(ids)):
            meta = metadatas[i] if metadatas else {}
            if filter_fn and not filter_fn(meta):
                continue

            # Chroma returns distance, but our interface expects score (where higher = better for cosine)
            score = (
                1.0 - distances[i]
                if self._distance_metric == "cosine"
                else distances[i]
            )

            search_results.append(
                SearchResult(
                    id=ids[i],
                    score=score,
                    embedding=embeddings[i],
                    metadata=meta,
                )
            )

        # Truncate to true k if filter_fn omitted some
        return search_results[:k]

    def count(self) -> int:
        """Get vector count."""
        return self._collection.count()

    def clear(self) -> None:
        """Clear all vectors in the collection."""
        # The easiest way is to delete and recreate the collection.
        name = self._collection.name
        metadata = self._collection.metadata
        self._client.delete_collection(name)
        self._collection = self._client.create_collection(name=name, metadata=metadata)
