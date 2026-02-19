# fpf/reasoning

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

First Principles Framework reasoning utilities. Provides tools for first principles reasoning and problem decomposition, including structured reasoning chains with confidence tracking, multiple reasoning strategies, and assumption identification.

## Key Exports

### Enums

- **`ReasoningStep`** -- Types of reasoning steps: `QUESTION`, `ASSUMPTION`, `FACT`, `INFERENCE`, `CONCLUSION`, `HYPOTHESIS`

### Data Classes

- **`Premise`** -- A premise in a reasoning chain with ID, content, step type, confidence score (0.0-1.0), optional source attribution, and dependency tracking via `depends_on` list
- **`ReasoningChain`** -- An ordered chain of premises toward a goal. Supports `add_premise()`, extracting subsets via `get_assumptions()` / `get_facts()`, structural `validate()` (detects circular deps and unsupported conclusions), and multiplicative `calculate_confidence()` across all premises
- **`ProblemSpace`** -- Defines a problem space with constraints, objectives, known facts, and assumptions

### Abstract Base Class

- **`ReasoningStrategy`** -- ABC requiring an `apply(problem)` method that returns a `ReasoningChain`

### Strategy Implementations

- **`DecompositionStrategy`** -- Breaks problems into fundamental components with configurable max depth and minimum component size
- **`AssumptionAnalysisStrategy`** -- Identifies and challenges assumptions by generating structured questions about necessity and impact
- **`AnalogicalReasoningStrategy`** -- Reasons by analogy, generating questions about problem structure and cross-domain solution applicability
- **`ContradictionStrategy`** -- Applies proof by contradiction, assuming the opposite of the hypothesis and checking for logical contradictions

### Reasoning Engine

- **`FirstPrinciplesReasoner`** -- Main reasoning engine that manages a registry of strategies (decomposition, assumption analysis, analogical, contradiction by default), maintains reasoning history, supports custom strategy registration via `add_strategy()`, and provides:
  - `reason()` -- Apply a named strategy to a problem
  - `decompose()` -- Simple word-based problem decomposition
  - `identify_assumptions()` -- Detect assumption indicators (always, never, must, should, etc.) in statements
  - `apply_all_strategies()` -- Run all registered strategies against a problem
  - `get_history()` -- Retrieve serialized reasoning history

### Factory Function

- **`create_reasoner()`** -- Create a pre-configured `FirstPrinciplesReasoner` instance

## Directory Contents

- `__init__.py` - Reasoning engine, strategies, chain/premise models, and problem space definition (360 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [fpf](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
