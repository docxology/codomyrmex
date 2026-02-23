# Website Test Suite — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Tests ensuring correctness, security, and regression prevention for the `codomyrmex.website` module. Covers static site generation, API endpoints, and data aggregation.

## Design Principles

- **Zero-Mock**: No `unittest.mock.Mock` for internal objects. Tests use real `DataProvider`, `WebsiteGenerator`, and live HTTP servers.
- **Isolation**: Each test creates its own `tmp_path` project tree — no shared mutable state.
- **Determinism**: Tests run offline without external dependencies (Ollama calls are `@patch`-ed).
- **Coverage**: Branch coverage ≥ 85% for `server.py` and `data_provider.py`.

## Functional Requirements

1. **Execution**: All tests run via `uv run python -m pytest`.
2. **Fixture-Based**: Tests use `pytest.fixture` for project trees and server instances.
3. **Security Validation**: Path traversal, absolute path injection, and non-`.md` file access are tested.

## Test Categories

| Category | Files | Coverage Focus |
| -------- | ----- | -------------- |
| Data Provider | `unit/test_data_provider.py` | Module scanning, config I/O, PAI data, security |
| Generator | `unit/test_generator.py` | Template rendering, asset copying, error handling |
| Server | `unit/test_server.py` | All 18 API endpoints via live HTTP, CORS, security |
| Integration | `integration/test_website_integration.py` | Full generation, nested docs, assets, security |

## Navigation

- **Parent**: [../README.md](../README.md)
- **Root**: [../../../../README.md](../../../../README.md)
