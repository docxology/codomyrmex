# Technical Specification - Permissions

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.skills.permissions`  
**Last Updated**: 2026-01-29

## 1. Purpose

Skill capability permissions and access control

## 2. Architecture

### 2.1 Components

```
permissions/
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
# Primary exports from codomyrmex.skills.permissions
from codomyrmex.skills.permissions import (
    SkillPermissionManager,  # Manages per-skill action permissions
)

# Key class signature:
class SkillPermissionManager:
    def __init__(self) -> None: ...
    def check_permission(self, skill_id: str, action: str) -> bool: ...
    def grant(self, skill_id: str, permission: str) -> None: ...
    def revoke(self, skill_id: str, permission: str) -> bool: ...
    def list_permissions(self, skill_id: str) -> list[str]: ...
    def grant_all(self, skill_id: str, permissions: list[str]) -> None: ...
    def revoke_all(self, skill_id: str) -> None: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **In-memory permission store**: Permissions are held in a `dict[str, set[str]]` keyed by `skill_id`. This keeps the implementation dependency-free and fast for the current single-process use case.
2. **Structured logging via `logging_monitoring`**: All grant/revoke operations are logged through the centralized logger with a graceful fallback to stdlib `logging` if the dependency is unavailable.

### 4.2 Limitations

- No persistence: permissions are lost on process restart
- No role-based or hierarchical permission model; flat action strings only

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/skills/permissions/
```

## 6. Future Considerations

- Add persistent storage backend (file or database)
- Support wildcard or role-based permission grants
- Add permission inheritance between skills
