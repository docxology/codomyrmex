# soul — Agent Capabilities

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Agent Access Matrix

### Engineer Agent

**Access**: Full
**Trust Level**: TRUSTED

| Capability | Tool / Method |
|---|---|
| Create agent memory files | `soul_init` |
| Query persistent agent | `soul_ask` |
| Inject facts into memory | `soul_remember` |
| Reset session context | `soul_reset` |
| File statistics | `soul_status` |

**Use Cases**: Building persistent AI assistants, storing project context across sessions, constructing git-trackable agent identities.

---

### Architect Agent

**Access**: Read-only
**Trust Level**: OBSERVED

| Capability | Tool / Method |
|---|---|
| Inspect memory files | `soul_status` |
| Review agent identity | Read SOUL.md directly |

**Use Cases**: Reviewing agent identity design, auditing memory growth, evaluating soul vs agentic_memory trade-offs.

---

### QATester Agent

**Access**: File-level validation
**Trust Level**: OBSERVED

| Capability | Tool / Method |
|---|---|
| Verify file creation | `soul_init`, `soul_status` |
| Validate memory structure | `soul_status` |

**Use Cases**: Verifying that soul_init creates valid files, confirming memory persists across calls.

---

### Security Agent

**Access**: Full
**Trust Level**: TRUSTED

| Capability | Tool / Method |
|---|---|
| Audit stored memory content | `soul_status` + direct file read |
| Check for PII in MEMORY.md | Read MEMORY.md |

**Use Cases**: Verifying no credentials are persisted in MEMORY.md, auditing agent identity in SOUL.md.

---

## Trust Level Definitions

| Level | Operations Permitted |
|---|---|
| UNTRUSTED | None |
| OBSERVED | `soul_status`, `soul_init` (file creation only), read-only |
| TRUSTED | Full access — `soul_ask`, `soul_remember`, `soul_reset` |

---

## MCP Tools Available

| Tool | Description | Requires soul-agent | Trust |
|------|-------------|---------------------|-------|
| `soul_init` | Create SOUL.md + MEMORY.md | No | OBSERVED |
| `soul_status` | File size statistics | No | OBSERVED |
| `soul_ask` | Query the agent | Yes | TRUSTED |
| `soul_remember` | Append note to MEMORY.md | Yes | TRUSTED |
| `soul_reset` | Clear session history | Yes | TRUSTED |

---

## PAI Algorithm Phase Mapping

| Phase | Tools | Agent |
|-------|-------|-------|
| OBSERVE | `soul_status` | All |
| PLAN | `soul_init` | Engineer, Architect |
| BUILD | `soul_ask`, `soul_remember` | Engineer |
| EXECUTE | `soul_ask` | Engineer |
| VERIFY | `soul_status`, `soul_init` | QATester |
| LEARN | `soul_remember` | Engineer |

---

## Security Constraints

1. API keys are never written to SOUL.md or MEMORY.md — sourced from environment only.
2. MEMORY.md is auto-truncated to 6 000 chars by soul.py — prevents unbounded growth.
3. All file I/O uses explicit `encoding="utf-8"` to prevent platform encoding issues.
4. `soul_init` never overwrites existing files — safe for idempotent use.
