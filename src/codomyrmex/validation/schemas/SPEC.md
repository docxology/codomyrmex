# Technical Specification - Schemas

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.validation.schemas`  
**Last Updated**: 2026-01-29

## 1. Purpose

Schema registry, versioning, and evolution management

## 2. Architecture

### 2.1 Components

```
schemas/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `validation`

## 3. Interfaces

### 3.1 Public API

```python
from codomyrmex.validation.schemas import SchemaType
from codomyrmex.validation.schemas import ValidationError
from codomyrmex.validation.schemas import ValidationResult
from codomyrmex.validation.schemas import FieldSchema
from codomyrmex.validation.schemas import Constraint
from codomyrmex.validation.schemas import TypeConstraint
from codomyrmex.validation.schemas import MinLengthConstraint
from codomyrmex.validation.schemas import MaxLengthConstraint
from codomyrmex.validation.schemas import MinValueConstraint
from codomyrmex.validation.schemas import MaxValueConstraint
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Constraint-first design**: Validation constraints (TypeConstraint, MinLengthConstraint, etc.) are composable objects, not hard-coded logic — enabling dynamic schema construction at runtime.

### 4.2 Limitations

- No JSON Schema draft 7/2020 support — uses an internal constraint model, not JSON Schema standard.
- Schema evolution (migrations) is not automatically applied; callers must manage version transitions.

## 5. Testing

```bash
# Run tests for this module
pytest tests/validation_schemas/
```

## 6. Future Considerations

- JSON Schema draft 7/2020-12 support: add an adapter that maps the existing constraint model to standard JSON Schema, enabling interoperability with external validators and schema registries.
- Schema versioning and migration: track schema version history and provide migration helpers that transform data conforming to an older schema version into the current schema, reducing manual upgrade work.
