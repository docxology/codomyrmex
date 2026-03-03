# Cerebrum

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

CEREBRUM (Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling) provides case-based reasoning combined with Bayesian probabilistic inference for cognitive modeling, code reasoning, and AI enhancement. It includes a reasoning engine, case management, Bayesian networks, active inference agents, model transformations, visualization tools, and optional FPF (Functional Programming Format) integration.

## Architecture Overview

```
cerebrum/
├── __init__.py              # Public API (40+ exports)
├── core/                    # CerebrumEngine, ModelManager, ReasoningEngine, WorkingMemory
│   ├── case.py              # Case, CaseBase, CaseRetriever
│   ├── model.py             # Model, ModelBase
│   └── transformations.py   # ModelTransformer, AdaptationTransformer, LearningTransformer
├── inference/               # BayesianNetwork, InferenceEngine, ActiveInferenceAgent
│   ├── bayesian.py          # BayesianNetwork, Distribution, PriorBuilder
│   └── active.py            # ActiveInferenceAgent, BeliefState, VariationalFreeEnergy
├── visualization/           # ModelVisualizer, CaseVisualizer, InferenceVisualizer
├── fpf/                     # FPF integration (optional)
└── mcp_tools.py             # MCP tools (query_knowledge_base, add_case_reference)
```

## PAI Integration

### Algorithm Phase Mapping

| Algorithm Phase | Role | Key Operations |
|----------------|------|---------------|
| THINK | Load case-based reasoning context and prior knowledge | `query_knowledge_base` |
| LEARN | Store new case references for future retrieval | `add_case_reference` |

## Key Classes and Functions

**`CerebrumEngine`** -- Main orchestrator for case-based reasoning and Bayesian inference.

**`BayesianNetwork`** -- Probabilistic graphical model for inference.

**`ActiveInferenceAgent`** -- Agent based on the free energy principle.

**`Case`** / **`CaseBase`** / **`CaseRetriever`** -- Case management and retrieval.

**`ReasoningChain`** -- Chain of reasoning steps with execution results.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `query_knowledge_base` | Query the cerebrum knowledge base for relevant cases | `query: str` | Safe |
| `add_case_reference` | Add a new case reference to the knowledge base | `case: dict` | Safe |

## Usage Examples

```python
from codomyrmex.cerebrum import CerebrumEngine, Case

engine = CerebrumEngine()
case = Case(features={"language": "python", "pattern": "singleton"})
engine.add_case(case)
results = engine.retrieve(query_features={"pattern": "singleton"})
```

## Related Modules

- [`agentic_memory`](../agentic_memory/readme.md) -- Memory storage that complements case-based reasoning
- [`agents/core`](../agents/readme.md) -- ThinkingAgent reasoning traces

## Navigation

- **Source**: [src/codomyrmex/cerebrum/](../../../../src/codomyrmex/cerebrum/)
- **Parent**: [All Modules](../README.md)
