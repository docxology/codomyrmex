# Vector Store Module — Agent Coordination

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Signposting

- **Parent**: [docs/modules](../AGENTS.md)
- **Self**: [vector_store/AGENTS.md](AGENTS.md)
- **Source**: [src/codomyrmex/vector_store/](../../../src/codomyrmex/vector_store/)

## Purpose

Embeddings storage with similarity search using cosine, euclidean, or dot product metrics.

## Agent Guidelines

- Follow existing module patterns and conventions
- Ensure all changes maintain backward compatibility
- Update documentation when modifying public APIs
- Run tests before committing changes

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [docs/modules/](../README.md)
- **Project Root**: [README](../../../README.md)

## Common Patterns

```python
from codomyrmex.vector_store import SearchResult, VectorEntry, DistanceMetric

# Initialize SearchResult
searchresult = SearchResult()
```
