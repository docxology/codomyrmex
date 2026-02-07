# Testing Module — Agent Coordination

## Purpose

Test fixtures, generators, property-based testing, and fuzzing utilities.

## Key Capabilities

- **GeneratorStrategy**: Abstract base for value generators.
- **IntGenerator**: Generate random integers.
- **FloatGenerator**: Generate random floats.
- **StringGenerator**: Generate random strings.
- **ListGenerator**: Generate random lists.
- `property_test()`: Decorator for property-based tests.
- `fixture()`: Decorator to create fixtures.
- `generate()`: generate

## Agent Usage Patterns

```python
from codomyrmex.testing import GeneratorStrategy

# Agent initializes testing
instance = GeneratorStrategy()
```

## Integration Points

- **Source**: [src/codomyrmex/testing/](../../../src/codomyrmex/testing/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Key Components

- **`GeneratorStrategy`** — Abstract base for value generators.
- **`IntGenerator`** — Generate random integers.
- **`FloatGenerator`** — Generate random floats.
- **`StringGenerator`** — Generate random strings.
- **`ListGenerator`** — Generate random lists.
- **`property_test()`** — Decorator for property-based tests.
- **`fixture()`** — Decorator to create fixtures.

### Submodules

- `fixtures` — Fixtures
- `generators` — Generators

