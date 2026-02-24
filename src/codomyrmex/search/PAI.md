# Personal AI Infrastructure — Search Module

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Search module provides code pattern identification, full-text search, and fuzzy
matching for codebase exploration. It powers the PAI Algorithm's OBSERVE phase by
enabling agents to find relevant code, patterns, and documentation across the project
without loading the entire codebase into context.

Three MCP tools expose search functionality to PAI agents: `search_documents` (TF-IDF
quick search), `search_index_query` (persistent index querying), and `search_fuzzy`
(approximate string matching for typo-tolerant navigation).

## PAI Capabilities

### Full-Text Search with TF-IDF Scoring

Rank documents by relevance to a query using term-frequency scoring:

```python
from codomyrmex.search import quick_search, Document

documents = [
    "Authentication middleware validates JWT tokens on every request",
    "Rate limiting enforces 100 req/s per user by default",
    "Audit logs capture all write operations to the event bus",
]
results = quick_search(documents, "authentication jwt", k=3)
# Returns ranked SearchResult objects with score and highlights
for r in results:
    print(f"{r.score:.3f} | {r.document.content[:80]}")
```

### Indexed Search

Build a persistent in-memory or disk-backed index for repeated queries:

```python
from codomyrmex.search import create_index, Document

index = create_index(backend="memory")  # or backend="disk"
for path in python_files:
    index.index(Document(id=path, content=open(path).read()))

results = index.search("trust gateway event bus", k=10)
```

### Fuzzy Matching

Tolerate typos and approximate names in user queries:

```python
from codomyrmex.search import FuzzyMatcher

matcher = FuzzyMatcher()
candidates = ["trust_gateway", "mcp_bridge", "event_schema", "collaboration"]
matches = matcher.match("trst_gatway", candidates, threshold=0.7)
# Returns: [("trust_gateway", 0.89), ...]
```

### File Pattern Search

Search file paths by pattern with fuzzy tolerance:

```python
from codomyrmex.search import search_files

results = search_files("pai.md", root="src/codomyrmex/", fuzzy=True)
# Returns all PAI.md paths across all modules
```

## MCP Tools

The following tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.search_documents` | Quick full-text search across a list of text strings | Safe | search |
| `codomyrmex.search_index_query` | Build an index from documents, then query it | Safe | search |
| `codomyrmex.search_fuzzy` | Fuzzy-match a query against a list of candidate strings | Safe | search |

### MCP Tool Usage Examples

**Quick search across strings:**
```python
result = mcp_call("codomyrmex.search_documents", {
    "query": "publish_event trust level",
    "documents": ["...file content 1...", "...file content 2..."],
    "top_k": 5
})
# Returns:
# {
#   "status": "ok",
#   "query": "publish_event trust level",
#   "results": [
#     {"doc_id": "0", "score": 0.82, "snippet": "...", "highlights": ["publish_event"]}
#   ]
# }
```

**Index and query:**
```python
result = mcp_call("codomyrmex.search_index_query", {
    "query": "event bus integration",
    "documents": ["..."], "top_k": 10
})
```

**Fuzzy match:**
```python
result = mcp_call("codomyrmex.search_fuzzy", {
    "query": "trst_gatway",
    "candidates": ["trust_gateway", "mcp_bridge", "event_schema"],
    "threshold": 0.7
})
# Returns: {"status": "ok", "matches": [["trust_gateway", 0.89]]}
```

## PAI Algorithm Phase Mapping

| Phase | Search Contribution | Key Functions |
|-------|---------------------|---------------|
| **OBSERVE** (1/7) | Find relevant code, files, and patterns in the codebase | `quick_search()`, `search_files()`, `search_index_query` MCP |
| **THINK** (2/7) | Retrieve past work, related PRDs, and prior Algorithm reflections | `FuzzyMatcher`, `search_documents` MCP |
| **VERIFY** (6/7) | Confirm absence of prohibited patterns (anti-criteria verification) | `quick_search()` with regex patterns |

### Concrete PAI Usage Pattern

PAI OBSERVE phase context recovery uses search to find prior work:

```python
# PAI OBSERVE — CONTEXT RECOVERY step
# Find prior PRDs matching current task keywords
result = mcp_call("codomyrmex.search_documents", {
    "query": "trust gateway event bus integration",
    "documents": [open(p).read() for p in prd_files],
    "top_k": 3
})
# Top result guides which PRD to load for context resumption
```

PAI VERIFY anti-criterion checks use search to confirm absence:

```python
# PAI VERIFY — "No TODO(v0.2.0) comments remain in trust_gateway.py"
result = mcp_call("codomyrmex.search_documents", {
    "query": "TODO(v0.2.0)",
    "documents": [open("src/codomyrmex/agents/pai/trust_gateway.py").read()],
    "top_k": 1
})
assert result["results"] == [], "Anti-criterion violated: TODO(v0.2.0) found"
```

## PAI Configuration

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `CODOMYRMEX_SEARCH_MAX_RESULTS` | `50` | Default maximum results per query |
| `CODOMYRMEX_SEARCH_INDEX_BACKEND` | `memory` | Index backend: `memory` or `disk` |
| `CODOMYRMEX_SEARCH_FUZZY_THRESHOLD` | `0.6` | Minimum similarity score for fuzzy matches |

## PAI Best Practices

1. **Use `search_documents` for ad-hoc queries, `search_index_query` for repeated searches**:
   Building an index has upfront cost; if you'll query the same corpus more than 3 times in
   a session, build an index first.

2. **Leverage search for VERIFY anti-criteria**: Any anti-criterion of the form "X pattern
   must not appear" is cheapest to verify with `search_documents` (query = the forbidden
   pattern, assert empty results).

3. **Combine with Glob/Grep for fast file discovery**: Use native Grep for simple regex
   matches on disk; use `search_documents` when relevance ranking matters (multiple
   documents, need the best match, not just any match).

## Architecture Role

**Core Layer** — Primary codebase exploration tool consumed by all agent types. Used by
`agents/` (Explore subagent), `documents/` (content search), and MCP `search_code` tool.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
