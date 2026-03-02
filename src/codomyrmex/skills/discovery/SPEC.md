# Skill Discovery -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides skill definition, registration, discovery, and execution through a registry pattern. Skills are defined as classes extending `Skill` ABC or as functions wrapped by `FunctionSkill` via the `@skill` decorator. The `SkillRegistry` stores and indexes skills by ID, category, and tags.

## Architecture

Registry pattern with ABC-based skill contracts. `FunctionSkill` infers metadata from function signatures and type hints via `inspect`. `SkillDiscoverer` scans modules for `Skill` subclasses and `@skill`-decorated functions. A global `DEFAULT_REGISTRY` singleton provides module-level convenience functions.

## Key Classes

### `Skill` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute` | `**kwargs` | `Any` | Abstract: execute the skill |
| `validate_params` | `**kwargs` | `list[str]` | Validate kwargs against parameter schema; return list of error messages |

### `FunctionSkill` (extends Skill)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `func: Callable, metadata: SkillMetadata\|None` | `None` | Wrap function; auto-infer metadata if not provided |
| `execute` | `**kwargs` | `Any` | Call the wrapped function |

### `SkillRegistry`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `skill: Skill` | `None` | Register by ID; index by category and tags |
| `unregister` | `skill_id: str` | `None` | Remove skill and all index entries |
| `get` | `skill_id: str` | `Skill\|None` | Lookup by ID |
| `get_by_name` | `name: str` | `Skill\|None` | Lookup by metadata name |
| `search` | `query, category, tags, enabled_only` | `list[Skill]` | Filter by text, category, tags, enabled state |
| `list_all` | | `list[SkillMetadata]` | All registered skill metadata |
| `execute` | `skill_id, **kwargs` | `Any` | Validate params then execute |

### `SkillDiscoverer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `discover_from_module` | `module` | `list[Skill]` | Find Skill subclasses and instances in a module |
| `discover_from_decorated` | `module` | `list[Skill]` | Find `FunctionSkill` instances from `@skill` decorator |

### Data Models

| Class | Key Fields | Description |
|-------|-----------|-------------|
| `SkillMetadata` | `id, name, description, version, category, tags, parameters, returns, examples` | Skill metadata with `to_dict()` and `to_json_schema()` |
| `ParameterSchema` | `name, param_type, description, required, default, enum_values` | Single parameter definition |
| `SkillCategory` | Enum: CODE, DATA, WEB, FILE, SYSTEM, COMMUNICATION, REASONING, UTILITY | Skill classification |

## Dependencies

- **Internal**: None (self-contained)
- **External**: `hashlib`, `inspect`, `json` (stdlib)

## Constraints

- Skill IDs are MD5 hashes of `module.function_name` (first 12 characters).
- `FunctionSkill._infer_metadata` maps Python type hints to JSON schema types: `int->integer`, `float->number`, `bool->boolean`, `list->array`, `dict->object`, default `string`.
- `SkillDiscoverer.discover_from_module` catches `TypeError` when instantiating Skill subclasses (e.g., those requiring constructor args).
- `SkillRegistry.execute` validates params before execution and raises `ValueError` on missing required params or unknown skill ID.
- Zero-mock: real function calls and module inspection only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `validate_params` returns error strings (not exceptions) for missing required parameters.
- `SkillRegistry.execute` raises `ValueError` for unknown skill IDs or invalid parameters.
- All errors logged before propagation.
