# Codomyrmex Agents — src/codomyrmex/agents/theory

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Theoretical foundations module providing abstract architectures and reasoning models for agentic systems. This module defines different agent architecture patterns and reasoning approaches that can be used as foundations for concrete agent implementations.

## Active Components

- `agent_architectures.py` - Agent architecture definitions
- `reasoning_models.py` - Reasoning model implementations
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Agent Architectures
- **`AgentArchitecture`** - Base class for agent architectures
  - Defines common interface for all architectures
  - Provides hooks for perception, decision, and action

- **`ReactiveArchitecture`** - Stimulus-response architecture
  - Direct mapping from perceptions to actions
  - No internal state or planning
  - Fast response, limited reasoning

- **`DeliberativeArchitecture`** - Plan-based architecture
  - Maintains world model and goals
  - Plans sequences of actions
  - Supports complex reasoning and lookahead

- **`HybridArchitecture`** - Combined reactive and deliberative
  - Reactive layer for immediate responses
  - Deliberative layer for complex tasks
  - Balances responsiveness and reasoning

### Reasoning Models
- **`ReasoningModel`** - Base class for reasoning approaches
  - Defines interface for inference and deduction
  - Supports different knowledge representations

- **`SymbolicReasoningModel`** - Logic-based reasoning
  - Uses formal logic and rules
  - Supports explanation and traceability
  - Suitable for structured domains

- **`NeuralReasoningModel`** - Neural network-based reasoning
  - Uses learned representations
  - Pattern matching and generalization
  - Suitable for unstructured data

- **`HybridReasoningModel`** - Combined symbolic and neural
  - Neural perception with symbolic reasoning
  - Balances learning and formal inference
  - Supports both structured and unstructured inputs

## Operating Contracts

- Architecture classes define abstract methods for perception-action loops.
- Reasoning models define abstract methods for inference.
- Implementations should override hooks for specific behaviors.
- Hybrid approaches must coordinate between subsystems.
- All architectures support the core agent interface patterns.

## Signposting

- **Simple agents?** Use `ReactiveArchitecture` for stimulus-response.
- **Planning agents?** Use `DeliberativeArchitecture` for goal-directed behavior.
- **Balanced agents?** Use `HybridArchitecture` for best of both.
- **Logic reasoning?** Use `SymbolicReasoningModel`.
- **Learning agents?** Use `NeuralReasoningModel`.
- **Combined approach?** Use `HybridReasoningModel`.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Generic Module**: [generic](../generic/AGENTS.md) - Practical base classes
- **Project Root**: ../../../../README.md - Main project documentation
