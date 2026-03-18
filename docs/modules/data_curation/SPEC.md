# Data Curation Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides MinHash-based near-duplicate detection and deduplication for text corpora. Uses Locality-Sensitive Hashing (LSH) for efficient approximate nearest neighbor search.

## Functional Requirements

1. MinHash signature generation for efficient approximate Jaccard similarity estimation
2. LSH index construction for sublinear-time near-duplicate retrieval
3. Batch deduplication with configurable similarity threshold and deduplication statistics


## Interface

```python
from codomyrmex.data_curation import DataCurator, MinHash, LSHIndex

curator = DataCurator(similarity_threshold=0.8)
unique_texts, stats = curator.deduplicate(texts)
mh = MinHash()
sig = mh.signature("sample text")
```

## Exports

MinHash, LSHIndex, DataCurator

## Navigation

- [Source README](../../src/codomyrmex/data_curation/README.md) | [AGENTS.md](AGENTS.md)
