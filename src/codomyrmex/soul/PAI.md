# soul — PAI Integration

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## PAI Algorithm Phase Mapping

### OBSERVE Phase

- **`soul_status`**: Check whether SOUL.md and MEMORY.md exist and how large they are before deciding whether to initialise or continue an agent session. Zero dependencies — works without soul-agent installed.

### PLAN Phase

- **`soul_init`**: Create SOUL.md and MEMORY.md with a custom agent name and description. Idempotent — safe to call when files may already exist. Use this at the start of a new agent project before any `soul_ask` calls.

### BUILD Phase

- **`soul_ask` (remember=True)**: Inject structured information into the agent's persistent memory by phrasing statements as facts. Example: `soul_ask("The project uses Python 3.12 and uv for dependency management.")`.
- **`soul_remember`**: Directly append a note without triggering an LLM call. More efficient than `soul_ask` when you do not need a response.

### EXECUTE Phase

- **`soul_ask`**: Primary interaction tool during agent execution. Each call reads SOUL.md + MEMORY.md, sends the question to the LLM, and appends the exchange to MEMORY.md when `remember=True`.

### VERIFY Phase

- **`soul_status`**: Confirm that MEMORY.md grew after a write operation. Useful in test scaffolding and post-execution validation.
- **`soul_init`**: Verify that the expected files exist (reports `skipped` for pre-existing files).

### LEARN Phase

- **`soul_remember`**: Persist post-execution insights, decisions, or learnings directly to MEMORY.md for future agent sessions.

---

## MCP Tools

| Tool | Description | Phase(s) | Requires soul-agent |
|------|-------------|---------|---------------------|
| `soul_status` | File statistics for SOUL.md + MEMORY.md | OBSERVE, VERIFY | No |
| `soul_init` | Create default SOUL.md + MEMORY.md | PLAN, VERIFY | No |
| `soul_ask` | Query the agent; persist exchange | BUILD, EXECUTE | Yes |
| `soul_remember` | Append a note to MEMORY.md | BUILD, LEARN | Yes |
| `soul_reset` | Clear in-session history | EXECUTE | Yes |

---

## Agent Capabilities by Role

| PAI Agent Type | Primary Tools | Use Case |
|---|---|---|
| Engineer | `soul_init`, `soul_ask`, `soul_remember` | Build and interact with persistent agents |
| Architect | `soul_status` | Review memory footprint and file layout |
| QATester | `soul_status`, `soul_init` | Validate file creation and idempotency |
| Security | All | Audit memory content for PII or credentials |

---

## Integration Points

- **Upstream** (depends on): `model_context_protocol` (MCP decorator), `exceptions.base` (CodomyrmexError)
- **Downstream** (used by): `cli` (future `soul:*` commands), PAI orchestration workflows
- **Sibling** (related): `agentic_memory` (heavyweight vector-DB alternative), `llm` (provider infrastructure)

---

## Trust Gateway

Operations at **TRUSTED** level (require explicit trust):
- `soul_ask` — triggers LLM call + file write
- `soul_remember` — writes to filesystem
- `soul_reset` — agent state mutation

Operations at **OBSERVED** level (read-only / creation-only):
- `soul_status` — filesystem read only
- `soul_init` — creates files only; never overwrites

---

## Best Practices for PAI Agents

1. Always call `soul_status` before `soul_ask` to confirm SOUL.md exists; call `soul_init` if absent.
2. Use `soul_remember` instead of `soul_ask` when you need to inject facts without an LLM round-trip.
3. Keep SOUL.md focused on identity and personality — avoid embedding volatile state (use MEMORY.md).
4. Use dedicated `soul_path` / `memory_path` per agent role to avoid cross-contamination.
5. After an EXECUTE phase session, call `soul_reset` to clear session history before the next independent task.
