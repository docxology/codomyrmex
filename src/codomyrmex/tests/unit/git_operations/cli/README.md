# Git Operations / CLI Tests

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `git_operations/cli` sub-module. Covers CLI metadata management commands (update, show, report, cleanup) and the main entry point.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestCmdUpdateMetadata` | Update command: validation, repo creation, verbose output, overwrite |
| `TestCmdShowMetadata` | Show command: unknown repo, existing repo, all repos, empty manager |
| `TestCmdReport` | Report command: empty/populated manager, JSON export, detailed mode |
| `TestCmdCleanup` | Cleanup command: dry run on empty/populated managers |
| `TestMain` | Main entry point: no args, help flag, invalid metadata file |

## Test Structure

```
tests/unit/git_operations/cli/
    __init__.py
    test_cli_metadata.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/git_operations/cli/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/git_operations/cli/ --cov=src/codomyrmex/git_operations -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../git_operations/README.md)
- [All Tests](../../README.md)
