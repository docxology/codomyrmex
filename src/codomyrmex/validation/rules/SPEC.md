# Technical Specification - Rules

**Version**: v1.0.0 | **Status**: Planned | **Last Updated**: February 2026

**Module**: `codomyrmex.validation.rules`  
**Last Updated**: 2026-01-29

## 1. Purpose

Custom validation rule definitions and composition

## 2. Architecture

### 2.1 Components

```
rules/
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
# No exports defined yet (scaffolded for future implementation)
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Rule composability**: Validation rules are independent callables; multiple rules are applied in sequence, collecting all failures rather than stopping at first failure.

### 4.2 Limitations

- No rule priority ordering — all rules at the same level run regardless of earlier failures.
- Rules do not cross-reference other fields by default; multi-field constraints require custom rule implementations.

## 5. Testing

```bash
# Run tests for this module
pytest tests/validation_rules/
```

## 6. Future Considerations

- Rule composition and chaining: provide `AND`, `OR`, and `NOT` combinators so complex validation policies can be built by composing simple atomic rules rather than writing monolithic validators.
- Cross-field validation: add a context-aware rule interface that receives the full data object, enabling constraints that span multiple fields (e.g., `end_date > start_date`).
- Async rule evaluation: support `async def` rule callables so external lookups (e.g., uniqueness checks against a database) can be performed without blocking the event loop.
