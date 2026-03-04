# Skills Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Skill discovery, listing, and invocation management. Provides 7 skill management tools for PAI skill ecosystem integration.

## Configuration Options

The skills module operates with sensible defaults and does not require environment variable configuration. Skill directories are auto-discovered from ~/.claude/skills/. Skill index is cached and regenerated on demand.

## MCP Tools

This module exposes 7 MCP tool(s):

- `skills_list`
- `skills_get`
- `skills_invoke`
- `skills_search`
- `skills_register`
- `skills_unregister`
- `skills_validate`

## PAI Integration

PAI agents invoke skills tools through the MCP bridge. Skill directories are auto-discovered from ~/.claude/skills/. Skill index is cached and regenerated on demand.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep skills

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/skills/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
