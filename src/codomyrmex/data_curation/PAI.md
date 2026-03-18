# Data Curation — PAI Integration

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## AI Capabilities

The `data_curation` module provides AI agents with near-duplicate detection and corpus deduplication tools. Agents can clean training data, assess document overlap, and maintain corpus quality through MinHash-based Jaccard similarity estimation with LSH-accelerated lookup.

## Algorithm Phase Mapping

| PAI Phase | Relevance | Tools Used | Description |
| :--- | :--- | :--- | :--- |
| **OBSERVE** (1/7) | Primary | `data_curation_similarity` | Check if new document duplicates existing corpus |
| **THINK** (2/7) | Secondary | `data_curation_similarity` | Assess document overlap before processing |
| **BUILD** (4/7) | Primary | `data_curation_deduplicate` | Clean training data corpora before model training |
| **VERIFY** (6/7) | Primary | `data_curation_deduplicate` | Validate corpus quality via deduplication statistics |
| **LEARN** (7/7) | Secondary | `data_curation_similarity` | Track content drift across document versions |

## MCP Tools

| Tool | Category | Trust Level | Description |
| :--- | :--- | :--- | :--- |
| `data_curation_deduplicate` | data_curation | Safe | Deduplicate a text list using MinHash + LSH |
| `data_curation_similarity` | data_curation | Safe | Estimate Jaccard similarity between two texts |

## Agent Role Access

| Agent Role | Access Level | Permitted Operations |
| :--- | :--- | :--- |
| Engineer | Full | Deduplication, similarity checks, index building |
| Architect | Read | Similarity analysis for design review |
| QATester | Execute | Corpus quality validation via deduplication stats |
| DataEngineer | Full | All data curation operations |

## Integration Patterns

### Training Data Quality Gate

Before training, agents can ensure corpus quality:

```python
from codomyrmex.data_curation import DataCurator

curator = DataCurator(similarity_threshold=0.9)
unique_texts, stats = curator.deduplicate(training_corpus)
if stats["deduplication_ratio"] < 0.8:
    # Flag high duplication for review
    pass
```

### Document Ingestion Guard

Check new documents before adding to a knowledge base:

```python
from codomyrmex.data_curation import MinHash

mh = MinHash()
existing_sig = mh.signature(existing_doc)
new_sig = mh.signature(new_doc)

if mh.jaccard_estimate(existing_sig, new_sig) >= 0.8:
    # Skip: near-duplicate of existing document
    pass
```

## Dependencies

- **Foundation**: `model_context_protocol` (`@mcp_tool` decorator)
- **External**: `numpy` (vectorized hash computation)
- **Standard Library**: `hashlib`, `re`

## Agent Providers

This module does not provide agent types. It provides data quality tools that agents consume.

## Signposting

- **Self**: [PAI.md](PAI.md) — This document
- **Parent**: [README.md](README.md) — Module overview
- **Siblings**: [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Root Bridge**: [/PAI.md](../../../PAI.md) — PAI system bridge
