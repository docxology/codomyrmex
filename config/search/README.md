# Search Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Full-text, fuzzy, and indexed search across documents and code. Provides search indexing, query parsing, and ranked result retrieval.

## Configuration Options

The search module operates with sensible defaults and does not require environment variable configuration. Search index storage path and tokenization settings are configurable. Fuzzy search threshold controls match sensitivity.

## MCP Tools

This module exposes 3 MCP tool(s):

- `search_documents`
- `search_index_query`
- `search_fuzzy`

## PAI Integration

PAI agents invoke search tools through the MCP bridge. Search index storage path and tokenization settings are configurable. Fuzzy search threshold controls match sensitivity.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep search

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/search/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
