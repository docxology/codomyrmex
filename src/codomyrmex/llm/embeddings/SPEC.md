# Technical Specification - Embeddings

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.llm.embeddings`  
**Last Updated**: 2026-01-29

## 1. Purpose

Text embedding generation, caching, and similarity search

## 2. Architecture

### 2.1 Components

```
embeddings/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `llm`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.llm.embeddings
from codomyrmex.llm.embeddings import (
    EmbeddingModel,           # Enum of supported embedding models (ada-002, 3-small, 3-large, Cohere, Voyage, local)
    Embedding,                # Dataclass: vector + text + model + metadata; supports normalize(), to_dict(), from_dict()
    SimilarityResult,         # Dataclass: embedding + score + rank from a similarity search
    EmbeddingProvider,        # ABC for embedding backends (embed, embed_batch, model_name)
    MockEmbeddingProvider,    # Deterministic hash-based provider for testing
    EmbeddingCache,           # Thread-safe LRU cache keyed by (text, model)
    EmbeddingIndex,           # In-memory similarity search index with pluggable distance function
    EmbeddingService,         # High-level service combining provider + cache + batching + stats
    cosine_similarity,        # (vec1, vec2) -> float in [-1, 1]
    euclidean_distance,       # (vec1, vec2) -> float >= 0
    dot_product,              # (vec1, vec2) -> float
    chunk_text,               # Split text into overlapping chunks for embedding
)

# Key class signatures:
class EmbeddingProvider(ABC):
    def embed(self, text: str) -> Embedding: ...
    def embed_batch(self, texts: list[str]) -> list[Embedding]: ...
    @property
    def model_name(self) -> str: ...

class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider, cache: EmbeddingCache | None = None, batch_size: int = 100): ...
    def embed(self, text: str, metadata: dict | None = None, use_cache: bool = True) -> Embedding: ...
    def embed_texts(self, texts: list[str], use_cache: bool = True) -> list[Embedding]: ...
    @property
    def cache_hit_rate(self) -> float: ...

class EmbeddingIndex:
    def __init__(self, similarity_fn: Callable = cosine_similarity): ...
    def add(self, embedding: Embedding) -> None: ...
    def search(self, query: Embedding | list[float], k: int = 10, threshold: float | None = None) -> list[SimilarityResult]: ...

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50, separator: str = "\n") -> list[str]: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Provider abstraction via ABC**: `EmbeddingProvider` defines `embed`, `embed_batch`, and `model_name` so backends (OpenAI, Cohere, local sentence-transformers) are swappable without changing calling code.
2. **LRU cache keyed by (text hash, model)**: `EmbeddingCache` is thread-safe with configurable `max_size`, evicting the least-recently-used entry on overflow.
3. **Pluggable similarity function**: `EmbeddingIndex` accepts any `(vec, vec) -> float` callable, defaulting to `cosine_similarity`; users can substitute `dot_product` or `euclidean_distance` without subclassing.

### 4.2 Limitations

- Token-count-based chunking is not supported; `chunk_text` operates on character counts only.
- `EmbeddingIndex` performs brute-force linear search -- not suitable for large-scale (>100k) vector sets; use a dedicated vector database for production workloads.
- `MockEmbeddingProvider` generates deterministic pseudo-embeddings via SHA-256 hashing; similarity scores between mock vectors are not semantically meaningful.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/llm/embeddings/
```

## 6. Future Considerations

- Integrate `tiktoken` for exact OpenAI token counting in `chunk_text`
- Add async variants of `EmbeddingProvider.embed` and `embed_batch`
- Support approximate nearest-neighbor search (e.g., HNSW) in `EmbeddingIndex` for larger datasets
