# Generators -- Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Test data generation module providing typed generators for 9 data types, composite record/dataset builders, and CSV export. All generators follow a common ABC protocol for composability.

## Architecture

```
generators/
  __init__.py  -- Generator ABC, 9 concrete generators, RecordGenerator, DatasetGenerator, DataType, FieldSpec
```

## Key Classes

### Generator (ABC)

| Method | Signature | Description |
|--------|-----------|-------------|
| `generate` | `() -> Any` | Generate a single value (abstract) |
| `generate_many` | `(count: int) -> list[Any]` | Generate N values via repeated `generate()` calls |

### Concrete Generators

| Generator | Output Type | Constructor Parameters |
|-----------|-------------|----------------------|
| `StringGenerator` | `str` | `min_length=5`, `max_length=20`, `charset=ascii_letters+digits` |
| `IntegerGenerator` | `int` | `min_value=0`, `max_value=1000` |
| `FloatGenerator` | `float` | `min_value=0.0`, `max_value=100.0`, `precision=2` |
| `BooleanGenerator` | `bool` | `true_probability=0.5` |
| `DateGenerator` | `datetime` | `start_date=datetime(2020,1,1)`, `end_date=datetime.now()` |
| `EmailGenerator` | `str` | (none) -- uses `StringGenerator` internally for usernames |
| `UUIDGenerator` | `str` | (none) -- generates 8-4-4-4-12 hex string |
| `NameGenerator` | `str` | (none) -- combines from 8 first + 8 last name lists |
| `ChoiceGenerator` | `Any` | `choices: list[Any]` (required) |

### RecordGenerator

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_field` | `(name: str, generator: Generator) -> RecordGenerator` | Register field generator (fluent) |
| `generate` | `() -> dict[str, Any]` | Generate one record |
| `generate_many` | `(count: int) -> list[dict]` | Generate N records |

### DatasetGenerator

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_column` | `(name: str, generator: Generator) -> DatasetGenerator` | Register column generator (fluent) |
| `columns` | `-> list[str]` (property) | Get column names |
| `generate` | `(rows: int = 100) -> list[dict]` | Generate dataset as list of dicts |
| `generate_csv` | `(rows: int = 100) -> str` | Generate dataset as CSV string with header row |

### DataType (Enum)

Values: `STRING`, `INTEGER`, `FLOAT`, `BOOLEAN`, `DATE`, `EMAIL`, `UUID`, `NAME`, `ADDRESS`, `PHONE`

### FieldSpec (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Field name |
| `data_type` | `DataType` | required | Data type for generation |
| `nullable` | `bool` | `False` | Whether field can be None |
| `unique` | `bool` | `False` | Whether values must be unique |
| `min_value` | `int | float | None` | `None` | Minimum numeric value |
| `max_value` | `int | float | None` | `None` | Maximum numeric value |
| `choices` | `list[Any] | None` | `None` | Constrained value set |
| `pattern` | `str | None` | `None` | Regex pattern constraint |

## Dependencies

- Standard library only: `random`, `string`, `hashlib`, `datetime`, `abc`, `dataclasses`, `enum`

## Constraints

- `UUIDGenerator` produces UUID-like strings but does not follow RFC 4122 (no version/variant bits).
- `EmailGenerator` uses 4 hardcoded domains. `NameGenerator` uses 8+8 hardcoded name lists.
- `DatasetGenerator.generate_csv()` does not escape commas in values; callers must ensure values do not contain commas.
- `FieldSpec` constraints (`nullable`, `unique`, `pattern`) are schema declarations only; the concrete generators do not automatically enforce them.
- `DateGenerator` generates dates at day granularity (no sub-day precision).

## Error Handling

- `ChoiceGenerator` raises `IndexError` if initialized with an empty `choices` list (via `random.choice`).
- No custom exceptions defined; generators rely on stdlib exceptions for invalid configurations.
