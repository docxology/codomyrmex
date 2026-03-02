# Data Curation -- Agent Integration Guide

## Module Purpose

Provides MinHash-based near-duplicate detection and deduplication for AI agents that need to clean text corpora, remove redundant training data, or estimate document similarity.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `data_curation_deduplicate` | Deduplicate a list of texts using MinHash + LSH | `texts: list[str]`, `threshold: float` | `{unique_texts, stats}` |
| `data_curation_similarity` | Estimate Jaccard similarity between two texts | `text_a: str`, `text_b: str` | `{similarity, are_similar}` |

## Agent Use Cases

### Corpus Deduplication
An agent preparing training data can use `data_curation_deduplicate` to remove near-duplicate documents, improving data quality and reducing training cost.

### Document Similarity
Use `data_curation_similarity` to check if two documents are near-duplicates before adding to a corpus.

### Data Quality Auditing
Agents can assess corpus quality by checking deduplication ratios across document collections.

## Example Agent Workflow

```
1. Agent receives: "Clean this dataset of 1000 documents"
2. Agent calls: data_curation_deduplicate(texts, threshold=0.8)
3. Response: {"unique_texts": [...], "stats": {"duplicates_removed": 47, ...}}
4. Agent reports: "Removed 47 near-duplicates, 953 unique documents remain"
```
