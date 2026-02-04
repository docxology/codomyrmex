# Codomyrmex Agents -- docs/modules/skills

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Agent-facing technical reference for the skills module. Provides the component inventory, interfaces, dependencies, and operating contracts needed for automated agents to interact with the skills system.

## Active Components

### Core (6 components)

| Component | File | Description |
|---|---|---|
| `SkillsManager` | `skills_manager.py` | Main interface for all skill operations: initialize, sync, list, search, get, add custom |
| `SkillLoader` | `skill_loader.py` | Loads YAML skill files from upstream and custom directories with merge logic and caching |
| `SkillSync` | `skill_sync.py` | Git-based synchronization: clone, pull, status check for the upstream repository |
| `SkillRegistry` | `skill_registry.py` | Builds index of all skills, extracts metadata, provides text/regex search |
| `SkillValidator` | `skill_validator.py` | Validates skill data dicts and YAML files against expected schema (patterns, anti_patterns, etc.) |
| `get_skills_manager()` | `__init__.py` | Factory function returning a configured SkillsManager instance |

### Discovery Framework (`discovery/`)

| Component | Description |
|---|---|
| `Skill` (ABC) | Abstract base class with `execute(**kwargs)` and `validate_params(**kwargs)` |
| `FunctionSkill` | Wraps a Python function as a Skill with auto-inferred metadata from signature/docstring |
| `SkillMetadata` | Dataclass for skill metadata with `to_dict()` and `to_json_schema()` for LLM tool calling |
| `ParameterSchema` | Dataclass for parameter definitions with type, required, default, enum support |
| `SkillCategory` | Enum: CODE, DATA, WEB, FILE, SYSTEM, COMMUNICATION, REASONING, UTILITY |
| `SkillRegistry` (discovery) | Runtime registry with register, unregister, search (by query/category/tags), execute |
| `SkillDiscoverer` | Discovers Skill instances and subclasses from Python modules |
| `@skill` decorator | Creates FunctionSkill from function with optional name, description, category, tags, registry |
| `register_skill()` / `get_skill()` | Global helpers for the default registry |

### Submodules (6 submodules)

| Submodule | Primary Class | Key Methods |
|---|---|---|
| `execution/` | `SkillExecutor` | `execute()`, `execute_with_timeout()`, `execute_chain()` |
| `composition/` | `SkillComposer` | `chain()`, `parallel()`, `conditional()` |
| `testing/` | `SkillTestRunner` | `test_skill()`, `validate_skill()`, `benchmark_skill()` |
| `marketplace/` | `SkillMarketplace` | `search_remote()`, `install()`, `list_sources()` |
| `versioning/` | `SkillVersionManager` | `get_version()`, `check_compatibility()`, `list_versions()` |
| `permissions/` | `SkillPermissionManager` | `check_permission()`, `grant()`, `revoke()` |

## Key Documentation Files

| File | Location | Content |
|---|---|---|
| API Specification | `src/codomyrmex/skills/API_SPECIFICATION.md` | Complete public API with signatures for all components |
| MCP Tools | `src/codomyrmex/skills/MCP_TOOL_SPECIFICATION.md` | 7 MCP tool definitions (skills_list, skills_get, skills_search, skills_sync, skills_add_custom, skills_get_categories, skills_get_upstream_status) |
| Functional Spec | `src/codomyrmex/skills/SPEC.md` | Architecture, requirements, directory structure, testing strategy |
| Source README | `src/codomyrmex/skills/README.md` | Features, quick start, component tables |

## Operating Contracts

- Custom skills in `skills/custom/` override upstream skills with the same category/name path
- YAML skill files must be dictionaries (not lists or scalars)
- The `@skill` decorator returns a `FunctionSkill` instance, not the original function
- `SkillRegistry` (YAML) and `SkillRegistry` (discovery) are separate classes in different modules
- PyYAML is an optional dependency; modules degrade gracefully if not installed
- All components use `try/except` for `codomyrmex.logging_monitoring` imports with `logging` fallback

## Dependencies

| Dependency | Type | Purpose |
|---|---|---|
| `git_operations` | Internal | Repository clone/pull operations |
| `logging_monitoring` | Internal | Structured logging |
| `model_context_protocol` | Internal | MCP tool interface |
| `PyYAML` | External (optional) | YAML file parsing |

## MCP Tools Summary

| Tool | Method | Description |
|---|---|---|
| `skills_list` | `list_skills(category?)` | List skills with optional category filter |
| `skills_get` | `get_skill(category, name)` | Get specific skill data |
| `skills_search` | `search_skills(query)` | Full-text search |
| `skills_sync` | `sync_upstream(force?)` | Sync with upstream repo |
| `skills_add_custom` | `add_custom_skill(category, name, data)` | Add custom skill |
| `skills_get_categories` | `get_categories()` | List all categories |
| `skills_get_upstream_status` | `get_upstream_status()` | Repo status info |

## Navigation Links

- **Source**: [src/codomyrmex/skills/](../../../src/codomyrmex/skills/)
- **Parent Directory**: [modules](../README.md)
- **Project Root**: ../../../README.md
