# Personal AI Infrastructure — Skills Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

This module manages Codomyrmex's **internal** skill system — discovery, loading, synchronization, permissions, versioning, and marketplace operations for skills that live *within* the codomyrmex Python package.

### The Dual-Skill-System Relationship

There are **two separate skill systems** that interact through a well-defined bridge:

| System | Location | Manager | Purpose |
|--------|----------|---------|---------|
| **Codomyrmex Skills** | `src/codomyrmex/skills/` (this module) | `SkillsManager`, `SkillLoader` | Internal Python skills for the development platform |
| **PAI Skills** | `~/.claude/skills/` | PAI Algorithm (SKILL.md) | Personal AI skills invoked by the Algorithm |

The **bridge** between them is the Codomyrmex PAI Skill at `~/.claude/skills/Codomyrmex/SKILL.md`. This PAI-side skill exposes codomyrmex capabilities (~148 auto-discovered MCP tools from 33 modules plus ~19 static tools = ~167 total, 3 resources, 10 prompts) to the PAI Algorithm via the MCP protocol. It also provides the `/codomyrmexVerify` and `/codomyrmexTrust` workflows.

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

## MCP Tools

Seven MCP tools are auto-discovered via `@mcp_tool` and available through the PAI
MCP bridge for skills management:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.skills_list` | List available skills, optionally filtered by category | Safe | skills |
| `codomyrmex.skills_get` | Get a specific skill by category and name | Safe | skills |
| `codomyrmex.skills_search` | Search skills by query string | Safe | skills |
| `codomyrmex.skills_sync` | Sync with upstream vibeship-spawner-skills repository | Safe | skills |
| `codomyrmex.skills_add_custom` | Add a custom skill that overrides upstream | Safe | skills |
| `codomyrmex.skills_get_categories` | Get all available skill categories | Safe | skills |
| `codomyrmex.skills_get_upstream_status` | Get status of upstream repository (branch, commits, changes) | Safe | skills |

### MCP Tool Usage Examples

```python
# List all skills
result = mcp_call("codomyrmex.skills_list")
# Returns: [{"category": "...", "name": "...", ...}, ...]

# Search by keyword
result = mcp_call("codomyrmex.skills_search", {"query": "authentication"})

# Get categories
result = mcp_call("codomyrmex.skills_get_categories")
# Returns: ["security", "coding", "ai", ...]
```

## PAI Algorithm Phase Mapping

| Phase | Skills Contribution | MCP Tools |
|-------|---------------------|-----------|
| **OBSERVE** | Discover available skills matching task context | `skills_list`, `skills_search` |
| **THINK** | Check skill metadata to inform capability selection decisions | `skills_get`, `skills_get_categories` |
| **PLAN** | Verify skill prerequisites and upstream sync status | `skills_get_upstream_status`, `skills_sync` |
| **EXECUTE** | Invoke skill by name; confirm custom overrides are in place | `skills_get`, `skills_add_custom` |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture. Depends on Foundation (logging, config) and Core (agents) layers.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Codomyrmex PAI Skill**: `~/.claude/skills/Codomyrmex/SKILL.md` — PAI-side bridge skill
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
