# docs/pai — Functional Specification

**Version**: v1.0.3 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Expanded reference documentation for the PAI-Codomyrmex integration. Supplements the root `PAI.md` bridge document with detailed architecture, API, and tool references. The PAI Dashboard (port 8889) is a Codomyrmex-integrated fork of [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure).

![PAI Analytics — Primary dashboard interface showing mission, project, and task metrics](screenshots/pai_analytics.png)

## Scope

| Document | Covers |
|----------|--------|
| `architecture.md` | Component diagram, data flow, trust model, cross-language communication |
| `tools-reference.md` | All 20 static tools with parameters, trust levels; dynamic discovery mechanism |
| `api-reference.md` | PAIBridge (24 methods), TrustRegistry, module functions, dataclasses, constants |
| `workflows.md` | `/codomyrmexVerify`, `/codomyrmexTrust`, Algorithm phase mapping |
| `screenshots/` | PAI Dashboard interface screenshots (8 tabs) |

## Design Principles

1. **Hierarchy**: Root PAI.md (bridge overview) → docs/pai/ (detailed reference) → src/ (implementation docs)
2. **No duplication**: Each document has a unique scope — no verbatim copying from root PAI.md
3. **Synchronized**: All counts (20 tools, 10 prompts, 2 resources, 4 destructive) match implementation
4. **Visual**: Interface screenshots embedded in context alongside the features they document

## Dashboard Tabs Covered

| Tab | Screenshot | Primary Doc |
|-----|-----------|-------------|
| Analytics | `screenshots/pai_analytics.png` | `api-reference.md` — PAI status/awareness |
| Board | `screenshots/pai_board.png` | `workflows.md` — Mission lifecycle tracking |
| Calendar | `screenshots/pai_calendar.png` | `workflows.md` — Scheduling integration |
| Email | `screenshots/pai_email.png` | `tools-reference.md` — MCP email tools |
| Network | `screenshots/pai_network.png` | `architecture.md` — Graph visualization |
| Git | `screenshots/pai_git.png` | `tools-reference.md` — Git operations |
| Dispatch | `screenshots/pai_dispatch.png` | `workflows.md` — Algorithm execution |
| Integration | `screenshots/pai_integration.png` | `architecture.md` — GitHub bridge |

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Documentation**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **Parent**: [docs/](../)
