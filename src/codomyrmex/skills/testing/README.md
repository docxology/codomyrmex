# Testing

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Skill testing framework. Provides utilities for validating skill metadata, running test cases against skills, and benchmarking skill execution performance.

## Key Exports

- **`SkillTestRunner`** -- Test harness for skills with three modes:
  - `test_skill(skill, test_cases)` -- Run test cases (each a dict with "name", "inputs", and optional "expected") and return pass/fail results
  - `validate_skill(skill)` -- Validate that a skill has required metadata (name, description, id) and interface methods (execute, validate_params)
  - `benchmark_skill(skill, iterations, **kwargs)` -- Benchmark execution performance returning min, max, avg, and total times with error count
- **`SkillTestResult`** -- Result of a single test case with name, passed flag, expected/actual values, and error message

## Directory Contents

- `__init__.py` - SkillTestRunner and SkillTestResult (170 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.skills.testing import SkillTestRunner

runner = SkillTestRunner()

# Run test cases
results = runner.test_skill(my_skill, [
    {"name": "basic", "inputs": {"text": "hello"}, "expected": "HELLO"},
    {"name": "empty", "inputs": {"text": ""}},
])

# Validate metadata
validation = runner.validate_skill(my_skill)
print(validation["valid"])  # True or False

# Benchmark
benchmark = runner.benchmark_skill(my_skill, iterations=1000, text="test")
print(f"Avg: {benchmark['avg_time']:.4f}s")
```

## Navigation

- **Parent Module**: [skills](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
