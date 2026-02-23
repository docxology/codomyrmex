# Unit Tests — Website Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Isolated unit tests for the three core website classes: `DataProvider`, `WebsiteGenerator`, and `WebsiteServer`. All tests follow the Zero-Mock policy.

## Test Files

| File | Class Under Test | Strategy |
| ---- | --------------- | -------- |
| `test_data_provider.py` | `DataProvider` | Real filesystem with `tmp_path` project trees |
| `test_generator.py` | `WebsiteGenerator` | Real Jinja2 templates and real `DataProvider` |
| `test_server.py` | `WebsiteServer` | Live `TCPServer` with real HTTP requests |

## Running

```bash
uv run python -m pytest src/codomyrmex/tests/unit/website/unit/ -v
```

## Navigation

- **Parent Module**: [website](../README.md)
- **Project Root**: [codomyrmex](../../../../../README.md)
