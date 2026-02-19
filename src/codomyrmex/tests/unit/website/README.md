# Website Test Suite

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Test suite for the `codomyrmex.website` module covering `DataProvider`, `WebsiteGenerator`, and `WebsiteServer`. All tests follow the **Zero-Mock policy** — no `unittest.mock.Mock` is used except for external service calls (Ollama).

## Directory Structure

| Directory | Purpose | Test Count |
| --------- | ------- | ---------- |
| `unit/` | Isolated unit tests for each class | ~95 |
| `integration/` | End-to-end generation and security tests | ~80 |
| Root files | Smoke tests for quick validation | ~6 |

## Test Files

- `test_website_data_provider.py` — Smoke tests for `DataProvider` initialisation
- `test_website_generator.py` — Smoke tests for `WebsiteGenerator` output
- `unit/test_data_provider.py` — Comprehensive `DataProvider` unit tests
- `unit/test_generator.py` — `WebsiteGenerator` rendering and asset copying
- `unit/test_server.py` — Live HTTP server tests for all 18 API endpoints
- `integration/test_website_integration.py` — Full generation, security, and config operations

## Running

```bash
uv run python -m pytest src/codomyrmex/tests/unit/website/ -v
```

## Navigation

- **Parent Module**: [unit](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
