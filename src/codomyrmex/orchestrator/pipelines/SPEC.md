# Technical Specification - Pipelines

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.orchestrator.pipelines`  
**Last Updated**: 2026-01-29

## 1. Purpose

Multi-step pipeline definitions with DAG support

## 2. Architecture

### 2.1 Components

```
pipelines/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `orchestrator`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.orchestrator.pipelines
from codomyrmex.orchestrator.pipelines import (
    StageStatus,             # Enum: PENDING, RUNNING, SUCCESS, FAILED, SKIPPED, CANCELLED
    PipelineStatus,          # Enum: CREATED, RUNNING, SUCCESS, FAILED, CANCELLED
    StageResult,             # Dataclass: stage execution result with timing
    PipelineResult,          # Dataclass: pipeline execution result with stage list
    Stage,                   # ABC: base class for pipeline stages
    FunctionStage,           # Stage wrapping a callable
    ConditionalStage,        # Stage that executes based on a condition
    ParallelStage,           # Stage that runs sub-stages in parallel threads
    Pipeline,                # Core pipeline with DAG-ordered stage execution
    PipelineBuilder,         # Fluent builder for constructing pipelines
)

# Key class signatures:
class Stage(ABC):
    def __init__(self, stage_id: str, name: str | None = None,
                 depends_on: list[str] | None = None,
                 retry_count: int = 0, timeout_s: float | None = None): ...
    def execute(self, context: dict[str, Any]) -> Any: ...        # abstract
    def on_success(self, result: StageResult, context: dict[str, Any]) -> None: ...
    def on_failure(self, result: StageResult, context: dict[str, Any]) -> None: ...

class Pipeline:
    def __init__(self, pipeline_id: str | None = None,
                 name: str | None = None, fail_fast: bool = True): ...
    def add_stage(self, stage: Stage) -> Pipeline: ...
    def set_context(self, key: str, value: Any) -> Pipeline: ...
    def run(self, initial_context: dict[str, Any] | None = None) -> PipelineResult: ...

class PipelineBuilder:
    def __init__(self, name: str): ...
    def stage(self, stage_id: str, func: Callable, depends_on: list[str] | None = None,
              retry_count: int = 0) -> PipelineBuilder: ...
    def parallel(self, stage_id: str, stages: list[Stage],
                 depends_on: list[str] | None = None) -> PipelineBuilder: ...
    def context(self, key: str, value: Any) -> PipelineBuilder: ...
    def build(self) -> Pipeline: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **DAG-based execution order**: Stages declare dependencies via `depends_on` and are topologically sorted at runtime, enabling flexible directed acyclic graph workflows.
2. **Fail-fast with optional override**: The `fail_fast` flag (default `True`) stops pipeline execution on the first stage failure; setting it to `False` allows best-effort completion of independent stages.
3. **Retry with exponential backoff**: Each stage supports configurable `retry_count` with `0.1 * 2^attempt` second backoff, avoiding thundering herd on transient failures.
4. **Thread-based parallelism**: `ParallelStage` uses `concurrent.futures.ThreadPoolExecutor` with configurable `max_workers`, suitable for I/O-bound stage workloads.

### 4.2 Limitations

- No async/await support; all execution is synchronous or thread-based
- `timeout_s` is declared on `Stage` but not enforced by the pipeline executor
- No built-in stage persistence or checkpoint/resume after failure

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/orchestrator/pipelines/
```

## 6. Future Considerations

- Enforce per-stage `timeout_s` via `concurrent.futures` deadline
- Add async pipeline executor for coroutine-based stages
- Checkpoint/resume support for long-running pipelines
