# soul — Technical Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Wrap the `soul-agent` library to expose persistent markdown-file-based LLM agent memory as a first-class Codomyrmex module with a consistent Python API, MCP tools, and zero-database footprint.

---

## Core Classes

### `SoulAgent`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(soul_path, memory_path, provider, api_key, model, base_url)` | Construct wrapper; raises `SoulImportError` if soul-agent absent |
| `ask` | `(question: str, remember: bool = True) -> str` | Query LLM; optionally persist to MEMORY.md |
| `remember` | `(note: str) -> None` | Append note to MEMORY.md |
| `reset_conversation` | `() -> None` | Clear in-session history (MEMORY.md unchanged) |
| `memory_stats` | `() -> dict[str, Any]` | File size statistics |

**Module-level constant**: `HAS_SOUL: bool` — `True` when `soul-agent` is importable.

---

## File Storage Protocol

soul.py uses two markdown files:

| File | Default | Content | Limit |
|------|---------|---------|-------|
| SOUL.md | `SOUL.md` (cwd) | Agent name, system prompt, personality | No limit |
| MEMORY.md | `MEMORY.md` (cwd) | Timestamped conversation log | Auto-truncated at 6 000 chars |

Truncation preserves the **most recent entries** — oldest are removed first.

Files are human-readable and git-trackable.

---

## Provider Compatibility

| Provider string | Backend | API key env var |
|----------------|---------|-----------------|
| `anthropic` | Anthropic Claude | `ANTHROPIC_API_KEY` |
| `openai` | OpenAI GPT | `OPENAI_API_KEY` |
| `openai-compatible` | Any HTTP endpoint (e.g. Ollama) | Provider-specific |

Default provider: `anthropic`.

---

## MCP Tool Architecture

Each MCP tool is **stateless** — a fresh `SoulAgent` is constructed per call. This is correct by design: persistent state lives in the markdown files, not in Python objects. The calling pattern is:

```
Tool call → SoulAgent(soul_path, memory_path, ...) → soul.py reads files → LLM call → soul.py writes files → result dict returned
```

Tools that do not require LLM access (`soul_status`, `soul_init`) operate directly on the filesystem and do not require `soul-agent` to be installed.

---

## Error Handling

| Exception | When Raised |
|---|---|
| `SoulImportError` | soul-agent not installed; construction attempted |
| `SoulError` | soul.py Agent construction failed (bad provider, etc.) |
| `SoulProviderError` | LLM call failed (network error, quota exceeded, etc.) |
| `SoulMemoryError` | File write to MEMORY.md failed (permissions, disk full) |

All MCP tools catch `SoulError` subclasses and return `{"status": "error", "message": str}`.

---

## Dependencies

| Package | Version | Purpose | Optional |
|---|---|---|---|
| `soul-agent` | >= 0.1.4 | Core agent + memory | Yes (`uv sync --extra soul`) |
| Python | >= 3.10 | soul.py requirement | No |

---

## Design Principles

1. **Import guard over silent fallback** — `SoulImportError` is raised; no placeholder classes.
2. **Stateless MCP tools** — soul.py's file-based design maps naturally to stateless HTTP calls.
3. **Env-key resolution** — API keys read from well-known env vars; no hardcoded defaults.
4. **No overwrite** — `soul_init` skips existing files; idempotent by design.

---

## Thread Safety

- `SoulAgent` instances are not thread-safe (soul.py makes no guarantees).
- MCP tools create new instances per call, so concurrent tool calls to different path pairs are safe.
- Concurrent calls sharing the same `memory_path` may cause interleaved writes.

---

## Navigation

- **Human Guide**: [README.md](README.md)
- **Agent Access**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Parent**: [codomyrmex](../SPEC.md)
