# Personal AI Infrastructure — Tests Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Tests module provides PAI integration for test automation and coverage.

## PAI Capabilities

### Test Execution

Run tests programmatically:

```python
from codomyrmex.tests import TestRunner

runner = TestRunner()
result = runner.run("tests/")

print(f"Passed: {result.passed}")
print(f"Failed: {result.failed}")
```

### Coverage Tracking

Track test coverage:

```python
from codomyrmex.tests import CoverageReporter

reporter = CoverageReporter()
coverage = reporter.run("tests/")
print(f"Coverage: {coverage.percent}%")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `TestRunner` | Execute tests |
| `CoverageReporter` | Track coverage |
| `TestGenerator` | AI-generated tests |

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.tests import ...`
- CLI: `codomyrmex tests <command>`

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
