# theory

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Theoretical foundations for agentic systems including agent architectures, reasoning models, and theoretical frameworks. Provides theoretical basis for understanding and designing agentic systems.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `agent_architectures.py` – File
- `reasoning_models.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

This module provides theoretical foundations for understanding agentic systems:

```python
from codomyrmex.agents.theory import (
    AgentArchitecture,
    ReasoningModel,
)

# Explore agent architectures
architectures = AgentArchitecture.list_architectures()
for arch in architectures:
    print(f"Architecture: {arch.name} - {arch.description}")

# Understand reasoning models
reasoning_models = ReasoningModel.list_models()
for model in reasoning_models:
    print(f"Model: {model.name} - {model.approach}")
```

