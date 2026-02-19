# AI Agent Guidelines - Mocking

**Module**: `codomyrmex.api.mocking`  
**Version**: v0.1.7  
**Status**: Active

## Purpose

API simulation server for development and integration workflows. This provides real HTTP endpoints that simulate external APIs — it is **not** a testing mock/double (see Zero-Mock policy in `general.cursorrules §2`).

## Agent Instructions

When working with this submodule:

### Key Patterns

1. **Import Convention**:

   ```python
   from codomyrmex.api.mocking import <specific_import>
   ```

2. **Error Handling**: Always handle exceptions gracefully
3. **Configuration**: Check for required environment variables

### Common Operations

- Operation 1: Description
- Operation 2: Description

### Integration Points

- Integrates with: `api` (parent module)
- Dependencies: Listed in `__init__.py`

## File Reference

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports and initialization |
| `README.md` | User documentation |
| `SPEC.md` | Technical specification |

## Troubleshooting

Common issues and solutions:

1. **Issue**: Description
   **Solution**: Resolution steps
