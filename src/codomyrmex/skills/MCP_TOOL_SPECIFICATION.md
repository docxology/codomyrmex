# skills - MCP Tool Specification

## Overview

This document specifies the Model Context Protocol (MCP) tools provided by the `skills` module for managing and accessing skills from the vibeship-spawner-skills repository.

## Available Tools

### `skills_list`

**Description**: List available skills, optionally filtered by category.

**Parameters**:
```json
{
  "category": {
    "type": "string",
    "description": "Optional category filter",
    "required": false
  }
}
```

**Returns**: List of skill information dictionaries with category, name, and metadata.

**Example**:
```json
{
  "tool": "skills_list",
  "parameters": {
    "category": "backend"
  }
}
```

### `skills_get`

**Description**: Get a specific skill by category and name.

**Parameters**:
```json
{
  "category": {
    "type": "string",
    "description": "Skill category",
    "required": true
  },
  "name": {
    "type": "string",
    "description": "Skill name",
    "required": true
  }
}
```

**Returns**: Skill data dictionary or null if not found.

**Example**:
```json
{
  "tool": "skills_get",
  "parameters": {
    "category": "backend",
    "name": "api-design"
  }
}
```

### `skills_search`

**Description**: Search skills by query string.

**Parameters**:
```json
{
  "query": {
    "type": "string",
    "description": "Search query",
    "required": true
  }
}
```

**Returns**: List of matching skills with full data and metadata.

**Example**:
```json
{
  "tool": "skills_search",
  "parameters": {
    "query": "authentication"
  }
}
```

### `skills_sync`

**Description**: Sync with upstream vibeship-spawner-skills repository.

**Parameters**:
```json
{
  "force": {
    "type": "boolean",
    "description": "Force re-clone even if directory exists",
    "required": false,
    "default": false
  }
}
```

**Returns**: Success status and sync information.

**Example**:
```json
{
  "tool": "skills_sync",
  "parameters": {
    "force": false
  }
}
```

### `skills_add_custom`

**Description**: Add a custom skill that overrides upstream.

**Parameters**:
```json
{
  "category": {
    "type": "string",
    "description": "Skill category",
    "required": true
  },
  "name": {
    "type": "string",
    "description": "Skill name",
    "required": true
  },
  "skill_data": {
    "type": "object",
    "description": "Skill data dictionary",
    "required": true
  }
}
```

**Returns**: Success status.

**Example**:
```json
{
  "tool": "skills_add_custom",
  "parameters": {
    "category": "my-category",
    "name": "my-skill",
    "skill_data": {
      "description": "My custom skill",
      "patterns": []
    }
  }
}
```

### `skills_get_categories`

**Description**: Get all available skill categories.

**Parameters**: None

**Returns**: List of category names.

**Example**:
```json
{
  "tool": "skills_get_categories",
  "parameters": {}
}
```

### `skills_get_upstream_status`

**Description**: Get status of upstream repository.

**Parameters**: None

**Returns**: Status dictionary with exists, is_git_repo, branch, has_changes, last_commit.

**Example**:
```json
{
  "tool": "skills_get_upstream_status",
  "parameters": {}
}
```

## Tool Registration

Tools are available through the SkillsManager instance:

```python
from codomyrmex.skills import get_skills_manager

manager = get_skills_manager()
manager.initialize()

# Tools can be called via MCP protocol
# The SkillsManager methods correspond to the MCP tools
```

## Related Documentation

- [Module README](./README.md)
- [API Specification](./AGENTS.md)
- [Functional Specification](./SPEC.md)

