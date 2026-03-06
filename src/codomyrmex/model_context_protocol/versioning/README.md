# MCP Versioning

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides semantic versioning, deprecation lifecycle management, and compatibility tracking for MCP tools. Tool authors annotate functions with `@versioned` and `@deprecated` decorators, while the `VersionRegistry` tracks all tool versions, generates migration guides, and produces markdown summaries. A `CompatibilityMatrix` enables explicit cross-version compatibility declarations beyond the default same-major-version rule.

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `APIVersion` | Dataclass | Frozen, ordered semantic version (major.minor.patch) with `parse()` and `is_compatible()` |
| `DeprecationInfo` | Dataclass | Deprecation metadata: since, removal, replacement, message |
| `VersionedTool` | Dataclass | Combines tool name, current version, deprecation flag, and introduction version |
| `versioned` | Decorator | Attaches `_api_version` and `_api_introduced` metadata to functions |
| `deprecated` | Decorator | Marks functions deprecated; emits `DeprecationWarning` on each call |
| `CompatibilityMatrix` | Class | Tracks version compatibility pairs; same-major versions compatible by default |
| `VersionRegistry` | Class | Registry of all versioned tools with deprecation, history, and migration support |
| `MigrationStep` | Dataclass | Single migration action: tool name, from/to version, action, details |

## Quick Start

```python
from codomyrmex.model_context_protocol.versioning import (
    APIVersion,
    VersionRegistry,
    versioned,
    deprecated,
)

# Parse and compare versions
v1 = APIVersion.parse("v1.2.3")
v2 = APIVersion.parse("1.3.0")
assert v1.is_compatible(v2)  # same major, v2 >= v1

# Annotate a tool with version metadata
@versioned(version="1.2.0", introduced="1.0.0")
def search_code(query: str) -> list:
    return []

# Mark a tool as deprecated
@deprecated(since="1.2.0", removal="2.0.0", replacement="search_code_v2")
def old_search(query: str) -> list:
    return []

# Track tools in the registry
registry = VersionRegistry()
registry.register("search_code", version="1.2.0")
registry.deprecate("search_code", since="1.2.0", removal="2.0.0",
                    replacement="search_code_v2")
print(registry.to_markdown())
```

## Architecture

```
versioning/
├── __init__.py            # Re-exports from both submodules
├── versioning.py          # Core primitives: APIVersion, decorators, CompatibilityMatrix
├── version_registry.py    # VersionRegistry and MigrationStep for tool lifecycle tracking
├── AGENTS.md              # Agent coordination docs
├── SPEC.md                # Technical specification
└── README.md              # This file
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/model_context_protocol/ -v
```

## Navigation
- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
