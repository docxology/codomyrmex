# Agent Theory

**Module**: `codomyrmex.agents.theory` | **Category**: Specialized | **Last Updated**: March 2026

## Overview

Theoretical foundations for agentic systems. Provides formal agent architecture types (reactive, deliberative, hybrid) and reasoning model types (symbolic, neural, hybrid) as typed classes.

## Key Classes

| Class | Purpose |
|:---|:---|
| `AgentArchitecture` | Base architecture type |
| `ReactiveArchitecture` | Stimulus-response agents |
| `DeliberativeArchitecture` | Planning/reasoning agents |
| `HybridArchitecture` | Combined reactive + deliberative |
| `ReasoningModel` | Base reasoning model type |
| `SymbolicReasoningModel` | Logic/rule-based reasoning |
| `NeuralReasoningModel` | Neural network-based reasoning |
| `HybridReasoningModel` | Combined symbolic + neural |

## Usage

```python
from codomyrmex.agents.theory import AgentArchitecture

client = AgentArchitecture()
```

## Source Module

Source: [`src/codomyrmex/agents/theory/`](../../../../src/codomyrmex/agents/theory/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/theory/](../../../../src/codomyrmex/agents/theory/)
- **Project Root**: [README.md](../../../README.md)
