# Testing Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Test fixtures, generators, and utilities for the Codomyrmex test suite. Provides a structured framework for creating reusable test data, managing fixture lifecycles with scoping and dependency resolution, and generating random typed data for property-based and integration testing.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **VERIFY** | Define and run test strategies with fixture management | Direct Python import |
| **BUILD** | Write test cases using generators and fixture builders | Direct Python import |
| **OBSERVE** | Analyze test coverage and fixture dependency graphs | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge for test data generation and fixture lifecycle management.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Fixtures (`fixture_utils.py` & `fixtures/`)

- **`FixtureManager`** — Core fixture lifecycle manager with `register()`, `get()`, `cleanup()`, and context manager `use()`. Supports scoped fixtures (function, class, module, session) and dependency resolution.
- **`DataFixture`** — Pre-defined data fixture with `filter()`, `find()`, and `all()` methods for querying test records.
- **`JSONFixtureLoader`** — Loads fixtures from JSON files with caching. Instantiated with a base path, then `load("name")` returns a `DataFixture`.
- **`FixtureBuilder`** — Fluent builder for creating fixture data: `FixtureBuilder("user").with_field("name", "Alice").build()`.
- **`FixtureScope`** — Enum: `FUNCTION`, `CLASS`, `MODULE`, `SESSION`.

### Generators (`strategies.py` & `generators/`)

- **`RecordGenerator`** — Generates structured records from field-level generators: `gen.add_field("name", NameGenerator()).generate()`.
- **`DatasetGenerator`** — Generates complete datasets with `generate(rows=N)` and `generate_csv()`.
- **Type Generators** — `StringGenerator`, `IntegerGenerator`, `FloatGenerator`, `BooleanGenerator`, `DateGenerator`, `EmailGenerator`, `UUIDGenerator`, `NameGenerator`, `ChoiceGenerator`.
- **`DataType`** — Enum of supported types: STRING, INTEGER, FLOAT, BOOLEAN, DATE, EMAIL, UUID, NAME, ADDRESS, PHONE.

## Usage

```python
from codomyrmex.testing.fixture_utils import FixtureManager, FixtureScope
from codomyrmex.testing.strategies import RecordGenerator, NameGenerator, EmailGenerator

# Fixture management
fixtures = FixtureManager()
fixtures.register("db", lambda: create_test_db(), scope=FixtureScope.SESSION)

with fixtures.use("db") as db:
    # test with db fixture
    pass

# Data generation
gen = RecordGenerator()
gen.add_field("name", NameGenerator())
gen.add_field("email", EmailGenerator())
records = gen.generate_many(100)
```

## Directory Contents

- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Functional specification
- `PAI.md` - PAI integration details
- `fixtures/` - Fixture management (pre-existing subpackage)
- `generators/` - Data generators (pre-existing subpackage)
- `fixture_utils.py` - Core fixture utilities (FixtureManager, decorator)
- `strategies.py` - Generation strategies (GeneratorStrategy, IntGenerator, etc.)

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`workflow/`** | Workflow validation and end-to-end testing |
| **`chaos/`** | Fault injection and resilience testing |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/testing/](../../../docs/modules/testing/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
