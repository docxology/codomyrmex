# prompt_testing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Systematic prompt evaluation and A/B testing framework. Provides test suites for running prompt test cases against LLM executors, with pluggable evaluators (exact match, substring containment, custom functions) and statistical reporting of pass rates, scores, and latency. Includes full A/B testing support to compare prompt variants and determine winners by configurable metrics.

## Key Exports

### Enums

- **`EvaluationType`** -- Evaluation strategy: EXACT_MATCH, CONTAINS, NOT_CONTAINS, SEMANTIC, CUSTOM
- **`TestStatus`** -- Test run status: PENDING, RUNNING, PASSED, FAILED, ERROR

### Data Classes

- **`PromptTestCase`** -- A single test case with prompt text, expected output, evaluation type, contains/not-contains lists, metadata, and weight
- **`TestResult`** -- Result of one test case execution with status, actual output, score (0-1), latency in milliseconds, and error details
- **`TestSuiteResult`** -- Aggregate result of a suite run with pass rate, average latency, average score, and per-test results

### Evaluators

- **`Evaluator`** -- Abstract base class for output evaluators; subclasses implement `evaluate(test_case, actual_output) -> float`
- **`ExactMatchEvaluator`** -- Scores 1.0 for exact match (optionally case-insensitive), 0.0 otherwise
- **`ContainsEvaluator`** -- Scores based on fraction of expected_contains and expected_not_contains checks that pass
- **`CustomEvaluator`** -- Wraps a user-provided callable for fully custom evaluation logic

### Core

- **`PromptTestSuite`** -- Collection of PromptTestCase instances identified by suite_id; supports add/get operations
- **`PromptTester`** -- Main testing engine that runs a suite against an executor function, applies evaluators, and returns TestSuiteResult with configurable pass threshold
- **`ABTest`** -- A/B testing harness for comparing prompt variants; runs each variant through the same test suite, selects winner by pass_rate, average_score, or average_latency_ms

## Directory Contents

- `__init__.py` - Module definition with all test framework classes and evaluators
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Detailed API documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/prompt_testing/](../../../docs/modules/prompt_testing/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
