# Personal AI Infrastructure — Tests Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Tests module provides PAI integration for test automation and coverage.

## PAI Capabilities

### Test Execution

Run tests through the repository contract:

```python
import subprocess

result = subprocess.run(["uv", "run", "pytest", "tests/"], check=False)
print(f"Exit status: {result.returncode}")
```

### Coverage Tracking

Track coverage with the same 60% release floor:

```python
import subprocess

result = subprocess.run(["make", "test"], check=False)
print(f"Exit status: {result.returncode}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `TestRunner` | Execute tests |
| `CoverageReporter` | Track coverage |
| `TestGenerator` | AI-generated tests |

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Repository command: `uv run pytest tests/`
- Release gate: `make test`

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
