# FPF Reasoning -- Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

First-principles reasoning engine providing structured problem decomposition and analysis strategies. Agents use this module to break problems into sub-components, identify assumptions, find analogies, and test hypotheses through contradiction.

## Key Components

| Export | Type | Role |
|--------|------|------|
| `ReasoningStep` | Enum | Step types: `QUESTION`, `ASSUMPTION`, `FACT`, `INFERENCE`, `CONCLUSION`, `HYPOTHESIS` |
| `Premise` | Dataclass | Reasoning unit with `id`, `content`, `step_type`, `confidence` (0-1), `source`, `depends_on` |
| `ReasoningChain` | Dataclass | Ordered sequence of `Premise` objects with `goal`, `conclusion`, validation, and confidence calculation |
| `ReasoningStrategy` | ABC | Abstract strategy -- subclasses implement `apply(problem) -> ReasoningChain` |
| `DecompositionStrategy` | Strategy | Breaks problem into fundamental components |
| `AssumptionAnalysisStrategy` | Strategy | Generates questions to identify and challenge assumptions |
| `AnalogicalReasoningStrategy` | Strategy | Finds structural similarities to solved problems |
| `ContradictionStrategy` | Strategy | Tests hypotheses by assuming the opposite and seeking contradictions |
| `ProblemSpace` | Dataclass | Problem definition container with `constraints`, `objectives`, `known_facts`, `assumptions` |
| `FirstPrinciplesReasoner` | Class | Orchestrator with strategy registry -- `reason()`, `decompose()`, `identify_assumptions()`, `apply_all_strategies()` |
| `create_reasoner` | Factory | Returns a `FirstPrinciplesReasoner` with all four default strategies registered |

## Agent Operating Contract

1. **Quick start** -- Call `create_reasoner()` to get a `FirstPrinciplesReasoner` pre-loaded with all four strategies. Then call `reasoner.reason(problem, strategy_name)` to get a `ReasoningChain`.
2. **Decomposition** -- `reasoner.decompose(problem)` splits a problem string on sentence boundaries (`.`, `;`, `\n`) and conjunctions (`and`, `or`, `but`) for segments longer than 10 words. Returns `list[str]`.
3. **Assumption detection** -- `reasoner.identify_assumptions(statement)` scans for indicator words (`always`, `never`, `must`, `obviously`, `everyone`, etc.) and returns assumption descriptions.
4. **Multi-strategy analysis** -- `reasoner.apply_all_strategies(problem)` runs all registered strategies and returns `list[ReasoningChain]`. Each chain can be serialized via `to_dict()`.
5. **Custom strategies** -- Subclass `ReasoningStrategy`, implement `apply(problem) -> ReasoningChain`, and register via `reasoner.add_strategy(name, strategy)`.
6. **Chain validation** -- `ReasoningChain.validate()` checks for dangling dependency references and conclusions without inference steps. Returns `list[str]` of error messages.
7. **Confidence** -- `ReasoningChain.calculate_confidence()` returns the product of all premise confidences. A single low-confidence premise pulls down the entire chain.

## Data Flow

```
problem (str) --> FirstPrinciplesReasoner.reason(problem, strategy)
                    --> ReasoningStrategy.apply(problem)
                        --> ReasoningChain (with Premise objects)
                            --> validate(), calculate_confidence(), to_dict()
```

## Dependencies

- **Internal**: None (self-contained module)
- **External**: `json`, `abc`, `dataclasses`, `enum`, `collections.abc`

## Testing Guidance

- Call `create_reasoner()` and verify all four strategies are registered in `reasoner.strategies`.
- Test `decompose()` with multi-sentence input and verify output list has more elements than a single-sentence input.
- Test `identify_assumptions()` with statements containing `always` and `never` -- verify at least one assumption is returned per indicator.
- Test `ReasoningChain.validate()` with a premise that `depends_on` a non-existent ID -- verify error is returned.
- Test `calculate_confidence()` -- product of [0.8, 0.5] should be 0.4.
- No mocks -- all classes are pure data/logic with no external dependencies.

## Navigation

- **Parent**: [fpf/](../README.md)
- **Sibling**: [analysis/](../analysis/AGENTS.md)
- **Project root**: [../../../../README.md](../../../../README.md)
