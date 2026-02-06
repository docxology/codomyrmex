# Search - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools exposed by the `search` module for full-text search, document indexing, and index management.

## General Considerations

- All tools operate on named index instances. If no index name is provided, the default in-memory index is used.
- Search uses TF-IDF scoring with automatic highlight generation around matching terms.
- Query strings support operators: `+term` (must include), `-term` (must exclude), `"phrase"` (exact match).

---

## Tool: `search_index`

### 1. Tool Purpose and Description
Search for documents matching a query string, returning ranked results with relevance scores and context highlights.

### 2. Invocation Name
`search_index`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `query` | `string` | Yes | Search query (supports +/- and phrase operators) | `'+python "machine learning"'` |
| `k` | `integer` | No | Maximum results to return (default: 10) | `5` |
| `index_name` | `string` | No | Target index instance (default: `"default"`) | `"documentation"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `results` | `array[object]` | Ranked search results | See below |
| `total_matches` | `integer` | Total candidate documents found | `42` |
| `query_parsed` | `object` | Parsed query structure | `{"terms": [], "must": ["python"]}` |

Each result object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `doc_id` | `string` | Document identifier | `"doc-001"` |
| `score` | `number` | TF-IDF relevance score | `3.72` |
| `highlights` | `array[string]` | Context snippets (max 3) | `["...python for machine learning..."]` |
| `metadata` | `object` | Document metadata | `{"author": "Smith"}` |

### 5. Error Handling
- Empty query returns `{"results": [], "total_matches": 0}`.
- Returns `{"error": "Index not found: <name>"}` for unknown index names.

### 6. Idempotency
Yes. Search is read-only.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "search_index",
  "arguments": {
    "query": "rate limiting API",
    "k": 3,
    "index_name": "documentation"
  }
}
```

### 8. Security Considerations
- Highlights contain excerpts from indexed content. Do not expose if documents contain sensitive data.
- Query strings are tokenized and sanitized internally; no injection risk.

---

## Tool: `search_add_document`

### 1. Tool Purpose and Description
Add or update a document in the search index. If a document with the same ID exists, it is re-indexed with the new content.

### 2. Invocation Name
`search_add_document`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `doc_id` | `string` | Yes | Unique document identifier | `"doc-001"` |
| `content` | `string` | Yes | Text content to index | `"Python rate limiting with token buckets"` |
| `metadata` | `object` | No | Arbitrary key-value metadata | `{"author": "Smith", "year": 2026}` |
| `index_name` | `string` | No | Target index instance (default: `"default"`) | `"documentation"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"indexed"` or `"re-indexed"` | `"indexed"` |
| `doc_id` | `string` | Confirmed document ID | `"doc-001"` |
| `token_count` | `integer` | Tokens extracted from content | `6` |

### 5. Error Handling
- `{"error": "Content must be a non-empty string"}` for blank or missing content.

### 6. Idempotency
Yes. Re-indexing the same content with the same ID produces identical index state.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "search_add_document",
  "arguments": {
    "doc_id": "readme-rate-limiting",
    "content": "Rate limiting protects APIs from abuse by throttling request frequency.",
    "metadata": {"module": "rate_limiting", "type": "readme"}
  }
}
```

### 8. Security Considerations
- Content is stored in-process memory. Sensitive documents should use encrypted-at-rest backends if available.
- Metadata is stored as-is. Do not include credentials or secrets.

---

## Tool: `search_create_index`

### 1. Tool Purpose and Description
Create a new named search index with optional tokenizer configuration.

### 2. Invocation Name
`search_create_index`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `index_name` | `string` | Yes | Name for the new index | `"project_docs"` |
| `backend` | `string` | No | Index backend type (default: `"memory"`) | `"memory"` |
| `tokenizer_config` | `object` | No | Tokenizer settings | `{"lowercase": true, "min_length": 3}` |

**`tokenizer_config` fields:**

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `lowercase` | `boolean` | `true` | Convert tokens to lowercase |
| `min_length` | `integer` | `2` | Minimum token character length |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"created"` | `"created"` |
| `index_name` | `string` | Confirmed index name | `"project_docs"` |
| `backend` | `string` | Backend type in use | `"memory"` |

### 5. Error Handling
- `{"error": "Index already exists: <name>"}` if the name is taken.
- `{"error": "Unknown backend: <value>"}` for unsupported backends.

### 6. Idempotency
No. Creating an index with an existing name returns an error. Use `search_add_document` to update content within an existing index.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "search_create_index",
  "arguments": {
    "index_name": "codebase_search",
    "tokenizer_config": {
      "lowercase": true,
      "min_length": 3
    }
  }
}
```

### 8. Security Considerations
- Index names should follow safe naming conventions (alphanumeric, hyphens, underscores).
- Each index consumes memory proportional to indexed content. Monitor total index count in production.

---

## Navigation Links

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
