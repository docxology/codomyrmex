# Personal AI Infrastructure — Skills Module

**Version**: v1.2.2 | **Status**: Active | **Last Updated**: March 2026

## Overview

This module manages Codomyrmex's **internal** skill system — discovery, loading, synchronization, permissions, versioning, and marketplace operations for skills that live *within* the codomyrmex Python package.

### The Dual-Skill-System Relationship

There are **two separate skill systems** that interact through a well-defined bridge:

| System | Location | Manager | Purpose |
|--------|----------|---------|---------|
| **Codomyrmex Skills** | `src/codomyrmex/skills/` (this module) | `SkillsManager`, `SkillLoader` | Internal Python skills for the development platform |
| **PAI Skills** | `~/.claude/skills/` | PAI Algorithm (SKILL.md) | Personal AI skills invoked by the Algorithm |

The **bridge** between them is the Codomyrmex PAI Skill at `~/.claude/skills/Codomyrmex/SKILL.md`. This PAI-side skill exposes codomyrmex capabilities (115 auto-discovered MCP tools from 27 modules, 2 resources, 10 prompts) to the PAI Algorithm via the MCP protocol. It also provides the `/codomyrmexVerify` and `/codomyrmexTrust` workflows.

### How They Connect

```
PAI Algorithm (SKILL.md)
  └── invokes PAI Skills (~/.claude/skills/)
        └── Codomyrmex Skill (~/.claude/skills/Codomyrmex/SKILL.md)
              └── calls MCP server (scripts/model_context_protocol/run_mcp_server.py)
                    └── routes to codomyrmex modules (src/codomyrmex/*)
                          └── including this skills module (src/codomyrmex/skills/)
```

This module does **not** manage PAI skills. It manages the internal codomyrmex skill registry that PAI agents can *consume* through the MCP bridge.

## PAI Capabilities

```python
from codomyrmex.skills import SkillsManager, SkillLoader, SkillSync, permissions, versioning, marketplace
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `permissions` | Function/Constant | Skill permission management |
| `versioning` | Function/Constant | Skill version tracking |
| `marketplace` | Function/Constant | Skill marketplace operations |
| `SkillsManager` | Class | Central skill lifecycle manager |
| `SkillLoader` | Class | Dynamic skill loading and initialization |
| `SkillSync` | Class | Skill synchronization across environments |
| `SkillRegistry` | Class | Skill discovery and registration |
| `discovery` | Function/Constant | Skill discovery utilities |
| `execution` | Function/Constant | Skill execution runtime |
| `composition` | Function/Constant | Skill composition and chaining |
| `testing` | Function/Constant | Skill testing framework |

## PAI Algorithm Phase Mapping

| Phase | Skills Contribution |
|-------|------------------------------|
| **OBSERVE** | `SkillRegistry.discover()` — scan available skills matching task context |
| **PLAN** | `SkillsManager.resolve_dependencies()` — check skill prerequisites |
| **EXECUTE** | `SkillLoader.load()` + `execution.run()` — load and run matched skills |
| **VERIFY** | `testing.validate()` — verify skill execution results |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture. Depends on Foundation (logging, config) and Core (agents) layers.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Codomyrmex PAI Skill**: `~/.claude/skills/Codomyrmex/SKILL.md` — PAI-side bridge skill
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
