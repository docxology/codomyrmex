# Personal AI Infrastructure — Website Tests

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: website tests
**Status**: Active

## Context

Unit and integration tests for the website module using pytest fixtures and real functional objects. Zero-Mock compliant — no internal mocking of `DataProvider`, `WebsiteGenerator`, or `WebsiteServer`.

## AI Strategy

As an AI agent working with this test suite:

1. **Never use `unittest.mock.Mock`** for internal objects — use real instances with `tmp_path` project trees.
2. **Use `live_server` fixture** for HTTP endpoint tests — it starts a real `TCPServer`.
3. **Only mock external services** — `@patch("codomyrmex.website.server.requests")` for Ollama calls.
4. **Verify real state** — check actual file contents, HTTP response bodies, and status codes.

## Key Files

- `unit/test_server.py`: Live HTTP server tests with `_LiveServer` helper
- `unit/test_generator.py`: Real Jinja2 template rendering tests
- `unit/test_data_provider.py`: Real filesystem scanning tests
- `integration/test_website_integration.py`: Full pipeline tests

## Future Considerations

- Add WebSocket tests if real-time features are added.
- Expand security tests for CSRF token validation.
