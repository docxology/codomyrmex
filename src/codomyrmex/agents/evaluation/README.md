# evaluation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Agent benchmarking, quality metrics, and performance comparison. Provides a generic `AgentBenchmark` harness that runs test cases against one or more agents, scores outputs with pluggable `Scorer` implementations, computes latency percentiles (p50/p95/p99), tracks token usage and cost, then generates a side-by-side comparison report or JSON export.

## Key Exports

- **`MetricType`** -- Enum of evaluation metric categories (latency, accuracy, completeness, coherence, relevance, cost, token_efficiency, custom)
- **`EvalResult`** -- Dataclass capturing the result of a single test case run against an agent (score, latency, tokens, cost, errors)
- **`TestCase`** -- Dataclass defining a test case with prompt, expected output constraints, tag-based grouping, and optional latency cap
- **`BenchmarkResult`** -- Aggregated benchmark results per agent including pass rate, latency percentiles, cost totals, and per-tag breakdowns
- **`Scorer`** -- Abstract base class for scoring agent outputs (0.0 to 1.0)
- **`ExactMatchScorer`** -- Scorer that compares output to expected via exact string match (configurable case sensitivity)
- **`ContainsScorer`** -- Scorer that checks whether output contains the expected text
- **`LengthScorer`** -- Scorer that evaluates output length relative to a target with configurable tolerance
- **`CompositeScorer`** -- Combines multiple scorers with weighted averaging
- **`AgentBenchmark`** -- Generic benchmark harness that runs test cases, collects results, and produces comparison reports
- **`create_basic_test_suite()`** -- Factory returning a pre-built list of test cases covering greeting, math, JSON formatting, safety refusal, and coding

## Directory Contents

- `__init__.py` - All evaluation logic: metric types, scorers, benchmark harness, result aggregation, comparison reporting
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
