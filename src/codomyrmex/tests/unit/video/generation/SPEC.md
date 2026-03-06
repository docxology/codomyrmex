# Video / Generation Test Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `video/generation` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/video/generation/
    __init__.py
    test_video_generation.py
```

## Functional Requirements

1. All public API methods in `video` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra video` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../../../video/)
