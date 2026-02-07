# Prompt Testing Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Systematic prompt evaluation and A/B testing framework. Provides a structured approach to testing LLM prompts with configurable test suites, multiple evaluation strategies (exact match, substring containment, custom functions), and A/B testing for comparing prompt variants. The module tracks pass rates, scores, and latency across test runs, enabling data-driven prompt engineering with reproducible results and variant comparison reports.


## Installation

```bash
pip install codomyrmex
```

## Key Features

- **Test Suite Management**: Organize test cases into named suites with descriptions for structured prompt evaluation
- **Multiple Evaluation Strategies**: Built-in evaluators for exact match (case-sensitive/insensitive) and substring containment (contains/not-contains)
- **Custom Evaluators**: Register custom evaluation functions for domain-specific scoring logic
- **A/B Testing**: Compare multiple prompt variants against the same test suite with automatic winner determination
- **Latency Tracking**: Measure and report execution latency for each test case in milliseconds
- **Pass Rate and Scoring**: Configurable pass threshold with aggregate statistics (pass rate, average score, average latency)
- **Test Result Analytics**: Detailed per-test results with status (PENDING, RUNNING, PASSED, FAILED, ERROR) and error reporting
- **Variant Comparison Reports**: Generate side-by-side comparison reports across prompt variants with multiple metrics


## Key Components

| Component | Description |
|-----------|-------------|
| `PromptTester` | Main testing engine that runs test suites against an executor function with configurable pass threshold |
| `PromptTestSuite` | Collection of test cases organized into a named suite with description |
| `PromptTestCase` | Individual test case with prompt, expected output, evaluation type, contains/not-contains lists, and weight |
| `ABTest` | A/B testing framework for comparing multiple prompt variants and determining winners by metric |
| `TestResult` | Result of a single test case execution with status, score, latency, and error details |
| `TestSuiteResult` | Aggregate result of a complete test suite run with pass rate, average score, and average latency |
| `Evaluator` | Abstract base class for implementing output evaluation strategies |
| `ExactMatchEvaluator` | Evaluator that scores 1.0 for exact matches and 0.0 otherwise (configurable case sensitivity) |
| `ContainsEvaluator` | Evaluator that checks substring containment and absence conditions, returning fractional scores |
| `CustomEvaluator` | Evaluator wrapping a user-provided scoring function |
| `EvaluationType` | Enum of evaluation types: EXACT_MATCH, CONTAINS, NOT_CONTAINS, SEMANTIC, CUSTOM |
| `TestStatus` | Enum of test statuses: PENDING, RUNNING, PASSED, FAILED, ERROR |

## Quick Start

```python
from codomyrmex.prompt_testing import (
    PromptTester, PromptTestSuite, PromptTestCase, EvaluationType
)

# Define a test suite
suite = PromptTestSuite("greeting_tests", description="Verify greeting behavior")

suite.add_test(PromptTestCase(
    id="hello_test",
    prompt="Say hello to the user",
    expected_contains=["hello", "hi"],
    evaluation_type=EvaluationType.CONTAINS,
))

suite.add_test(PromptTestCase(
    id="no_profanity",
    prompt="Respond to an angry user",
    expected_not_contains=["stupid", "idiot"],
    evaluation_type=EvaluationType.CONTAINS,
))

# Define an executor (calls your LLM)
def executor(prompt: str) -> str:
    # Replace with actual LLM call
    return "Hello! How can I help you today?"

# Run tests
tester = PromptTester(pass_threshold=0.5)
results = tester.run(suite, executor, prompt_version="v1.0")

print(f"Pass rate: {results.pass_rate:.1%}")
print(f"Average score: {results.average_score:.2f}")
print(f"Average latency: {results.average_latency_ms:.1f}ms")
```

```python
from codomyrmex.prompt_testing import ABTest, PromptTestSuite, PromptTestCase

# Set up A/B test for prompt variants
ab_test = ABTest("system_prompt_test")
ab_test.add_variant("concise", "Be brief and direct. Answer: {prompt}")
ab_test.add_variant("detailed", "Provide a thorough explanation. Answer: {prompt}")

# Define test suite
suite = PromptTestSuite("quality_checks")
suite.add_test(PromptTestCase(
    id="accuracy",
    prompt="What is 2+2?",
    expected_contains=["4"],
))

# Run A/B test (executor_factory creates an executor for each variant)
def executor_factory(template: str):
    def executor(prompt: str) -> str:
        # Replace with actual LLM call using the template
        return "The answer is 4."
    return executor

results = ab_test.run(suite, executor_factory)

# Determine winner
winner = ab_test.get_winner(metric="pass_rate")
print(f"Winner: {winner}")

# Get comparison report
report = ab_test.compare()
for variant, stats in report.items():
    print(f"{variant}: pass_rate={stats['pass_rate']:.1%}, avg_score={stats['average_score']:.2f}")
```

## Related Modules

- [model_ops](../model_ops/) - Model evaluation metrics that complement prompt testing
- [multimodal](../multimodal/) - Build multimodal prompts for testing vision/audio models
- [llm](../llm/) - LLM infrastructure providing the executors for prompt testing

## Navigation

- **Source**: [src/codomyrmex/prompt_testing/](../../../src/codomyrmex/prompt_testing/)
- **Parent**: [docs/modules/](../README.md)
