# Skills

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Skills Module for Codomyrmex

## Architecture Overview

```
skills/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`SkillsManager`**
- **`SkillLoader`**
- **`SkillSync`**
- **`SkillRegistry`**
- **`arscontexta`**
- **`discovery`**
- **`execution`**
- **`composition`**
- **`testing`**
- **`mcp_tools`**
- **`run_skill`**
- **`run_skill_by_name`**
- **`list_runnable_skills`**
- **`cli_commands`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `skills_list` | Safe |
| `skills_get` | Safe |
| `skills_search` | Safe |
| `skills_sync` | Safe |
| `skills_add_custom` | Safe |
| `skills_get_categories` | Safe |
| `skills_get_upstream_status` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/skills/](../../../../src/codomyrmex/skills/)
- **Parent**: [All Modules](../README.md)
