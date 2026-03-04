# Validation Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Validation utilities for system integrity and integration checks. The top-level package exports a PAI integration validator and shared result types used across 74+ codomyrmex modules. Additional validation capabilities (schema validation, config validation, validation summaries) are available via submodules and MCP tools.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Validate schemas and configs at system boundaries before use | `validate_schema`, `validate_config` |
| **VERIFY** | Run full validation suite to confirm system correctness | `validate_schema`, `validate_config`, `validation_summary` |

PAI's validation module is a cornerstone of the VERIFY phase. QATester agents call `validate_schema` and `validate_config` to confirm correctness; `validation_summary` aggregates results for reporting. Engineer agents use validation at BUILD-phase boundaries.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

The top-level `codomyrmex.validation` package exports three items (see `__init__.py`):

| Export | Type | Description |
|--------|------|-------------|
| `validate_pai_integration` | Function | Validates PAI system integration and returns a diagnostic report |
| `Result` | Class | Shared result container imported from `validation.schemas` |
| `ResultStatus` | Enum | Status enum (`OK`, `ERROR`, etc.) imported from `validation.schemas` |

> **Note**: The full validation API -- including `validate_schema`, `validate_config`, and `validation_summary` MCP tools -- is available via submodules (`validation.schemas`, `validation.pai`) and through the MCP tool interface.

## Directory Contents

- `__init__.py` -- Package exports (`validate_pai_integration`, `Result`, `ResultStatus`)
- `pai.py` -- PAI integration validation logic
- `schemas/` -- Shared `Result` and `ResultStatus` types used for cross-module interop

## Quick Start

```python
from codomyrmex.validation import Result, ResultStatus, validate_pai_integration

# Check a result
result = Result(status=ResultStatus.OK, message="Validation passed")
print(result.status)  # ResultStatus.OK

# Validate PAI integration
report = validate_pai_integration()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k validation -v
```

## Submodules

| Sub-module | Description |
|------------|-------------|
| **`schemas/`** | Shared `Result` and `ResultStatus` types used by 74+ modules for cross-module interop |
| **`pai.py`** | PAI integration validation (`validate_pai_integration`) |

## Navigation

- **Full Documentation**: [docs/modules/validation/](../../../docs/modules/validation/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
