# Prompt Testing Module — Agent Coordination

## Purpose

Systematic prompt evaluation and A/B testing.

## Key Capabilities

- **EvaluationType**: Types of prompt evaluation.
- **TestStatus**: Status of a test run.
- **PromptTestCase**: A single test case for prompt evaluation.
- **TestResult**: Result of running a single test case.
- **TestSuiteResult**: Result of running a complete test suite.
- `to_dict()`: Convert to dictionary.
- `passed()`: Check if test passed.
- `to_dict()`: Convert to dictionary.

## Agent Usage Patterns

```python
from codomyrmex.prompt_testing import EvaluationType

# Agent initializes prompt testing
instance = EvaluationType()
```

## Integration Points

- **Source**: [src/codomyrmex/prompt_testing/](../../../src/codomyrmex/prompt_testing/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
