# Codomyrmex Agents — docs/

**Version**: v1.2.2 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination document for the `docs/` directory. Guides AI agents navigating the documentation surface of the Codomyrmex ecosystem.

## Documentation Architecture

The `docs/` directory is organized into **19 thematic sections** containing **200+ markdown files**:

### Core References (Top Level)

| File | Purpose | Lines |
|:---|:---|---:|
| `ARCHITECTURE.md` | System architecture, layers, module graph | 448 |
| `DEPENDENCIES.md` | Dependency compatibility guide | 116 |
| `PAI.md` | Personal AI Infrastructure hub | 127 |
| `PAI_DASHBOARD.md` | Dashboard functionality matrix | 38 |
| `SPEC.md` | Functional specification | 178 |
| `index.md` | Documentation site entry point | 50 |

### Thematic Sections

| Section | Focus | Key Content |
|:---|:---|:---|
| `agents/` | AI agent integrations | 38 agent subfolders, Hermes deep-dive (19 docs) |
| `agi/` | AGI theory | Essays on emergence, category theory, agency |
| `bio/` | Biological simulation | BioSimulator, genetic algorithms |
| `cognitive/` | Cognitive systems | Cerebrum, Bayesian networks, active inference |
| `compliance/` | Regulatory | Audit frameworks, data governance |
| `deployment/` | DevOps | CI/CD, containers, cloud deployment |
| `development/` | Developer guides | Environment setup, testing, coding standards |
| `examples/` | Tutorials | Executable demos and integration examples |
| `getting-started/` | Onboarding | Quickstart, installation, learning path |
| `integration/` | Cross-module | Integration patterns, MCP bridges |
| `modules/` | Module docs | 126 module subdirectories |
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

## Navigation

- **Parent**: [AGENTS.md](../AGENTS.md) — Root agent coordination
- **Project Root**: [README.md](../README.md) — Project overview
- **Source**: [src/codomyrmex/](../src/codomyrmex/) — Source code
