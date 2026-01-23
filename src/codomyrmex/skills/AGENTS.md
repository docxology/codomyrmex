# Codomyrmex Agents — src/codomyrmex/skills

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Skills module provides integration with the vibeship-spawner-skills repository for skill management, upstream synchronization, and custom skill support. It enables loading, indexing, searching, and merging YAML-based skill definitions with support for patterns, anti-patterns, validations, and sharp edges. The module maintains separation between upstream skills (synced from the remote repository) and custom skills (local overrides), with custom skills taking precedence during merging.

## Active Components

### Core Components

- `skills_manager.py` - Main interface for skill operations
  - Key Class: `SkillsManager`
  - Key Functions: `initialize()`, `sync_upstream()`, `get_skill()`, `list_skills()`, `search_skills()`, `add_custom_skill()`
- `skill_loader.py` - Skill file loading and merging
  - Key Class: `SkillLoader`
  - Key Functions: `load_skill_file()`, `get_merged_skill()`, `load_all_skills()`, `merge_skills()`, `clear_cache()`
- `skill_sync.py` - Upstream repository synchronization
  - Key Class: `SkillSync`
  - Key Functions: `clone_upstream()`, `pull_upstream()`, `check_upstream_status()`, `get_upstream_version()`
- `skill_registry.py` - Skill indexing and search
  - Key Class: `SkillRegistry`
  - Key Functions: `build_index()`, `search_skills()`, `search_by_pattern()`, `get_categories()`, `refresh_index()`
- `skill_validator.py` - Skill YAML validation
  - Key Class: `SkillValidator`
  - Key Functions: `validate_skill()`, `validate_file()`, `validate_directory()`
- `__init__.py` - Module entry point with `get_skills_manager()` factory

### Skill Storage

- `skills/` - Directory containing skill YAML files
  - `upstream/` - Skills synced from vibeship-spawner-skills repository
  - `custom/` - Custom skill overrides (takes precedence)
  - `.cache/` - Cached merged skills (optional)

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `SkillsManager` | skills_manager | Main interface for all skill operations |
| `SkillLoader` | skill_loader | Loads and parses YAML skill files with merge logic |
| `SkillSync` | skill_sync | Handles syncing with upstream repository |
| `SkillRegistry` | skill_registry | Indexes and categorizes skills for search |
| `SkillValidator` | skill_validator | Validates skill YAML against schema |
| `get_skills_manager()` | `__init__` | Factory function for configured SkillsManager |
| `initialize()` | SkillsManager | Initialize skills system (dirs, clone, index) |
| `sync_upstream()` | SkillsManager | Sync with upstream repository |
| `get_skill()` | SkillsManager | Get a specific skill by category and name |
| `list_skills()` | SkillsManager | List available skills with optional category filter |
| `search_skills()` | SkillsManager | Search skills by query string |
| `add_custom_skill()` | SkillsManager | Add a custom skill override |
| `get_merged_skill()` | SkillLoader | Get skill with custom overrides applied |
| `clone_upstream()` | SkillSync | Clone the upstream repository |
| `pull_upstream()` | SkillSync | Pull latest changes from upstream |
| `build_index()` | SkillRegistry | Build search index from all skills |
| `search_by_pattern()` | SkillRegistry | Search skills by regex pattern |
| `validate_skill()` | SkillValidator | Validate skill data dictionary |

## Operating Contracts

1. **Logging**: All components use `logging_monitoring` for structured logging
2. **Upstream Source**: Default upstream is `vibeforge1111/vibeship-spawner-skills` on GitHub
3. **Merge Priority**: Custom skills override upstream skills completely
4. **Caching**: Merged skills are cached in memory and optionally on disk
5. **YAML Format**: Skills use YAML format with optional fields for patterns, anti_patterns, validations, sharp_edges
6. **Git Operations**: Uses `git_operations` module when available, falls back to subprocess

## Integration Points

- **logging_monitoring** - All components log via centralized logger
- **git_operations** - Git clone/pull operations for upstream sync
- **model_context_protocol** - MCP tool specifications for skill operations
- **agents** - Skills provide patterns for AI agent behavior

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agent integrations |
| fpf | [../fpf/AGENTS.md](../fpf/AGENTS.md) | First Principles Framework |
| git_operations | [../git_operations/AGENTS.md](../git_operations/AGENTS.md) | Git automation |
| plugin_system | [../plugin_system/AGENTS.md](../plugin_system/AGENTS.md) | Plugin architecture |
| cerebrum | [../cerebrum/AGENTS.md](../cerebrum/AGENTS.md) | Reasoning engine |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| skills/ | Skill YAML file storage |
| skills/upstream/ | Skills synced from upstream repository |
| skills/custom/ | Custom skill overrides |
| skills/.cache/ | Cached merged skills |

### Related Documentation

- [README.md](README.md) - User documentation
- [SPEC.md](SPEC.md) - Functional specification
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specs
