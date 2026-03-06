# Data Curation -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides MinHash-based near-duplicate detection and deduplication for text corpora. Uses Locality-Sensitive Hashing (LSH) for efficient approximate nearest neighbor search.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `data_curation_deduplicate` | Deduplicate a list of texts using MinHash and LSH | Standard | data_curation |
| `data_curation_similarity` | Estimate Jaccard similarity between two texts using MinHash | Standard | data_curation |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Prepare deduplicated training corpora for ML pipelines |
| VERIFY | QA Agent | Validate dataset quality by detecting near-duplicate documents |


## Agent Instructions

1. Set similarity threshold between 0.0 and 1.0 (default 0.8) for deduplication strictness
2. Use data_curation_similarity to compare two individual documents before batch deduplication


## Navigation

- [Source README](../../src/codomyrmex/data_curation/README.md) | [SPEC.md](SPEC.md)
