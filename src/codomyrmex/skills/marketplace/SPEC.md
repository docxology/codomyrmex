# Technical Specification - Marketplace

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.skills.marketplace`  
**Last Updated**: 2026-01-29

## 1. Purpose

Skill discovery from external sources and repositories

## 2. Architecture

### 2.1 Components

```
marketplace/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `skills`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.skills.marketplace
from codomyrmex.skills.marketplace import (
    SkillMarketplace,  # Discovers and installs skills from remote sources
)

# Key class signature:
class SkillMarketplace:
    def __init__(self, sources: list[dict[str, str]] | None = None) -> None: ...
    def search_remote(self, query: str) -> list[dict[str, Any]]: ...
    def install(self, skill_id: str, source: str | None = None) -> dict[str, Any]: ...
    def list_sources(self) -> list[dict[str, str]]: ...
    def add_source(self, name: str, url: str, source_type: str = "git") -> None: ...
    def remove_source(self, name: str) -> bool: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Default upstream source**: The marketplace ships with a default source pointing to the `vibeship-spawner-skills` GitHub repository, providing an out-of-box discovery target.
2. **Explicit non-implementation for network operations**: `search_remote` and `install` return structured status dicts rather than raising `NotImplementedError`, allowing callers to detect the "not yet available" state without exception handling.

### 4.2 Limitations

- `search_remote` and `install` are not yet functional; they return status dicts indicating network access is required
- No local caching of remote skill metadata

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/skills/marketplace/
```

## 6. Future Considerations

- Implement Git-based remote search and clone-to-install workflow
- Add local metadata cache for offline browsing of remote skill catalogs
- Support versioned skill installation and dependency resolution
