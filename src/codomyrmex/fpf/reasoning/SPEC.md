# FPF Reasoning -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview

First-principles reasoning engine implementing the Strategy pattern for structured problem analysis. Provides four built-in reasoning strategies, a composable chain-of-reasoning data model, and an orchestrator that maintains reasoning history.

## 2. Data Types

### ReasoningStep (Enum)

| Value | Meaning |
|-------|---------|
| `QUESTION` | An open question to investigate |
| `ASSUMPTION` | A stated assumption that may need validation |
| `FACT` | An established fact with high confidence |
| `INFERENCE` | A logical deduction from other premises |
| `CONCLUSION` | A final conclusion drawn from the chain |
| `HYPOTHESIS` | A testable hypothesis |

### Premise (Dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | -- | Auto-assigned as `p{N}` by `ReasoningChain.add_premise()` |
| `content` | `str` | -- | The premise statement |
| `step_type` | `ReasoningStep` | -- | Classification of this premise |
| `confidence` | `float` | `1.0` | Confidence in [0.0, 1.0] |
| `source` | `str | None` | `None` | Provenance reference |
| `depends_on` | `list[str]` | `[]` | IDs of prerequisite premises |

### ReasoningChain (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Chain identifier (set by strategy) |
| `goal` | `str` | What this chain aims to solve |
| `premises` | `list[Premise]` | Ordered list of reasoning steps |
| `conclusion` | `str | None` | Final conclusion text |
| `metadata` | `dict` | Arbitrary metadata |

| Method | Returns | Behavior |
|--------|---------|----------|
| `add_premise(content, step_type, **kwargs)` | `Premise` | Appends premise with auto-generated ID |
| `get_assumptions()` | `list[Premise]` | Filters premises where `step_type == ASSUMPTION` |
| `get_facts()` | `list[Premise]` | Filters premises where `step_type == FACT` |
| `validate()` | `list[str]` | Checks: (1) all `depends_on` IDs exist, (2) conclusion requires at least one INFERENCE |
| `calculate_confidence()` | `float` | Product of all premise confidences; returns 0.0 if no premises |
| `to_dict()` | `dict` | Serializable dict including computed confidence |

### ProblemSpace (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `problem` | `str` | Problem statement |
| `constraints` | `list[str]` | Hard constraints |
| `objectives` | `list[str]` | Goals to achieve |
| `known_facts` | `list[str]` | Established facts |
| `assumptions` | `list[str]` | Active assumptions |

## 3. Strategy Pattern

### ReasoningStrategy (ABC)

Abstract method: `apply(problem: str) -> ReasoningChain`

### Built-in Strategies

| Strategy | Chain ID | Premises Generated |
|----------|----------|--------------------|
| `DecompositionStrategy(max_depth, min_component_size)` | `"decomposition"` | 1 QUESTION (component identification) + 1 HYPOTHESIS (sub-problem independence, confidence 0.8) |
| `AssumptionAnalysisStrategy` | `"assumption_analysis"` | 3 QUESTION premises (what assumptions, are they necessary, what if different) |
| `AnalogicalReasoningStrategy` | `"analogical"` | 3 QUESTION premises (structure, precedents, transferability) |
| `ContradictionStrategy` | `"contradiction"` | 1 ASSUMPTION (opposite hypothesis, confidence 0.5) + 2 QUESTION premises (consequences, contradictions) |

## 4. FirstPrinciplesReasoner

Constructor: `FirstPrinciplesReasoner()` -- registers all four built-in strategies.

| Method | Signature | Behavior |
|--------|-----------|----------|
| `add_strategy` | `(name: str, strategy: ReasoningStrategy)` | Registers custom strategy |
| `reason` | `(problem: str, strategy_name: str = "decomposition") -> ReasoningChain` | Applies named strategy, appends to `reasoning_history` |
| `decompose` | `(problem: str) -> list[str]` | Splits on `.`, `;`, `\n`; sub-splits segments >10 words on `and`, `or`, `, but` |
| `identify_assumptions` | `(statement: str) -> list[str]` | Scans for 12 indicator words: `always`, `never`, `must`, `should`, `obviously`, `clearly`, `certainly`, `everyone`, `no one`, `all`, `none` |
| `apply_all_strategies` | `(problem: str) -> list[ReasoningChain]` | Runs every registered strategy sequentially |
| `get_history` | `() -> list[dict]` | Returns `to_dict()` for all chains in `reasoning_history` |

Factory: `create_reasoner() -> FirstPrinciplesReasoner`

## 5. Dependencies

- **Internal**: None
- **External**: `json`, `abc`, `dataclasses`, `enum`, `collections.abc` (all standard library)

## 6. Constraints

- `DecompositionStrategy` produces structural questions, not actual decomposition -- agents must populate answers.
- `decompose()` uses simple string splitting, not semantic analysis.
- `identify_assumptions()` is keyword-based only -- may miss context-dependent assumptions.
- `calculate_confidence()` uses multiplicative aggregation, which strongly penalizes any single low-confidence premise.
- `validate()` only checks structural correctness (dangling references, inference gaps), not logical validity.

## Navigation

- **Parent**: [fpf/](../README.md)
- **Project root**: [../../../../README.md](../../../../README.md)
