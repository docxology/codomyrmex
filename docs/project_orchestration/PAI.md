# Personal AI Infrastructure Context: docs/project_orchestration/

## Purpose

Documentation for project orchestration, automation, and multi-project management.

## AI Agent Guidance

This directory covers cross-project coordination. AI agents should:

1. **Understand orchestration** — How projects are coordinated
2. **Follow workflows** — Use defined automation patterns
3. **Respect boundaries** — Honor project isolation

## Directory Structure

| File | Description |
|------|-------------|
| `orchestration_patterns.md` | Common orchestration patterns |
| `automation_guide.md` | Automation setup |
| `multi_project.md` | Managing multiple projects |

## PAI Integration

```python
from codomyrmex.project_orchestration import ProjectOrchestrator

# Orchestrate multiple projects
orchestrator = ProjectOrchestrator()
orchestrator.discover_projects("./projects/")

# Run across all projects
results = orchestrator.run_all("pytest")
```

## Cross-References

- [README.md](README.md) — Overview
- [AGENTS.md](AGENTS.md) — Agent rules
- [SPEC.md](SPEC.md) — Specification
- [../](../) — Parent docs directory
