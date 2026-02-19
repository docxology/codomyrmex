# Agent Guide — Website Integration Tests

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

End-to-end validation ensuring the full website generation pipeline produces correct output and security controls are enforced.

## Active Components

- `test_website_integration.py` — Comprehensive integration test suite covering:
  - `TestFullWebsiteGeneration` — DataProvider data collection, 10-page generation, content verification
  - `TestConfigOperations` — Config read/write round-trip
  - `TestDocumentationTree` — Nested doc structure scanning
  - `TestAssetsCopying` — CSS/JS asset pipeline
  - `TestWebsiteServerIntegration` — Server class attributes and handler method existence
  - `TestSecurityIntegration` — Path traversal, absolute path, and file type restrictions

## Testing Patterns

```python
# Full project fixture with modules, scripts, configs, and docs
@pytest.fixture
def project_structure(self, tmp_path):
    (tmp_path / "src" / "codomyrmex").mkdir(parents=True)
    module1 = tmp_path / "src" / "codomyrmex" / "coding"
    module1.mkdir()
    (module1 / "__init__.py").write_text('"""Code editing module."""')
    ...
```

## Navigation Links

- **📁 Parent Directory**: [website](../README.md)
- **🏠 Project Root**: [codomyrmex](../../../../../README.md)
