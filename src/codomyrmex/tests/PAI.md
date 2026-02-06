# Personal AI Infrastructure — Tests Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

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

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
