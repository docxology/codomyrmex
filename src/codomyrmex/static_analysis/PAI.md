# Personal AI Infrastructure — Static Analysis Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Static Analysis module provides PAI integration for code quality analysis.

## PAI Capabilities

### Code Analysis

Analyze code quality:

```python
from codomyrmex.static_analysis import Analyzer

analyzer = Analyzer()
report = analyzer.analyze("src/")

print(f"Issues: {len(report.issues)}")
print(f"Score: {report.quality_score}")
```

### Lint Integration

Run linters:

```python
from codomyrmex.static_analysis import LintRunner

linter = LintRunner(tool="ruff")
issues = linter.run("src/")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Analyzer` | Code analysis |
| `LintRunner` | Run linters |
| `TypeChecker` | Type checking |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
