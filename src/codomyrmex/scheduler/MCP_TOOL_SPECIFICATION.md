# Scheduler - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools exposed by the `scheduler` module for creating, listing, cancelling, and inspecting scheduled jobs.

## General Considerations

- Jobs execute callable functions in a thread pool. MCP callers schedule by referencing registered task names or inline definitions.
- The scheduler runs as a background thread; `start()` must be called before jobs will fire.
- Cron expressions use standard 5-field format: `minute hour day_of_month month day_of_week`.

---

## Tool: `schedule_job`

### 1. Tool Purpose and Description
Create a new scheduled job with a specified trigger type and parameters.

### 2. Invocation Name
`schedule_job`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `name` | `string` | Yes | Human-readable job name | `"nightly_backup"` |
| `task` | `string` | Yes | Registered task function name | `"run_backup"` |
| `trigger_type` | `string` | Yes | One of: `once`, `interval`, `cron` | `"interval"` |
| `trigger_config` | `object` | Yes | Trigger-specific configuration (see below) | `{"hours": 1}` |
| `args` | `array` | No | Positional arguments for the task | `["/data"]` |
| `kwargs` | `object` | No | Keyword arguments for the task | `{"compress": true}` |
| `max_runs` | `integer` | No | Maximum number of executions (null = unlimited) | `10` |

**`trigger_config` by type:**
- `once`: `{"run_at": "2026-02-05T15:00:00"}` (ISO 8601)
- `interval`: `{"seconds": 0, "minutes": 0, "hours": 1, "days": 0}`
- `cron`: `{"expression": "0 */2 * * *"}`

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `job_id` | `string` | Unique job identifier | `"job_1_1738764000"` |
| `name` | `string` | Confirmed job name | `"nightly_backup"` |
| `next_run` | `string \| null` | ISO 8601 next execution time | `"2026-02-05T16:00:00"` |
| `status` | `string` | Initial status | `"pending"` |

### 5. Error Handling
- `{"error": "Unknown task: <name>"}` if the task function is not registered.
- `{"error": "Invalid cron expression: <expr>"}` for malformed cron strings.

### 6. Idempotency
No. Each call creates a new job with a unique ID.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "schedule_job",
  "arguments": {
    "name": "hourly_cleanup",
    "task": "cleanup_temp_files",
    "trigger_type": "interval",
    "trigger_config": {"hours": 1},
    "max_runs": 24
  }
}
```

### 8. Security Considerations
- Task names must resolve to registered functions only. Arbitrary code execution is not permitted.
- Validate `trigger_config` values are positive numbers.

---

## Tool: `list_jobs`

### 1. Tool Purpose and Description
List all scheduled jobs, optionally filtered by status.

### 2. Invocation Name
`list_jobs`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `status` | `string` | No | Filter by status: `pending`, `running`, `completed`, `failed`, `cancelled` | `"pending"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `jobs` | `array[object]` | List of job summaries | See below |
| `total` | `integer` | Total matching jobs | `3` |

Each job object:

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `job_id` | `string` | Unique identifier |
| `name` | `string` | Job name |
| `status` | `string` | Current status |
| `trigger_type` | `string` | Trigger type |
| `next_run` | `string \| null` | Next scheduled run |
| `run_count` | `integer` | Total executions |
| `last_run` | `string \| null` | Last execution time |

### 5. Error Handling
- Invalid `status` values return `{"error": "Unknown status: <value>"}`.

### 6. Idempotency
Yes. Read-only operation.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "list_jobs",
  "arguments": {
    "status": "failed"
  }
}
```

### 8. Security Considerations
- Job listings may reveal internal task names. Restrict to authorized callers.

---

## Tool: `cancel_job`

### 1. Tool Purpose and Description
Cancel a scheduled job by its ID. The job will not execute again.

### 2. Invocation Name
`cancel_job`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `job_id` | `string` | Yes | The job ID to cancel | `"job_1_1738764000"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `cancelled` | `boolean` | Whether the job was found and cancelled | `true` |
| `job_id` | `string` | Confirmed job ID | `"job_1_1738764000"` |

### 5. Error Handling
- Returns `{"cancelled": false}` if the job ID does not exist.

### 6. Idempotency
Yes. Cancelling an already-cancelled job returns `true` without error.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "cancel_job",
  "arguments": {
    "job_id": "job_1_1738764000"
  }
}
```

### 8. Security Considerations
- Callers should only cancel their own jobs. Implement ownership checks in production.

---

## Tool: `job_status`

### 1. Tool Purpose and Description
Get detailed status and execution history for a specific job.

### 2. Invocation Name
`job_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `job_id` | `string` | Yes | The job ID to query | `"job_1_1738764000"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `job_id` | `string` | Job identifier | `"job_1_1738764000"` |
| `name` | `string` | Job name | `"hourly_cleanup"` |
| `status` | `string` | Current status | `"completed"` |
| `trigger_type` | `string` | Trigger type | `"interval"` |
| `created_at` | `string` | ISO 8601 creation time | `"2026-02-05T10:00:00"` |
| `last_run` | `string \| null` | Last execution time | `"2026-02-05T14:00:00"` |
| `next_run` | `string \| null` | Next scheduled run | `"2026-02-05T15:00:00"` |
| `run_count` | `integer` | Total executions | `4` |
| `max_runs` | `integer \| null` | Max allowed runs | `24` |
| `error` | `string \| null` | Last error message | `null` |

### 5. Error Handling
- Returns `{"error": "Job not found: <id>"}` for unknown IDs.

### 6. Idempotency
Yes. Read-only operation.

### 7. Usage Examples (JSON)

```json
{
  "tool_name": "job_status",
  "arguments": {
    "job_id": "job_1_1738764000"
  }
}
```

### 8. Security Considerations
- Error messages may contain stack traces. Sanitize before exposing to untrusted callers.

---

## Navigation Links

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
