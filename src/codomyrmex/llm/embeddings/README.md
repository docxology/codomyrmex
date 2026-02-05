# embeddings

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Text embedding generation, caching, and similarity computation. Provides an `EmbeddingProvider` abstraction for plugging in any embedding API, an LRU `EmbeddingCache` to avoid redundant API calls, an `EmbeddingIndex` for in-memory similarity search, and an `EmbeddingService` that ties providers, caching, and batching together. Includes three vector similarity functions (cosine, Euclidean, dot product) and a `chunk_text()` utility for splitting documents before embedding.

## Key Exports

- **`EmbeddingModel`** -- Enum of known embedding models (OpenAI ada-002/3-small/3-large, Cohere embed-v3, Voyage large-2, local sentence-transformer) with a `dimensions` property
- **`Embedding`** -- Dataclass holding a float vector, source text, model name, timestamp, and metadata; supports L2 normalization and dict serialization
- **`SimilarityResult`** -- Dataclass wrapping an `Embedding` with a similarity score and rank
- **`EmbeddingProvider`** -- Abstract base class defining `embed()` and `embed_batch()` interfaces
- **`MockEmbeddingProvider`** -- Testing provider that generates deterministic pseudo-embeddings from SHA-256 hashes
- **`EmbeddingCache`** -- Thread-safe LRU cache keyed by (text hash, model) with configurable max size
- **`EmbeddingIndex`** -- In-memory similarity search index using a configurable similarity function; supports add, batch add, search with top-k and threshold, and removal by text
- **`EmbeddingService`** -- High-level service combining a provider and cache with automatic cache-first lookup, batch processing of uncached texts, and hit-rate statistics
- **`cosine_similarity()`** -- Compute cosine similarity between two float vectors (returns -1 to 1)
- **`euclidean_distance()`** -- Compute Euclidean distance between two float vectors (returns >= 0)
- **`dot_product()`** -- Compute dot product of two float vectors
- **`chunk_text()`** -- Split text into overlapping chunks by character count with preferred separator splitting

## Directory Contents

- `__init__.py` - All embedding logic: models enum, embedding dataclass, providers, cache, index, service, similarity functions, text chunking
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
