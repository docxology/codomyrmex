# performance

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Validation coverage, fixtures, and regression checks for Performance.

These tests are intentionally marked `performance` (and the pytest-benchmark
cases are also marked `benchmark`). They are informational and are excluded
from the default unit/integration coverage gate because timing-sensitive tests
can mutate process-wide registries. Run them explicitly with:

```bash
uv run pytest tests/performance -m performance
```

## Directory Contents
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `conftest.py` – File
- `py.typed` – File
- `test_benchmarking.py` – File
- `test_benchmarks.py` – File
- `test_lazy_imports.py` – File
- `test_mcp_load.py` – File
- `test_mcp_performance.py` – File
- `test_module_performance.py` – File

## Navigation
- **Parent Directory**: [tests](../README.md)
- **Project Root**: ../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
