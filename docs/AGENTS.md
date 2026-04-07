# Codomyrmex Agents — docs/

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination document for the `docs/` directory. Guides AI agents navigating the documentation surface of the Codomyrmex ecosystem.

## Key Files

| Path | Role |
|:---|:---|
| [reference/inventory.md](reference/inventory.md) | Canonical counts (modules, tests, MCP decorators, workflows) |
| [development/documentation.md](development/documentation.md) | Authoring policy, Mermaid, bootstrap vs hand-edit |
| [modules/AGENTS.md](modules/AGENTS.md) | Module doc ownership (`enrich_module_docs` vs `src/`) |
| [agents/AGENTS.md](agents/AGENTS.md) | Agent documentation tree root |
| [index.md](index.md) | Published docs entry |

## Dependencies

- **Source of truth**: `src/codomyrmex/` and root `SPEC.md` / `AGENTS.md`; this tree explains and links, it does not replace code.
- **Tooling**: `uv` for scripts (`scripts/doc_inventory.py`, `scripts/documentation/validate_agents_structure.py`); optional site build per `pyproject.toml` / Docusaurus under `src/codomyrmex/documentation/` when publishing.

## Development Guidelines

- Follow [development/documentation.md](development/documentation.md) for curated markers, bootstrap scope, and validator expectations after substantive edits.
- Prefer targeted hand edits over full-repo bootstrap; keep **Operating Contracts** below for navigation and mirror rules.
- Refresh volatile numbers via `uv run python scripts/doc_inventory.py --pytest` before updating [reference/inventory.md](reference/inventory.md) or root `README.md`.

## Documentation Architecture

The `docs/` directory is organized into **19 thematic sections** containing **200+ markdown files**:

### Core references (top level)

| File | Purpose |
|:---|:---|
| `ARCHITECTURE.md` | System architecture, layers, module graph |
| `DEPENDENCIES.md` | Dependency compatibility guide |
| `PAI.md` | Personal AI Infrastructure hub |
| `PAI_DASHBOARD.md` | Dashboard functionality matrix |
| `SPEC.md` | Documentation-area functional specification ([root `SPEC.md`](../SPEC.md) is authoritative for the whole repo) |
| `index.md` | Documentation site entry point |

Volatile counts (modules, MCP tools, tests) live in [reference/inventory.md](reference/inventory.md); refresh with `uv run python scripts/doc_inventory.py`.

### Thematic Sections

| Section | Focus | Key Content |
|:---|:---|:---|
| `agents/` | AI agent integrations | 39 packages mirror `src/codomyrmex/agents/` (+ [`agents/rules/`](agents/rules/) docs-only); Hermes: [agents/hermes/AGENTS.md](agents/hermes/AGENTS.md), [skills.md](agents/hermes/skills.md) |
| `agi/` | AGI theory | Essays on emergence, category theory, agency |
| `bio/` | Biological simulation | BioSimulator, genetic algorithms |
| `cognitive/` | Cognitive systems | Cerebrum, Bayesian networks, active inference |
| `compliance/` | Regulatory | Audit frameworks, data governance |
| `deployment/` | DevOps | CI/CD, containers, cloud deployment |
| `development/` | Developer guides | Environment setup, testing, coding standards |
| `examples/` | Tutorials | Executable demos and integration examples |
| `getting-started/` | Onboarding | Quickstart, installation, learning path |
| `integration/` | Cross-module | Integration patterns, MCP bridges |
| `modules/` | Module docs | **128** top-level packages; ownership hub [modules/AGENTS.md](modules/AGENTS.md) (see [reference/inventory.md](reference/inventory.md)) |
| `pai/` | PAI system | Dashboard, skills, memory, dispatch |
| `plans/` | Roadmap | Release plans, version targets |
| `project/` | Standards | Contributing, architecture, coding style |
| `project_orchestration/` | Workflows | Multi-agent coordination, orchestration |
| `reference/` | API docs | CLI tools, configuration reference |
| `security/` | Security | Threat models, audit, secret management |
| `skills/` | Agent skills | Skill creation, registry, testing |

## Operating Contracts

1. **Docs mirror src/**: The `docs/agents/` structure mirrors `src/codomyrmex/agents/` with a documentation subfolder for each agent framework
2. **Navigation consistency**: Every document must have Navigation section with links to parent, siblings, and root
3. **Version stamping**: All top-level docs must have version/status/date header
4. **Real content only**: No placeholder or auto-generated boilerplate — every file must contain substantive documentation

## Key Patterns

- **Signposting**: Parent/child/sibling links in every document
- **Cross-references**: Source docs link to doc docs and vice versa via relative paths
- **Hierarchical AGENTS.md**: Root → `docs/AGENTS.md` → `docs/agents/AGENTS.md` → per-agent `AGENTS.md`
- **Mermaid**: [development/documentation.md](development/documentation.md) — theme-neutral diagrams, subgraph conventions, normalizer scripts under `scripts/`

## Navigation

- **Parent**: [AGENTS.md](../AGENTS.md) — Root agent coordination
- **Project Root**: [README.md](../README.md) — Project overview
- **Source**: [src/codomyrmex/](../src/codomyrmex/) — Source code
