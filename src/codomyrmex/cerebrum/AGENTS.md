# Agent Guidelines - Cerebrum

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Cognitive architecture for case-based reasoning, planning, and decision-making. Provides
`CerebrumEngine` for orchestrating multi-step reasoning, `WorkingMemory` for short-term context
storage, and a `CaseBase` knowledge store for storing and retrieving prior problem-solution pairs.
Two MCP tools (`query_knowledge_base`, `add_case_reference`) expose the knowledge lifecycle to
PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `CerebrumEngine`, `WorkingMemory`, `ReasoningChain`, `DecisionModule` |
| `engine.py` | `CerebrumEngine` — core reasoning engine |
| `memory.py` | `WorkingMemory` — short-term context storage |
| `reasoning.py` | `ReasoningChain` — step-by-step chain-of-thought orchestration |
| `decision.py` | `DecisionModule` — multi-criteria decision making |
| `case_base.py` | `CaseBase` — knowledge store for prior problem-solution pairs |
| `mcp_tools.py` | MCP tools: `query_knowledge_base`, `add_case_reference` |

## Key Classes

- **CerebrumEngine** — Core reasoning engine that orchestrates all cognitive components.
- **WorkingMemory** — Short-term context storage for reasoning steps and decisions.
- **ReasoningChain** — Orchestrates step-by-step chain-of-thought reasoning.
- **DecisionModule** — Handles multi-criteria decision making based on weighted attributes.

## Agent Instructions

1. **Context management** — Update working memory as needed
2. **Chain reasoning** — Use step-by-step reasoning
3. **Validate decisions** — Check decision consistency
4. **Track uncertainty** — Maintain confidence scores
5. **Explain reasoning** — Provide rationale

## Common Patterns

```python
from codomyrmex.cerebrum import (
    CerebrumEngine, WorkingMemory, ReasoningChain
)

# Initialize engine
engine = CerebrumEngine()
engine.load_knowledge("domain_knowledge.json")

# Working memory
memory = WorkingMemory()
memory.store("user_goal", "Refactor authentication")
memory.store("constraints", ["maintain compatibility", "add tests"])

# Reasoning chain
chain = ReasoningChain()
chain.add_step("Analyze current implementation")
chain.add_step("Identify refactoring patterns")
chain.add_step("Generate implementation plan")
result = chain.execute(memory)

# Decision making
decision = engine.decide(options, criteria, context)
print(f"Decision: {decision.choice} (confidence: {decision.confidence})")
```

## Testing Patterns

```python
# Verify reasoning
chain = ReasoningChain()
chain.add_step("Analyze")
result = chain.execute(context)
assert result.steps_completed == 1

# Verify working memory
memory = WorkingMemory()
memory.store("key", "value")
assert memory.retrieve("key") == "value"
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `query_knowledge_base` | Perform semantic retrieval from the CaseBase | SAFE |
| `add_case_reference` | Store intelligence context directly into the CaseBase | SAFE |

## Operating Contracts

- `WorkingMemory` is not thread-safe — create one instance per concurrent reasoning task
- `ReasoningChain.execute()` requires all steps to be added before calling
- `query_knowledge_base` is read-only — does not modify the CaseBase
- `add_case_reference` writes persist within the session but may not be durable across restarts
- **DO NOT** call `engine.decide()` without providing a non-empty `options` list

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full knowledge CRUD | `query_knowledge_base`, `add_case_reference` | TRUSTED |
| **Architect** | Query-only | `query_knowledge_base` — architectural decision retrieval | OBSERVED |
| **QATester** | Retrieval verification | `query_knowledge_base` — retrieval accuracy verification | OBSERVED |
| **Researcher** | Read-only | `query_knowledge_base` — knowledge retrieval for research | SAFE |

### Engineer Agent
**Use Cases**: Adding case references during LEARN phase, storing problem-solution pairs, building domain knowledge from successful Algorithm runs.

### Architect Agent
**Use Cases**: Querying past architectural decisions, retrieving analogous problems for pattern matching, informing ISC criteria with case-based precedents during THINK phase.

### QATester Agent
**Use Cases**: Verifying that `add_case_reference` writes are retrievable, testing relevance ranking, confirming CaseBase consistency.

### Researcher Agent
**Use Cases**: Semantic knowledge retrieval for research analysis, querying prior case references.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/cerebrum.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/cerebrum.cursorrules)
