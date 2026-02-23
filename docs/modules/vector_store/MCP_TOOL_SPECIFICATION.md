# Vector Store - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools exposed by the `vector_store` module for adding, searching, deleting, and counting vector embeddings.

## General Considerations

- All tools operate on a named vector store instance. If no store name is provided, the default in-memory store is used.
- Embeddings are arrays of floats. Dimension consistency is the caller's responsibility.
- Search returns results ordered by similarity score (highest first for cosine/dot, lowest first for euclidean).

---

## Tool: `vector_add`

### 1. Tool Purpose and Description
Add a vector embedding with optional metadata to the store. Overwrites if the ID already exists.

### 2. Invocation Name
`vector_add`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `id` | `string` | Yes | Unique identifier for the vector | `"doc-abc-123"` |
| `embedding` | `array[number]` | Yes | The embedding vector | `[0.1, 0.2, 0.3, 0.4]` |
| `metadata` | `object` | No | Arbitrary key-value metadata | `{"source": "paper", "year": 2026}` |
| `store_name` | `string` | No | Target store instance (default: `"default"`) | `"project_embeddings"` |
| `namespace` | `string` | No | Namespace within the store | `"chapter-1"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"added"` or `"updated"` | `"added"` |
| `id` | `string` | Confirmed vector ID | `"doc-abc-123"` |
| `dimension` | `integer` | Embedding dimensionality | `4` |

### 5. Error Handling
- `{"error": "Embedding must be a non-empty array of numbers"}` for invalid input.

### 6. Idempotency
Yes. Adding the same ID with the same embedding and metadata produces identical state.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "vector_add",
  "arguments": {
    "id": "doc-abc-123",
    "embedding": [0.1, 0.2, 0.3, 0.4],
    "metadata": {"source": "arxiv", "title": "Attention Is All You Need"}
  }
}
```

### 8. Security Considerations
- Metadata is stored as-is. Do not include secrets or credentials in metadata fields.
- Large embeddings (>4096 dimensions) may impact memory. Monitor store size.

---

## Tool: `vector_search`

### 1. Tool Purpose and Description
Perform similarity search against stored vectors using a query embedding.

### 2. Invocation Name
`vector_search`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `query` | `array[number]` | Yes | Query embedding vector | `[0.1, 0.2, 0.3, 0.4]` |
| `k` | `integer` | No | Number of results to return (default: 10) | `5` |
| `store_name` | `string` | No | Target store instance (default: `"default"`) | `"project_embeddings"` |
| `namespace` | `string` | No | Namespace to search within | `"chapter-1"` |
| `metadata_filter` | `object` | No | Key-value pairs that must match in metadata | `{"source": "arxiv"}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `results` | `array[object]` | Ordered search results | See below |
| `total_searched` | `integer` | Vectors evaluated | `150` |

Each result object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `id` | `string` | Vector identifier | `"doc-abc-123"` |
| `score` | `number` | Similarity score | `0.95` |
| `metadata` | `object` | Associated metadata | `{"source": "arxiv"}` |

### 5. Error Handling
- `{"error": "Query embedding must be a non-empty array"}` for invalid input.
- Returns empty `results` if the store is empty.

### 6. Idempotency
Yes. Search is read-only.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "vector_search",
  "arguments": {
    "query": [0.1, 0.2, 0.3, 0.4],
    "k": 3,
    "metadata_filter": {"source": "arxiv"}
  }
}
```

### 8. Security Considerations
- Embeddings in results may allow reconstruction of original content. Consider omitting from responses to untrusted callers.

---

## Tool: `vector_delete`

### 1. Tool Purpose and Description
Remove a vector from the store by its ID.

### 2. Invocation Name
`vector_delete`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `id` | `string` | Yes | Vector ID to delete | `"doc-abc-123"` |
| `store_name` | `string` | No | Target store instance (default: `"default"`) | `"project_embeddings"` |
| `namespace` | `string` | No | Namespace containing the vector | `"chapter-1"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `deleted` | `boolean` | Whether the vector was found and removed | `true` |
| `id` | `string` | Confirmed vector ID | `"doc-abc-123"` |

### 5. Error Handling
- Returns `{"deleted": false}` if the ID does not exist. No error raised.

### 6. Idempotency
Yes. Deleting a non-existent ID is a no-op.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "vector_delete",
  "arguments": {
    "id": "doc-abc-123"
  }
}
```

### 8. Security Considerations
- Deletion is permanent. No soft-delete or undo capability in the base implementation.

---

## Tool: `vector_count`

### 1. Tool Purpose and Description
Get the total number of vectors stored in a store or namespace.

### 2. Invocation Name
`vector_count`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `store_name` | `string` | No | Target store instance (default: `"default"`) | `"project_embeddings"` |
| `namespace` | `string` | No | Namespace to count within | `"chapter-1"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `count` | `integer` | Total number of vectors | `1523` |
| `store_name` | `string` | Queried store | `"default"` |

### 5. Error Handling
- Returns `{"count": 0}` for empty or non-existent stores.

### 6. Idempotency
Yes. Read-only operation.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "vector_count",
  "arguments": {
    "store_name": "project_embeddings",
    "namespace": "chapter-1"
  }
}
```

### 8. Security Considerations
- Count alone does not expose vector content. Safe for monitoring dashboards.

---

## Navigation Links

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
