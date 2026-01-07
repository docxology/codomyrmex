# Codomyrmex Agents — src/codomyrmex/agents/theory

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Theoretical foundations for agentic systems including agent architectures, reasoning models, and theoretical frameworks. Provides theoretical basis for understanding and designing agentic systems.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `agent_architectures.py` – Agent architecture patterns and designs
- `reasoning_models.py` – Reasoning models and frameworks

## Key Classes and Functions

### AgentArchitectures (`agent_architectures.py`)
- `AgentArchitectures()` – Agent architecture patterns and designs
- `get_architecture(architecture_name: str) -> Architecture` – Get architecture pattern

### ReasoningModels (`reasoning_models.py`)
- `ReasoningModels()` – Reasoning models and frameworks
- `get_reasoning_model(model_name: str) -> ReasoningModel` – Get reasoning model

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation