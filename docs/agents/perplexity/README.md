# Perplexity AI

**Module**: `codomyrmex.agents.perplexity` | **Category**: API-based | **Last Updated**: March 2026

## Overview

Search-augmented generation using the Perplexity Sonar API. Combines web search with LLM inference for real-time, citation-backed responses. Used for research queries, fact-checking, and up-to-date information retrieval.

## Key Classes

| Class | Purpose |
|:---|:---|
| `PerplexityClient` | Sonar API client for search-augmented queries |
| `PerplexityError` | Error handling for API failures |

## Configuration

**Required**: `PERPLEXITY_API_KEY`

## Usage

```python
from codomyrmex.agents.perplexity import PerplexityClient

client = PerplexityClient()
```

## Source Module

Source: [`src/codomyrmex/agents/perplexity/`](../../../../src/codomyrmex/agents/perplexity/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/perplexity/](../../../../src/codomyrmex/agents/perplexity/)
- **Project Root**: [README.md](../../../README.md)
