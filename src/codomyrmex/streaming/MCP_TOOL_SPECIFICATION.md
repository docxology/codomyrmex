# Streaming - MCP Tool Specification

This document defines the Model Context Protocol tools for the Streaming module, covering stream lifecycle management, event publishing, subscription control, and status monitoring.

## General Considerations

- **Async Operations**: All underlying stream operations are async. The MCP tools abstract this for synchronous invocation.
- **Event Persistence**: In-memory streams buffer a configurable number of recent events. Events are not persisted to disk.
- **Topic Routing**: Events can target specific topics or broadcast to all subscribers.

---

## Tool: `stream_create`

### 1. Tool Purpose and Description

Creates a new named stream instance of the specified type (in-memory, SSE, or topic-based).

### 2. Invocation Name

`stream_create`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `name` | `string` | Yes | Unique stream name | `"order-events"` |
| `stream_type` | `string` | No | `"in_memory"`, `"sse"`, or `"topic"` (default: `"in_memory"`) | `"sse"` |
| `buffer_size` | `integer` | No | Max events to buffer (default: 1000) | `500` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"created"` or `"error"` | `"created"` |
| `stream_name` | `string` | Name of the created stream | `"order-events"` |
| `stream_type` | `string` | Type of stream created | `"sse"` |

### 5. Error Handling

- **Duplicate Name**: Returns error if a stream with the same name already exists.
- **Invalid Type**: Returns error if `stream_type` is not recognized.

### 6. Idempotency

- **Not Idempotent**: Creating the same name twice returns an error.

### 7. Usage Examples

```json
{
  "tool_name": "stream_create",
  "arguments": {
    "name": "notifications",
    "stream_type": "topic",
    "buffer_size": 200
  }
}
```

### 8. Security Considerations

- Stream names should not contain sensitive information as they may appear in logs.

---

## Tool: `stream_publish`

### 1. Tool Purpose and Description

Publishes an event to a named stream, optionally targeting a specific topic.

### 2. Invocation Name

`stream_publish`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `stream_name` | `string` | Yes | Target stream | `"order-events"` |
| `data` | `any` | Yes | Event payload (must be JSON-serializable) | `{"order_id": 42}` |
| `event_type` | `string` | No | Event type (default: `"message"`) | `"error"` |
| `topic` | `string` | No | Topic for topic-based streams | `"orders.created"` |
| `metadata` | `object` | No | Additional event metadata | `{"source": "api"}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"published"` or `"error"` | `"published"` |
| `event_id` | `string` | UUID of the published event | `"a1b2c3d4-..."` |
| `timestamp` | `string` | ISO timestamp | `"2026-02-05T10:00:00Z"` |

### 5. Error Handling

- **Stream Not Found**: Returns error if stream_name does not exist.
- **Serialization Error**: Returns error if data is not JSON-serializable.

### 6. Idempotency

- **Not Idempotent**: Each call creates a new event with a unique ID.

### 7. Usage Examples

```json
{
  "tool_name": "stream_publish",
  "arguments": {
    "stream_name": "order-events",
    "data": {"order_id": 42, "status": "completed"},
    "event_type": "message",
    "topic": "orders.completed"
  }
}
```

### 8. Security Considerations

- Validate `data` payloads to prevent oversized events from exhausting memory buffers.
- Sensitive data in events should be encrypted or redacted before publishing.

---

## Tool: `stream_subscribe`

### 1. Tool Purpose and Description

Creates a subscription to a named stream, optionally filtered by topic.

### 2. Invocation Name

`stream_subscribe`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `stream_name` | `string` | Yes | Stream to subscribe to | `"order-events"` |
| `topic` | `string` | No | Topic filter (default: `"*"` for all) | `"orders.created"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"subscribed"` or `"error"` | `"subscribed"` |
| `subscription_id` | `string` | UUID of the subscription | `"sub-e5f6..."` |
| `stream_name` | `string` | Stream subscribed to | `"order-events"` |
| `topic` | `string` | Active topic filter | `"orders.created"` |

### 5. Error Handling

- **Stream Not Found**: Returns error if stream_name does not exist.

### 6. Idempotency

- **Not Idempotent**: Each call creates a new subscription.

### 7. Usage Examples

```json
{
  "tool_name": "stream_subscribe",
  "arguments": {
    "stream_name": "order-events",
    "topic": "orders.created"
  }
}
```

### 8. Security Considerations

- Subscriptions should be cleaned up when no longer needed to prevent memory leaks.
- Consider access control to restrict which topics a caller can subscribe to.

---

## Tool: `stream_status`

### 1. Tool Purpose and Description

Returns statistics and metadata about a stream including subscriber count, buffer usage, and recent event counts.

### 2. Invocation Name

`stream_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `stream_name` | `string` | No | Specific stream (default: all streams) | `"order-events"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `streams` | `array[object]` | Status of each stream | See below |
| `total_streams` | `integer` | Number of active streams | `3` |

Each stream object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `name` | `string` | Stream name | `"order-events"` |
| `type` | `string` | Stream type | `"in_memory"` |
| `subscriber_count` | `integer` | Active subscriptions | `5` |
| `buffered_events` | `integer` | Events in buffer | `42` |
| `buffer_capacity` | `integer` | Max buffer size | `1000` |
| `topics` | `array[string]` | Active topics (topic streams only) | `["orders.created"]` |

### 5. Error Handling

- Returns empty `streams` array if no streams exist or name is not found.

### 6. Idempotency

- **Idempotent**: Yes. Read-only query.

### 7. Usage Examples

```json
{
  "tool_name": "stream_status",
  "arguments": {
    "stream_name": "order-events"
  }
}
```

### 8. Security Considerations

- Read-only operation. Subscriber counts and topic names may reveal system architecture.

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Home**: [Root README](../../../README.md)
