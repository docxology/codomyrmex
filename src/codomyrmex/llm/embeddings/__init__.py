"""LLM embedding models, providers, and vector similarity."""

from .models import Embedding, EmbeddingModel, SimilarityResult
from .providers import EmbeddingProvider, TestEmbeddingProvider
from .service import EmbeddingCache, EmbeddingIndex, EmbeddingService, chunk_text
from .similarity import cosine_similarity, dot_product, euclidean_distance

__all__ = [
    "Embedding",
    "EmbeddingCache",
    "EmbeddingIndex",
    "EmbeddingModel",
    "EmbeddingProvider",
    "EmbeddingService",
    "SimilarityResult",
    "TestEmbeddingProvider",
    "chunk_text",
    "cosine_similarity",
    "dot_product",
    "euclidean_distance",
]
