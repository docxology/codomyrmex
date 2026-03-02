# Agent Guidelines - Cerebrum

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Cognitive architecture for reasoning, planning, and decision-making.

## Key Classes

- **CerebrumEngine** — Core reasoning engine
- **WorkingMemory** — Short-term context
- **ReasoningChain** — Chain-of-thought reasoning
- **DecisionModule** — Decision making

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

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `query_knowledge_base` | Perform semantic retrieval from the CaseBase | Safe |
| `add_case_reference` | Store intelligence context directly into the CaseBase | Safe |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full knowledge CRUD | `query_knowledge_base`, `add_case_reference` | TRUSTED |
| **Architect** | Query-only | `query_knowledge_base` | OBSERVED |
| **QATester** | Retrieval verification | `query_knowledge_base` | OBSERVED |
| **Researcher** | Read-only | `query_knowledge_base` | OBSERVED |

### Engineer Agent
**Access**: Full — both read and write operations on the knowledge base (CaseBase).
**Use Cases**: Adding case references during LEARN phase, storing problem-solution pairs for future retrieval, building up domain knowledge from successful Algorithm runs.

### Architect Agent
**Access**: Query-only — semantic retrieval for design decisions.
**Use Cases**: Querying past architectural decisions, retrieving analogous problems for pattern matching, informing ISC criteria with case-based precedents from the THINK phase.

### QATester Agent
**Access**: Retrieval verification — confirming knowledge retrieval accuracy.
**Use Cases**: Verifying that `add_case_reference` writes are retrievable via `query_knowledge_base`, testing relevance ranking of search results, confirming CaseBase consistency.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
