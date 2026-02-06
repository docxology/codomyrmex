# Agent Guidelines - Vector Store

## Module Context

The `vector_store` module provides embeddings storage for similarity search, commonly used in RAG pipelines and semantic retrieval systems.

## Key Classes

- `VectorStore` - Abstract base class defining the interface
- `InMemoryVectorStore` - Fast, volatile storage for development/testing
- `NamespacedVectorStore` - Multi-tenant vector isolation

## Integration Points

- **agentic_memory**: Use for embedding-based memory retrieval
- **graph_rag**: Backend storage for knowledge graph embeddings
- **llm**: Store and retrieve context embeddings

## Best Practices

1. **Normalize embeddings** before storage for consistent cosine similarity
2. **Use namespaces** to isolate different embedding models or datasets
3. **Batch inserts** for large datasets using `add_batch()`
4. **Filter first** using metadata filters to reduce search space

## Common Patterns

```python
# With agentic_memory
from codomyrmex.vector_store import InMemoryVectorStore
from codomyrmex.agentic_memory import AgentMemory

store = InMemoryVectorStore()
memory = AgentMemory(embedding_store=store)
```
