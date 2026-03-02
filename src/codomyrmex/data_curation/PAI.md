# Data Curation -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `data_curation_similarity` | Check if new document duplicates existing corpus |
| THINK | `data_curation_similarity` | Assess document overlap before processing |
| BUILD | `data_curation_deduplicate` | Clean training data corpora |
| VERIFY | `data_curation_deduplicate` | Validate corpus quality via deduplication stats |
| LEARN | `data_curation_similarity` | Track content drift across document versions |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `data_curation_deduplicate` | data_curation | Deduplicate texts using MinHash + LSH |
| `data_curation_similarity` | data_curation | Estimate Jaccard similarity between two texts |

## Agent Providers

This module does not provide agent types. It provides data quality tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
