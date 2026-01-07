# Codomyrmex Unified Testing Architecture

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This directory contains the unified testing architecture for Codomyrmex. All unit and integration tests are organized here to maintain a clean and modular source directory.

## Structure

- `unit/` - Unit tests organized by module (e.g., `unit/fpf/`, `unit/website/`, `unit/agents/`).
- `integration/` - End-to-end and cross-module integration tests.
- `fixtures/` - Shared test data and mock resources.
- `performance/` - Benchmarks and performance tests.
- `conftest.py` - Root pytest configuration and shared fixtures.

## Running Tests

To run the full test suite, ensure you are in the project root and set the `PYTHONPATH`:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest src/codomyrmex/tests
```

To run tests for a specific module:

```bash
pytest src/codomyrmex/tests/unit/website
```

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)
    - [Running Tests Detailed Guide](RUNNING_TESTS.md)

## Navigation
- **Project Root**: [README](../../../README.md)
- **Source Root**: [src](../../README.md)
