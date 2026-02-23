# agents/theory

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Theoretical foundations for agentic systems. Defines abstract agent architecture types (reactive, deliberative, hybrid) and reasoning model abstractions (symbolic, neural, hybrid) used as base classes throughout the agents module.

## Key Exports

From `agent_architectures`:

- **`AgentArchitecture`** -- Base class for agent architecture definitions
- **`ReactiveArchitecture`** -- Stimulus-response architecture without internal state
- **`DeliberativeArchitecture`** -- Planning-based architecture with world models
- **`HybridArchitecture`** -- Combined reactive and deliberative architecture

From `reasoning_models`:

- **`ReasoningModel`** -- Base class for reasoning model abstractions
- **`SymbolicReasoningModel`** -- Logic and rule-based reasoning
- **`NeuralReasoningModel`** -- Neural network-based reasoning
- **`HybridReasoningModel`** -- Combined symbolic and neural reasoning

## Directory Contents

- `__init__.py` - Package init; re-exports all architecture and reasoning classes
- `agent_architectures.py` - Agent architecture type definitions
- `reasoning_models.py` - Reasoning model type definitions
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
