# Personal AI Infrastructure Context: docs/modules/

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Comprehensive documentation hub for all 88 Codomyrmex modules. This directory contains per-module RASP documentation sets (README.md, AGENTS.md, SPEC.md) and system-level architecture documents that describe module relationships, dependencies, and integration patterns.

## AI Agent Guidance

### Context for Agents

- **88 modules subdirectories** — each with README.md, AGENTS.md, SPEC.md
- **System-level views** — overview, relationships, dependency graph
- **Module categories** — Foundation, AI & Intelligence, Code & Analysis, Data & Visualization, DevOps & Infrastructure, Security & Cognitive, Interface & Communication, Framework & Utilities

### Key Documents

| Document | Purpose |
|----------|---------|
| `overview.md` | Module architecture, design principles, layer definitions |
| `relationships.md` | Module dependencies, compatibility matrix, data flow patterns |
| `dependency-graph.md` | Mermaid dependency visualization and layer rules |
| `ollama.md` | Local LLM setup and Ollama integration guide |
| `README.md` | Module index with category tables |
| `AGENTS.md` | Agent quality standards and operating contracts |
| `SPEC.md` | Functional specification and design principles |

### Navigation Strategy

1. **Finding a module**: Start with `README.md` module tables or browse subdirectories
2. **Understanding dependencies**: Use `relationships.md` for the compatibility matrix
3. **Architecture overview**: Use `overview.md` for design principles and layer definitions
4. **Visual orientation**: Use `dependency-graph.md` for the Mermaid diagram

### Subdirectories

Each module subdirectory follows the RASP documentation pattern:

- **README.md** — Human-readable overview, quick start, and features
- **AGENTS.md** — Agent signposting, guidelines, and coordination
- **SPEC.md** — Functional specification and design principles

## PAI System Documentation

This file describes the AI context for the `docs/modules/` directory. It is distinct from the **PAI system bridge** documentation:

| Document | Purpose |
|----------|---------|
| [`/PAI.md`](../../PAI.md) | **Authoritative bridge** — maps the actual PAI system (`~/.claude/skills/PAI/`) to codomyrmex modules |
| [`docs/pai/`](../pai/) | Detailed PAI-Codomyrmex reference — architecture, tools, API, workflows |
| `src/codomyrmex/<module>/PAI.md` | Per-module AI capabilities (RASP pattern) |
| This file (`docs/modules/PAI.md`) | AI agent context for the documentation directory |

If you're looking for how PAI (the system) integrates with codomyrmex, start at [`/PAI.md`](../../PAI.md).

## Cross-References

- [README.md](README.md) — Module index and category tables
- [AGENTS.md](AGENTS.md) — Agent quality standards (84/84 complete)
- [SPEC.md](SPEC.md) — Module system specification
- [overview.md](overview.md) — Architecture and design principles
- [relationships.md](relationships.md) — Dependency matrix and data flows
- [dependency-graph.md](dependency-graph.md) — Visual dependency graph
