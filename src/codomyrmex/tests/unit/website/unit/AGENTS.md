# Agent Guide — Website Unit Tests

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Unit-level validation for `DataProvider`, `WebsiteGenerator`, and `WebsiteServer`. Tests run in isolation using temporary project trees and ephemeral HTTP servers.

## Active Components

- `test_data_provider.py` — Tests for module scanning, config I/O, PAI data, health status, and security (path traversal, symlink escape)
- `test_generator.py` — Tests for Jinja2 template rendering, asset copying, output directory management, and error handling
- `test_server.py` — Tests for all 18 API endpoints via live HTTP requests, CORS preflight, origin validation, and Ollama proxy (mocked external)

## Testing Patterns

```python
# Live HTTP server fixture — each test gets its own server on a random port
@pytest.fixture
def live_server(tmp_path):
    root = _build_project(tmp_path)
    srv = _LiveServer(root)
    yield srv
    srv.shutdown()

# Real DataProvider — no mocking
provider = DataProvider(tmp_path)
assert isinstance(provider.get_modules(), list)
```

## Navigation Links

- **📁 Parent Directory**: [website](../README.md)
- **🏠 Project Root**: [codomyrmex](../../../../../README.md)
