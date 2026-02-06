# Agent Guidelines - Cerebrum

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
