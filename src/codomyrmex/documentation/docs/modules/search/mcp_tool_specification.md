# Search - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools exposed by the `search` module. These tools are defined in `mcp_tools.py` and exposed via the `@mcp_tool` decorator.

## General Considerations

- Search uses TF-IDF scoring with automatic highlight generation around matching terms.
- Fuzzy matching uses Levenshtein distance for approximate string matching.
- All tools operate on in-memory data passed as arguments.

---

## Tool: `search_documents`

### 1. Tool Purpose and Description
Perform a quick full-text search across a list of text strings using TF-IDF scoring.

### 2. Invocation Name
`codomyrmex.search_documents`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `query` | `string` | Yes | Search query string | `"rate limiting API"` |
| `documents` | `array[string]` | Yes | List of plain-text strings to search | `["Rate limiting protects...", "API docs..."]` |
| `top_k` | `integer` | No | Maximum number of results to return (default: 5) | `3` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `query` | `string` | The original query | `"rate limiting API"` |
| `results` | `array[object]` | Ranked search results | See below |

Each result object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `doc_id` | `string` | Document identifier | `"0"` |
| `score` | `number` | TF-IDF relevance score | `3.72` |
| `snippet` | `string` | First 200 characters of content | `"Rate limiting protects..."` |
| `highlights` | `array[string]` | Context snippets around matches | `["...rate limiting API..."]` |

### 5. Error Handling
- Returns `{"status": "error", "error": "<message>"}` on failures.

### 6. Idempotency
Yes. Search is read-only.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "codomyrmex.search_documents",
  "arguments": {
    "query": "rate limiting API",
    "documents": ["Rate limiting protects APIs", "Authentication guide", "API rate limits"],
    "top_k": 3
  }
}
```

### 8. Security Considerations
- Highlights contain excerpts from document content. Do not expose if documents contain sensitive data.
- Query strings are tokenized and sanitized internally; no injection risk.

---

## Tool: `search_index_query`

### 1. Tool Purpose and Description
Build an in-memory search index from document strings and search it. Combines index creation and querying in one operation.

### 2. Invocation Name
`codomyrmex.search_index_query`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `query` | `string` | Yes | Search query string | `"machine learning"` |
| `documents` | `array[string]` | Yes | List of plain-text strings to index | `["Python ML guide", "Deep learning tutorial"]` |
| `top_k` | `integer` | No | Maximum results to return (default: 10) | `5` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `query` | `string` | The original query | `"machine learning"` |
| `index_size` | `integer` | Number of documents indexed | `2` |
| `results` | `array[object]` | Ranked search results (same structure as `search_documents`) | `[...]` |

### 5. Error Handling
- Returns `{"status": "error", "error": "<message>"}` on failures.

### 6. Idempotency
Yes. Creates a temporary index and searches it; no persistent state.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "codomyrmex.search_index_query",
  "arguments": {
    "query": "deployment guide",
    "documents": ["Production deployment steps", "Development setup guide", "Deployment best practices"],
    "top_k": 2
  }
}
```

### 8. Security Considerations
- Same as `search_documents`. Content is held in memory only during the call.

---

## Tool: `search_fuzzy`

### 1. Tool Purpose and Description
Find the best fuzzy match for a query string among a list of candidate strings using Levenshtein distance.

### 2. Invocation Name
`codomyrmex.search_fuzzy`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `query` | `string` | Yes | String to match against | `"pythn"` |
| `candidates` | `array[string]` | Yes | List of candidate strings | `["python", "java", "rust"]` |
| `threshold` | `number` | No | Minimum similarity score (0.0-1.0, default: 0.6) | `0.7` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `query` | `string` | The original query | `"pythn"` |
| `best_match` | `string` or `null` | Best matching candidate above threshold | `"python"` |
| `matches` | `array[object]` | All matches above threshold, sorted by score | See below |

Each match object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `candidate` | `string` | Matched candidate string | `"python"` |
| `score` | `number` | Similarity score (0.0-1.0) | `0.83` |

### 5. Error Handling
- Returns `{"status": "error", "error": "<message>"}` on failures.

### 6. Idempotency
Yes. Fuzzy matching is stateless and deterministic.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "codomyrmex.search_fuzzy",
  "arguments": {
    "query": "contanerization",
    "candidates": ["containerization", "configuration", "compilation"],
    "threshold": 0.7
  }
}
```

### 8. Security Considerations
- No data is persisted. Candidates are processed in memory.

---

## Navigation Links

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
