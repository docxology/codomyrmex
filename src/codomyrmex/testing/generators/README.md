# generators

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Test data generation utilities for producing typed random data. Provides composable generators for strings, integers, floats, booleans, dates, emails, UUIDs, and names, plus composite `RecordGenerator` and `DatasetGenerator` for structured test data and CSV output.

## Key Exports

- **`RecordGenerator`** — Generates structured records from field-level generators with `add_field()` and `generate_many(count)`
- **`DatasetGenerator`** — Generates complete datasets with named columns, supports `generate(rows=N)` and `generate_csv()`
- **`StringGenerator`** — Configurable random strings (min/max length, charset)
- **`IntegerGenerator`** — Random integers within min/max bounds
- **`FloatGenerator`** — Random floats with configurable precision
- **`BooleanGenerator`** — Random booleans with configurable true probability
- **`DateGenerator`** — Random dates within a start/end range
- **`EmailGenerator`** — Random email addresses with realistic domains
- **`UUIDGenerator`** — UUID-like string generation
- **`NameGenerator`** — Random first/last name combinations
- **`ChoiceGenerator`** — Random selection from a provided list
- **`Generator`** — Abstract base class with `generate()` and `generate_many(count)`
- **`DataType`** — Enum: STRING, INTEGER, FLOAT, BOOLEAN, DATE, EMAIL, UUID, NAME, ADDRESS, PHONE
- **`FieldSpec`** — Dataclass specifying a generated field (name, type, nullable, unique, min/max, choices, pattern)

## Navigation

- **Parent Module**: [testing](../README.md)
- **Parent Directory**: [codomyrmex](../../README.md)
