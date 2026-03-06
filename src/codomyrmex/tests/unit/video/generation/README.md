# Video / Generation Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `video/generation` sub-module. Covers VideoGenerator initialization and video generation using the Gemini client.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestVideoGenerator` | Default client creation, provided client usage, video generation success, client call verification |

## Test Structure

```
tests/unit/video/generation/
    __init__.py
    test_video_generation.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/video/generation/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/video/generation/ --cov=src/codomyrmex/video -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../video/README.md)
- [All Tests](../../README.md)
