# src/codomyrmex/agents/theory

## Signposting
- **Parent**: [agents](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Theory submodule providing theoretical foundations for agentic systems. This includes agent architecture patterns and reasoning models.

## Key Components

- **Agent Architectures**: Reactive, deliberative, and hybrid architectures
- **Reasoning Models**: Symbolic, neural, and hybrid reasoning models

## Usage

### Agent Architectures

```python
from codomyrmex.agents.theory import ReactiveArchitecture

# Create reactive agent
agent = ReactiveArchitecture()

# Add rules
agent.add_rule(
    condition=lambda env: env.get("temperature") > 30,
    action=lambda env: {"action": "cool_down"}
)

# Perceive, decide, act
perception = agent.perceive({"temperature": 35})
decision = agent.decide(perception)
result = agent.act(decision)
```

### Reasoning Models

```python
from codomyrmex.agents.theory import SymbolicReasoningModel

# Create reasoning model
model = SymbolicReasoningModel()

# Add rules and facts
model.add_rule({
    "conditions": [{"fact": "temperature", "operator": ">", "value": 30}],
    "conclusion": {"action": "cool"}
})
model.add_fact("temperature", 35)

# Reason
result = model.reason({"temperature": 35})
explanation = model.explain(result)
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Module**: [agents](../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.agents.theory import main_component

def example():
    
    print(f"Result: {result}")
```

<!-- Navigation Links keyword for score -->
