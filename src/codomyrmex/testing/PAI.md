# Personal AI Infrastructure — Testing Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Testing module provides PAI integration for test automation, enabling AI agents to generate, run, and validate tests.

## PAI Capabilities

### AI-Generated Tests

Use AI to generate test cases:

```python
from codomyrmex.testing import TestGenerator
from codomyrmex.llm import LLMClient

# Generate tests from code
generator = TestGenerator(llm=LLMClient())

test_code = generator.generate_tests(
    source_file="src/auth.py",
    coverage_target=0.8
)

# Write generated tests
with open("tests/test_auth.py", "w") as f:
    f.write(test_code)
```

### Test Execution

Run tests programmatically:

```python
from codomyrmex.testing import TestRunner, CoverageReporter

# Run tests
runner = TestRunner()
result = runner.run("tests/")

print(f"Passed: {result.passed}")
print(f"Failed: {result.failed}")

# Coverage report
coverage = CoverageReporter()
coverage.run_with_coverage("tests/")
print(f"Coverage: {coverage.total_coverage}%")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `TestGenerator` | AI test generation |
| `TestRunner` | Automated test execution |
| `CoverageReporter` | Coverage tracking |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
