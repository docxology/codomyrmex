# Integration Tests — Website Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

End-to-end integration tests for the `codomyrmex.website` module. Tests exercise the full pipeline from project scanning through HTML generation, plus security validation.

## Test Categories

| Category | What It Tests |
| -------- | ------------- |
| Full Generation | DataProvider → WebsiteGenerator → 10 HTML pages + assets |
| Config Operations | Read/write cycle for TOML and YAML config files |
| Documentation Tree | Nested directory scanning for `.md` files |
| Assets Copying | CSS/JS assets copied to output directory |
| Server Integration | Handler method existence and class attributes |
| Security | Path traversal, absolute path injection, non-`.md` file rejection |

## Running

```bash
uv run python -m pytest src/codomyrmex/tests/unit/website/integration/ -v
```

## Navigation

- **Parent Module**: [website](../README.md)
- **Project Root**: [codomyrmex](../../../../../README.md)
