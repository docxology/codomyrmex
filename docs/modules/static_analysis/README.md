# Static Analysis Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Code analysis: linting, type checking, complexity analysis, and security scanning.

## Key Features

- **Linting** — Ruff, flake8 integration
- **Types** — Mypy type checking
- **Complexity** — Cyclomatic complexity
- **Security** — Security vulnerability scan

## Quick Start

```python
from codomyrmex.static_analysis import Analyzer, LintRunner

analyzer = Analyzer()
report = analyzer.analyze("src/")

linter = LintRunner(tool="ruff")
issues = linter.run("src/main.py")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/static_analysis/](../../../src/codomyrmex/static_analysis/)
- **Parent**: [Modules](../README.md)
