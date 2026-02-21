# Testing Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Testing module provides test fixtures, data generators, and utilities for the Codomyrmex test suite. It offers a comprehensive toolkit for creating reproducible test data, managing fixture lifecycles with scoped cleanup, and building structured datasets for integration and unit testing scenarios.

## Key Features

- **Test Data Generation**: Type-aware generators for strings, integers, floats, booleans, dates, emails, UUIDs, names, and arbitrary choices
- **Fixture Management**: Scoped fixture lifecycle management (function, class, module, session) with dependency resolution and automatic cleanup
- **Data Fixtures**: Pre-defined data collections with filtering and lookup capabilities
- **Record and Dataset Generation**: Composite generators for producing structured records and complete datasets with CSV export
- **JSON Fixture Loading**: File-based fixture loading with caching for efficient test setup
- **Fluent Fixture Building**: Builder pattern for constructing test data with chained method calls

## Key Components

### Generators (`generators/`)

| Component | Description |
|-----------|-------------|
| `Generator` | Abstract base class for all data generators with `generate()` and `generate_many()` methods |
| `StringGenerator` | Generates random strings with configurable length and character set |
| `IntegerGenerator` | Generates random integers within a configurable range |
| `FloatGenerator` | Generates random floats with configurable precision |
| `BooleanGenerator` | Generates random booleans with configurable true probability |
| `DateGenerator` | Generates random datetimes within a configurable date range |
| `EmailGenerator` | Generates random email addresses with realistic domains |
| `UUIDGenerator` | Generates UUID-formatted identifier strings |
| `NameGenerator` | Generates random first and last name combinations |
| `ChoiceGenerator` | Generates random selections from a provided list |
| `RecordGenerator` | Composes multiple field generators into structured record output |
| `DatasetGenerator` | Generates complete multi-column datasets with CSV export support |
| `DataType` | Enum defining supported generated data types |
| `FieldSpec` | Dataclass for specifying generated field constraints |

### Fixtures (`fixtures/`)

| Component | Description |
|-----------|-------------|
| `FixtureManager` | Core fixture registry with scoped lifecycle management and dependency resolution |
| `DataFixture` | Pre-defined data collection with `filter()`, `find()`, and iteration support |
| `JSONFixtureLoader` | Loads fixture data from JSON files with built-in caching |
| `FixtureBuilder` | Fluent builder for constructing fixture data with `with_field()` chaining |
| `FixtureScope` | Enum defining fixture scopes: `FUNCTION`, `CLASS`, `MODULE`, `SESSION` |
| `FixtureDefinition` | Dataclass describing a fixture's factory, scope, cleanup, and dependencies |
| `FixtureInstance` | Dataclass representing an instantiated fixture with creation timestamp |

## Quick Start

### Generating Test Data

```python
from codomyrmex.testing.generators import (
    NameGenerator, EmailGenerator, IntegerGenerator,
    RecordGenerator, DatasetGenerator, UUIDGenerator
)

# Generate individual values
names = NameGenerator()
print(names.generate())         # "Alice Johnson"
print(names.generate_many(5))   # List of 5 random names

# Build structured records
gen = RecordGenerator()
gen.add_field("name", NameGenerator())
gen.add_field("email", EmailGenerator())
gen.add_field("age", IntegerGenerator(18, 65))

record = gen.generate()
records = gen.generate_many(100)

# Generate complete datasets
dataset = DatasetGenerator("users")
dataset.add_column("id", UUIDGenerator())
dataset.add_column("name", NameGenerator())
csv_output = dataset.generate_csv(rows=1000)
```

### Managing Fixtures

```python
from codomyrmex.testing.fixtures import (
    FixtureManager, DataFixture, JSONFixtureLoader, FixtureBuilder
)

# Register and use fixtures with lifecycle management
fixtures = FixtureManager()
fixtures.register("db", lambda: create_test_db(), cleanup=lambda db: db.close())

with fixtures.use("db") as db:
    # Test with database fixture - auto-cleanup on exit
    pass

# Pre-defined data fixtures
users = DataFixture([
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
])
active_users = users.filter(active=True)

# Fluent fixture building
user = (FixtureBuilder("user")
    .with_field("id", 1)
    .with_field("name", "Test User")
    .with_field("active", True)
    .build())
```

## Related Modules

- [testing](../testing/) - End-to-end workflow validation that complements unit-level test utilities
- [logging_monitoring](../logging_monitoring/) - Structured logging for test output and diagnostics

## Navigation

- **Source**: [src/codomyrmex/testing/](../../../src/codomyrmex/testing/)
- **Parent**: [docs/modules/](../README.md)
