# Technical Specification - Evaluation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.evaluation`  
**Last Updated**: 2026-01-29

## 1. Purpose

Agent benchmarking, quality metrics, and performance comparison

## 2. Architecture

### 2.1 Components

```
evaluation/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `agents`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.agents.evaluation
from codomyrmex.agents.evaluation import (
    MetricType,            # Enum: LATENCY, ACCURACY, COMPLETENESS, COHERENCE, RELEVANCE, COST, TOKEN_EFFICIENCY, CUSTOM
    EvalResult,            # Dataclass: result of a single evaluation run
    TestCase,              # Dataclass: defines a test case with expected outputs and constraints
    BenchmarkResult,       # Dataclass: aggregated benchmark results per agent
    Scorer,                # ABC: base class for custom scoring strategies
    ExactMatchScorer,      # Scorer: exact string match
    ContainsScorer,        # Scorer: substring containment check
    LengthScorer,          # Scorer: output length relative to target
    CompositeScorer,       # Scorer: weighted combination of multiple scorers
    AgentBenchmark,        # Generic benchmark runner with compare() and to_json()
    create_basic_test_suite,  # Factory: returns a list of 5 pre-built TestCases
)

# Key class signatures:
class AgentBenchmark(Generic[T]):
    def __init__(self, scorer: Scorer | None = None, include_cost: bool = True): ...
    def add_test_case(self, test_case: TestCase) -> "AgentBenchmark[T]": ...
    def run(self, agents: dict[str, T], executor: Callable[[T, str], str], ...) -> dict[str, BenchmarkResult]: ...
    def compare(self, results: dict[str, BenchmarkResult]) -> str: ...
    def to_json(self, results: dict[str, BenchmarkResult]) -> str: ...

class Scorer(ABC):
    def score(self, output: str, expected: str | None = None) -> float: ...

class TestCase:
    def check_output(self, output: str) -> tuple[bool, list[str]]: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Strategy pattern for scoring**: `Scorer` ABC allows pluggable scoring strategies; `CompositeScorer` enables weighted multi-metric evaluation without subclassing `AgentBenchmark`.
2. **Generic type parameter**: `AgentBenchmark[T]` is generic over the agent type, so any object can serve as the agent -- the benchmark is decoupled from the agent interface via the `executor` callable.
3. **Tag-based aggregation**: `BenchmarkResult.by_tag` enables per-category analysis (e.g., "safety", "coding", "math") without separate benchmark runs.

### 4.2 Limitations

- Scoring is synchronous; no built-in support for parallel agent execution across test cases
- `create_basic_test_suite` uses broad substring checks that may produce false positives on certain prompts

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/evaluation/
```

## 6. Future Considerations

- Async executor support for parallel agent benchmarking
- LLM-as-judge scorer using a reference model to evaluate output quality
