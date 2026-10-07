# Personal AI Infrastructure — Testing Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Testing module provides PAI integration for test automation, enabling AI agents to generate, run, and validate tests.

## PAI Capabilities

### Generated Test Scaffolds

Generate test scaffolds from source code for an agent to fill in. The generator lives in the `coding` module:

```python
from pathlib import Path

from codomyrmex.coding.test_generator import TestGenerator

# Generate test stubs from code
generator = TestGenerator()
suite = generator.from_source(Path("src/auth.py").read_text(), module_name="auth")

# Write generated tests
Path("tests/test_auth.py").write_text(suite.render())
```

`TestGenerator` parses the source with `ast` and emits one stub per public function, class and public method (`# TODO` plus `assert True`). It does not call an LLM; the agent replaces each stub body with real assertions.

### Test Execution

The module does not wrap the test runner; run pytest (with pytest-cov) directly:

```python
import pytest

# Run tests with coverage; a non-zero exit code means failures or coverage below the floor
exit_code = pytest.main(["tests/", "-q", "--cov=src/codomyrmex", "--cov-fail-under=60"])
print(f"pytest exit code: {exit_code}")
```

## PAI Integration Points

| Component | PAI Use Case |
| --- | --- |
| `coding.test_generator.TestGenerator` | Test scaffold generation |
| `pytest` / `pytest-cov` | Automated test execution and coverage tracking |
| `testing.property_test`, `testing.Fuzzer` | Property-based and fuzz testing |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
