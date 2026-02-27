# Technical Specification - Versioning

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.skills.versioning`  
**Last Updated**: 2026-01-29

## 1. Purpose

Skill version management and compatibility tracking

## 2. Architecture

### 2.1 Components

```
versioning/
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
from codomyrmex.skills.versioning import SkillVersionManager
from codomyrmex.skills.versioning import parse_version
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Semantic versioning only**: Version management follows semver (MAJOR.MINOR.PATCH); non-semver schemes are not supported.

### 4.2 Limitations

- Version history is in-memory per session; no persistent version ledger across sessions.
- No automatic rollback support; callers must manage downgrade logic.

## 5. Testing

```bash
# Run tests for this module
pytest tests/skills_versioning/
```

## 6. Future Considerations

- Semantic version conflict detection: when multiple skills declare incompatible version constraints on shared dependencies, surface conflicts with actionable resolution suggestions rather than raising a bare ImportError.
- Persistent version ledger: write resolved version records to disk so the state survives across sessions, enabling audit trails and reproducible skill environments.
- Automatic rollback: when a skill upgrade fails its post-install checks, automatically revert to the previously resolved version and log the rollback event.
