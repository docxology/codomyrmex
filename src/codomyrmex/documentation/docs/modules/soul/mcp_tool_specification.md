# soul — MCP Tool Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

This module exposes **5 MCP tools** via the `@mcp_tool` decorator, auto-discovered by the PAI MCP bridge.

---

## soul_status

**Category**: soul | **Trust**: OBSERVED | **Requires soul-agent**: No

Return file statistics for SOUL.md and MEMORY.md.

### Arguments

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `soul_path` | `str` | No | `"SOUL.md"` | Path to SOUL.md |
| `memory_path` | `str` | No | `"MEMORY.md"` | Path to MEMORY.md |

### Returns

```json
{
  "status": "success",
  "soul_path": "SOUL.md",
  "memory_path": "MEMORY.md",
  "soul_exists": true,
  "soul_size_bytes": 312,
  "memory_exists": true,
  "memory_size_bytes": 1840
}
```

---

## soul_init

**Category**: soul | **Trust**: OBSERVED | **Requires soul-agent**: No

Create default SOUL.md and MEMORY.md for a new agent. Does **not** overwrite existing files.

### Arguments

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `soul_path` | `str` | No | `"SOUL.md"` | Destination for SOUL.md |
| `memory_path` | `str` | No | `"MEMORY.md"` | Destination for MEMORY.md |
| `agent_name` | `str` | No | `"Assistant"` | Agent name in SOUL.md header |
| `description` | `str` | No | `"A helpful AI assistant..."` | System prompt content |

### Returns

```json
{
  "status": "success",
  "created": ["SOUL.md", "MEMORY.md"],
  "skipped": []
}
```

Or, when files already exist:

```json
{
  "status": "success",
  "created": [],
  "skipped": ["SOUL.md", "MEMORY.md"]
}
```

---

## soul_ask

**Category**: soul | **Trust**: TRUSTED | **Requires soul-agent**: Yes

Ask a persistent markdown-memory agent a question.

### Arguments

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `question` | `str` | **Yes** | — | Question or statement to send |
| `soul_path` | `str` | No | `"SOUL.md"` | Agent identity file |
| `memory_path` | `str` | No | `"MEMORY.md"` | Conversation log |
| `provider` | `str` | No | `"anthropic"` | LLM provider |
| `model` | `str \ | None` | No | `None` Model override |
| `base_url` | `str \ | None` | No | `None` Endpoint for openai-compatible |
| `remember` | `bool` | No | `True` | Persist exchange to MEMORY.md |

### Returns

```json
{
  "status": "success",
  "response": "Hello! Nice to meet you.",
  "remembered": true
}
```

---

## soul_remember

**Category**: soul | **Trust**: TRUSTED | **Requires soul-agent**: Yes

Manually append a note to MEMORY.md without an LLM round-trip.

### Arguments

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `note` | `str` | **Yes** | — | Text to append to MEMORY.md |
| `soul_path` | `str` | No | `"SOUL.md"` | Agent identity file |
| `memory_path` | `str` | No | `"MEMORY.md"` | Conversation log |
| `provider` | `str` | No | `"anthropic"` | LLM provider (for SoulAgent init) |

### Returns

```json
{
  "status": "success",
  "memory_path": "MEMORY.md"
}
```

---

## soul_reset

**Category**: soul | **Trust**: TRUSTED | **Requires soul-agent**: Yes

Reset in-session conversation history.  MEMORY.md is **not** modified.

### Arguments

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `soul_path` | `str` | No | `"SOUL.md"` | Agent identity file |
| `memory_path` | `str` | No | `"MEMORY.md"` | Conversation log |
| `provider` | `str` | No | `"anthropic"` | LLM provider |

### Returns

```json
{
  "status": "success",
  "note": "In-session history cleared. MEMORY.md is unchanged."
}
```

---

## Error Handling

All tools return an error dict on failure:

```json
{
  "status": "error",
  "message": "soul-agent is not installed. Run: uv sync --extra soul"
}
```

---

## Navigation

- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Human Guide**: [README.md](README.md)
- **Parent**: [codomyrmex package](../README.md)
