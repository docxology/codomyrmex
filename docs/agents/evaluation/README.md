# Agent Evaluation

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.evaluation` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Quality evaluation and benchmarking infrastructure. Provides metrics collection, response quality scoring, and comparative agent benchmarks.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `AgentBenchmark` | Runs `TestCase`s against one or more agents and compares the results |
| `TestCase` / `BenchmarkResult` / `EvalResult` | Test definitions and per-case / aggregate results |
| `ExactMatchScorer`, `ContainsScorer`, `LengthScorer`, `CompositeScorer` | Response quality scorers (subclasses of `Scorer`) |

## Usage

```python
from codomyrmex.agents.evaluation import AgentBenchmark, TestCase

benchmark = AgentBenchmark()
benchmark.add_test_case(
    TestCase(id="greeting", prompt="Say hello", expected_contains=["hello"])
)

# Any object works as an "agent"; the executor maps (agent, prompt) -> output text.
results = benchmark.run(
    agents={"echo": str.upper}, executor=lambda agent, prompt: agent(prompt)
)
print(benchmark.compare(results))
```

## Source Module

Source: [`src/codomyrmex/agents/evaluation/`](../../../src/codomyrmex/agents/evaluation/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/evaluation/](../../../src/codomyrmex/agents/evaluation/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
