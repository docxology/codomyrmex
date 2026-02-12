# Agent Guide — Website Test Suite

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Validation suite for the `codomyrmex.website` module. Tests verify `DataProvider`, `WebsiteGenerator`, and `WebsiteServer` using real objects and live HTTP requests.

## Testing Patterns

### Zero-Mock Policy

All tests use real functional objects:

```python
# ✅ Correct — real DataProvider with temp project tree
provider = DataProvider(tmp_path)
modules = provider.get_modules()
assert isinstance(modules, list)

# ✅ Correct — live HTTP server with real requests
srv = _LiveServer(tmp_path)
status, data = srv.get("/api/status")
assert status == 200
```

The only permitted `@patch` usage is for external services (Ollama):

```python
@patch("codomyrmex.website.server.requests")
def test_chat(self, mock_requests, live_server):
    ...
```

### Fixture Patterns

- `tmp_path` + `_build_project()` — creates minimal project tree for `DataProvider`
- `live_server` — starts a real `TCPServer` + `WebsiteServer` on a random port
- `simple_template_dir` — creates minimal Jinja2 templates for rendering tests

## Active Components

- `unit/` — Isolated unit tests (data_provider, generator, server)
- `integration/` — End-to-end generation, security, and config tests
- `test_website_data_provider.py` — DataProvider smoke tests
- `test_website_generator.py` — Generator smoke tests

## Navigation Links

- **📁 Parent Directory**: [unit](../README.md)
- **🏠 Project Root**: [codomyrmex](../../../../README.md)
