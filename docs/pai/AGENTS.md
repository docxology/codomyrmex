# Codomyrmex Agents — docs/pai

**Version**: v1.0.3 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Documentation module for the PAI-Codomyrmex integration. Provides architecture references, tool inventories, API documentation, and workflow guides. The PAI Dashboard (port 8889) is a Codomyrmex-integrated fork of [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure).

## Active Components

| File | Description | Screenshot |
|------|-------------|------------|
| `README.md` | Index page with full screenshot gallery | All 8 tabs |
| `architecture.md` | MCP bridge architecture and trust model | Analytics, Network, Integration |
| `tools-reference.md` | Complete tool inventory (22 static + dynamic) | Git, Email |
| `api-reference.md` | Python API reference (PAIBridge, TrustRegistry) | Analytics |
| `workflows.md` | Workflow documentation and Algorithm mapping | Dispatch, Board, Calendar |
| `screenshots/` | PAI Dashboard interface screenshots (8 tabs) | — |

## Visual Reference

The PAI Dispatch tab demonstrates Algorithm phase execution with per-mission action buttons:

![PAI Dispatch — Mission action center with Summarize, Scope & Plan, Review, Enact Next Step](screenshots/pai_dispatch.png)

The Network tab shows the agent's awareness of mission→project→task relationships:

![PAI Network — Force-directed graph visualization with missions (blue), projects (cyan), tasks (gray)](screenshots/pai_network.png)

## Operating Contracts

1. **Reference only**: This folder contains documentation, not executable code
2. **No duplication**: Expands on the root PAI.md bridge doc, does not duplicate it
3. **Synchronized**: Counts and versions match the implementation in `src/codomyrmex/agents/pai/`
4. **Visual-first**: Every doc embeds relevant interface screenshots for context

## Navigation Links

- **README**: [README.md](README.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)
- **Parent**: [docs/](../)
- **Root PAI Bridge**: [../../PAI.md](../../PAI.md)
