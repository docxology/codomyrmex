# Generators -- Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides test data generation utilities with typed generators for common data types, composite record generators, and dataset generators with CSV export. Agents use this module to create realistic test data without external dependencies.

## Key Components

| Component | Source | Role |
|-----------|--------|------|
| `Generator` (ABC) | `__init__.py` | Base class with `generate()` and `generate_many(count)` |
| `StringGenerator` | `__init__.py` | Random strings with configurable `min_length`, `max_length`, `charset` |
| `IntegerGenerator` | `__init__.py` | Random integers in `[min_value, max_value]` range (default 0--1000) |
| `FloatGenerator` | `__init__.py` | Random floats with configurable `precision` (default 2 decimal places) |
| `BooleanGenerator` | `__init__.py` | Random booleans with configurable `true_probability` (default 0.5) |
| `DateGenerator` | `__init__.py` | Random `datetime` between `start_date` and `end_date` |
| `EmailGenerator` | `__init__.py` | Random emails from 4 domains: example.com, test.org, mail.net, demo.io |
| `UUIDGenerator` | `__init__.py` | UUID-like strings (8-4-4-4-12 hex format, not RFC 4122 compliant) |
| `NameGenerator` | `__init__.py` | Random full names from 8 first names and 8 last names |
| `ChoiceGenerator` | `__init__.py` | Random selection from a provided list |
| `RecordGenerator` | `__init__.py` | Composite: field-name-to-generator mapping, produces `dict[str, Any]` |
| `DatasetGenerator` | `__init__.py` | Column-based: produces row lists with `generate(rows)` and `generate_csv(rows)` |

## Operating Contracts

1. **Generator Protocol**: All generators extend `Generator` ABC and implement `generate() -> Any`. `generate_many(count)` is inherited and calls `generate()` N times.
2. **Composition**: `RecordGenerator.add_field(name, generator)` and `DatasetGenerator.add_column(name, generator)` accept any `Generator` subclass, enabling nested composition.
3. **CSV Export**: `DatasetGenerator.generate_csv()` produces comma-separated output with header row. Values are stringified via `str()`.
4. **Randomness**: All generators use `random` module (not cryptographically secure). Seed via `random.seed()` for reproducibility.
5. **No External Dependencies**: Pure Python implementation using only `random`, `string`, `datetime` from stdlib.

## Integration Points

- **testing parent**: Part of the `testing` module alongside `chaos`, `fixtures`, and `workflow`
- **DataType enum**: Defines 10 types (STRING, INTEGER, FLOAT, BOOLEAN, DATE, EMAIL, UUID, NAME, ADDRESS, PHONE) for schema-driven generation
- **FieldSpec dataclass**: Structured field specification with `nullable`, `unique`, `min_value`, `max_value`, `choices`, `pattern` constraints

## Navigation

- **Parent**: [testing/](../README.md)
- **Siblings**: [chaos/](../chaos/), [fixtures/](../fixtures/), [workflow/](../workflow/)
- **Spec**: [SPEC.md](SPEC.md)
