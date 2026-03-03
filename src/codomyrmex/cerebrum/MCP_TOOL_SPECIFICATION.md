# Cerebrum -- MCP Tool Specification

This document specifies the MCP-discoverable tools exposed by the `cerebrum` module. These tools provide case-based reasoning capabilities through semantic retrieval and case storage in the CaseBase.

## General Considerations

- **Auto-Discovery**: Tools use the `@mcp_tool(category="cerebrum")` decorator and are auto-discovered via the MCP bridge.
- **Dependencies**: Requires the `cerebrum` module's `CaseBase`, `CaseRetriever`, and `Case` classes.
- **Error Handling**: All tools return `{"status": "error", "message": "..."}` on failure.

---

## Tool: `query_knowledge_base`

### 1. Tool Purpose and Description

Perform semantic retrieval from the CaseBase. Searches for cases matching a conceptual query and returns ranked results with similarity scores.

### 2. Invocation Name

`query_knowledge_base`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | The semantic concept or question to search for | `"error handling patterns"` |
| `limit` | `integer` | No | Maximum number of cases to return (default: 5) | `10` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `results` | `array` | List of matching case objects | `[{"id": "...", "features": {...}, "solution": "...", "similarity_score": 0.92}]` |
| `count` | `integer` | Number of results returned | `3` |
| `message` | `string` | Error description (only on error) | `"Knowledge base query failed: ..."` |

Each item in `results` contains:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Unique case identifier |
| `features` | `object` | Feature dictionary of the case |
| `solution` | `string` | The paired resolution or insight |
| `similarity_score` | `number` | Similarity to the query (0.0--1.0) |

### 5. Error Handling

- CaseBase initialization failures return an error status with the exception message.
- Retrieval failures (e.g., empty case base, invalid query) return an error status.

### 6. Idempotency

- **Idempotent**: Yes (for the same case base state)
- **Explanation**: The same query against the same CaseBase content returns the same results. Results may differ if cases have been added or removed between calls.

### 7. Usage Examples

```json
{
  "tool_name": "query_knowledge_base",
  "arguments": {
    "query": "authentication middleware design",
    "limit": 3
  }
}
```

### 8. Security Considerations

- Query strings are used as feature filters and should be validated to prevent injection into the retrieval pipeline.
- Returned case data may contain sensitive solution information; consumers should handle results appropriately.

---

## Tool: `add_case_reference`

### 1. Tool Purpose and Description

Store intelligence context directly into the CaseBase. Creates a new case with a concept feature and a paired solution string.

### 2. Invocation Name

`add_case_reference`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `concept` | `string` | Yes | The problem or concept feature string | `"retry logic for HTTP 429"` |
| `solution` | `string` | Yes | The paired resolution or insight | `"Use exponential backoff with jitter, max 5 retries"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `message` | `string` | Confirmation or error description | `"Case stored successfully"` |
| `case_id` | `string` | Unique identifier of the stored case (only on success) | `"c8f2e1a0-..."` |

### 5. Error Handling

- CaseBase initialization failures return an error status.
- Case construction or storage failures return an error status with the exception message.

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Each call creates a new case with a unique ID, even if the same concept and solution are provided.

### 7. Usage Examples

```json
{
  "tool_name": "add_case_reference",
  "arguments": {
    "concept": "database connection pooling",
    "solution": "Use connection pool with max_size=20, timeout=30s, health_check_interval=60s"
  }
}
```

### 8. Security Considerations

- Both `concept` and `solution` are stored as-is in the CaseBase. Callers should avoid storing secrets, credentials, or PII.
- Input strings should be validated for length and content before storage.

---

## Navigation Links

- **Parent**: [Module README](./README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Home**: [Root README](../../../README.md)
