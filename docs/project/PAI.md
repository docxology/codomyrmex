# Personal AI Infrastructure Context: docs/project/

## Purpose

Project-level documentation including audit results, health reports, and project status tracking.

## AI Agent Guidance

This directory contains project health information and audit results. AI agents should:

1. **Reference history** — Check audit results for known issues
2. **Track progress** — Use status files for project health
3. **Understand context** — Read background for project decisions

## Directory Structure

| File | Description |
|------|-------------|
| `audit_results.md` | Security and quality audits |
| `project_status.md` | Current project health |
| `decision_log.md` | Architectural decisions |

## PAI Integration

```python
from codomyrmex.system_discovery import get_project_status

# Query project health
status = get_project_status()
print(f"Health: {status.health_score}%")
print(f"Open Issues: {status.open_issues}")
```

## Cross-References

- [README.md](README.md) — Overview
- [AGENTS.md](AGENTS.md) — Agent rules
- [SPEC.md](SPEC.md) — Specification
- [../](../) — Parent docs directory
