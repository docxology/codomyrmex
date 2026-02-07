# Prompt Testing — Functional Specification

**Module**: `codomyrmex.prompt_testing`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Systematic prompt evaluation and A/B testing.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `EvaluationType` | Class | Types of prompt evaluation. |
| `TestStatus` | Class | Status of a test run. |
| `PromptTestCase` | Class | A single test case for prompt evaluation. |
| `TestResult` | Class | Result of running a single test case. |
| `TestSuiteResult` | Class | Result of running a complete test suite. |
| `Evaluator` | Class | Base class for output evaluators. |
| `ExactMatchEvaluator` | Class | Evaluator for exact matches. |
| `ContainsEvaluator` | Class | Evaluator for substring containment. |
| `CustomEvaluator` | Class | Evaluator using custom function. |
| `PromptTestSuite` | Class | Collection of test cases for prompt evaluation. |
| `to_dict()` | Function | Convert to dictionary. |
| `passed()` | Function | Check if test passed. |
| `to_dict()` | Function | Convert to dictionary. |
| `total_tests()` | Function | Get total number of tests. |
| `passed_tests()` | Function | Get number of passed tests. |

## 3. Dependencies

See `src/codomyrmex/prompt_testing/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.prompt_testing import EvaluationType, TestStatus, PromptTestCase, TestResult, TestSuiteResult
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k prompt_testing -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/prompt_testing/)
