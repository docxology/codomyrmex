# Testing — Functional Specification

**Module**: `codomyrmex.testing`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Test fixtures, generators, property-based testing, and fuzzing utilities.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `GeneratorStrategy` | Class | Abstract base for value generators. |
| `IntGenerator` | Class | Generate random integers. |
| `FloatGenerator` | Class | Generate random floats. |
| `StringGenerator` | Class | Generate random strings. |
| `ListGenerator` | Class | Generate random lists. |
| `DictGenerator` | Class | Generate random dictionaries. |
| `OneOfGenerator` | Class | Generate one of specified values. |
| `PropertyTestResult` | Class | Result of a property-based test. |
| `FuzzingStrategy` | Class | Fuzzing strategies. |
| `FuzzResult` | Class | Result of a fuzz test. |
| `property_test()` | Function | Decorator for property-based tests. |
| `fixture()` | Function | Decorator to create fixtures. |
| `generate()` | Function | generate |
| `generate()` | Function | generate |
| `generate()` | Function | generate |

### Submodule Structure

- `fixtures/` — Testing Fixtures Module
- `generators/` — Testing Generators Module

## 3. Dependencies

See `src/codomyrmex/testing/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.testing import GeneratorStrategy, IntGenerator, FloatGenerator, StringGenerator, ListGenerator
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k testing -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/testing/)
