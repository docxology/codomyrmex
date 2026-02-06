# Rate Limiting - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools exposed by the `rate_limiting` module for checking, configuring, and monitoring API rate limits.

## General Considerations

- All tools operate on in-process limiter state. Distributed backends (Redis) require the `distributed` extra.
- Keys are arbitrary strings (user IDs, IP addresses, API key hashes).
- Thread-safe by design; safe to call from concurrent MCP tool invocations.

---

## Tool: `rate_limit_check`

### 1. Tool Purpose and Description
Check whether a request from a given key would be allowed under the current rate limit, without consuming quota.

### 2. Invocation Name
`rate_limit_check`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `key` | `string` | Yes | Identifier for the rate-limited entity | `"user-abc-123"` |
| `limiter_name` | `string` | No | Named limiter to check (default: `"default"`) | `"per_minute"` |
| `cost` | `integer` | No | Request cost in tokens (default: 1) | `5` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `allowed` | `boolean` | Whether the request would be permitted | `true` |
| `remaining` | `integer` | Remaining quota in current window | `42` |
| `limit` | `integer` | Total window limit | `100` |
| `reset_at` | `string` | ISO 8601 timestamp of window reset | `"2026-02-05T12:01:00Z"` |
| `retry_after` | `number \| null` | Seconds to wait if denied | `18.5` |

### 5. Error Handling
- Returns `{"error": "Limiter not found: <name>"}` if the named limiter does not exist.

### 6. Idempotency
Yes. Check is read-only and does not mutate quota state.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "rate_limit_check",
  "arguments": {
    "key": "user-abc-123",
    "limiter_name": "per_minute",
    "cost": 1
  }
}
```

### 8. Security Considerations
- Keys should not contain PII in logs. Hash or anonymize before passing.
- No filesystem or network access required.

---

## Tool: `rate_limit_configure`

### 1. Tool Purpose and Description
Create or reconfigure a named rate limiter with a specified algorithm and parameters.

### 2. Invocation Name
`rate_limit_configure`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `limiter_name` | `string` | Yes | Name for the limiter | `"api_calls"` |
| `algorithm` | `string` | Yes | One of: `fixed_window`, `sliding_window`, `token_bucket` | `"sliding_window"` |
| `limit` | `integer` | Yes | Maximum requests per window (or bucket capacity) | `100` |
| `window_seconds` | `integer` | Yes | Window duration in seconds | `60` |
| `refill_rate` | `number` | No | Tokens per refill interval (token_bucket only) | `10.0` |
| `refill_interval` | `number` | No | Seconds between refills (token_bucket only, default: 1.0) | `1.0` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"created"` or `"updated"` | `"created"` |
| `limiter_name` | `string` | Confirmed limiter name | `"api_calls"` |
| `algorithm` | `string` | Algorithm in use | `"sliding_window"` |

### 5. Error Handling
- Returns `{"error": "Unknown algorithm: <value>"}` for invalid algorithm names.

### 6. Idempotency
No. Reconfiguring a limiter resets all existing quota state for that limiter.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "rate_limit_configure",
  "arguments": {
    "limiter_name": "burst_control",
    "algorithm": "token_bucket",
    "limit": 50,
    "window_seconds": 30,
    "refill_rate": 5.0
  }
}
```

### 8. Security Considerations
- Only authorized callers should configure limits. Misconfiguration can disable rate protection.
- Validate `limit` and `window_seconds` are positive integers.

---

## Tool: `rate_limit_status`

### 1. Tool Purpose and Description
Retrieve current usage statistics for a key across one or all configured limiters.

### 2. Invocation Name
`rate_limit_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `key` | `string` | Yes | Identifier to query | `"user-abc-123"` |
| `limiter_name` | `string` | No | Specific limiter (omit for all) | `"per_minute"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `key` | `string` | Queried key | `"user-abc-123"` |
| `limiters` | `object` | Map of limiter name to status | See below |

Each limiter entry:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `allowed` | `boolean` | Current allow state | `true` |
| `remaining` | `integer` | Remaining quota | `73` |
| `limit` | `integer` | Window limit | `100` |
| `reset_at` | `string \| null` | ISO 8601 reset time | `"2026-02-05T12:01:00Z"` |

### 5. Error Handling
- Returns empty `limiters` object if no limiters are configured.

### 6. Idempotency
Yes. Read-only operation.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "rate_limit_status",
  "arguments": {
    "key": "user-abc-123"
  }
}
```

### 8. Security Considerations
- Exposes quota details per key. Restrict access to authorized monitoring contexts.

---

## Navigation Links

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
