# Cerebrum Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Case-based reasoning and cognitive architecture module. Implements Bayesian inference, active inference, and memory systems for intelligent decision-making.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Case-Based Reasoning**: Learn from past examples
- **Bayesian Networks**: Probabilistic inference
- **Active Inference**: Goal-directed reasoning
- **Memory Systems**: Episodic and semantic memory


## Key Components

| Component | Description |
|-----------|-------------|
| `CerebrumEngine` | Core reasoning engine |
| `CaseBase` | Case storage and retrieval |
| `BayesianNetwork` | Probabilistic inference |
| `ActiveInferenceAgent` | Goal-directed agent |

## Quick Start

```python
from codomyrmex.cerebrum import CerebrumEngine, Case

engine = CerebrumEngine()
result = engine.reason(
    case=Case(problem="Debug API error"),
    context={"language": "python", "framework": "fastapi"}
)
```

## Directory Contents

- [fpf_integration.md](fpf_integration.md) - FPF integration guide
- [tutorials/](tutorials/) - Usage tutorials


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cerebrum -v
```

## Related Modules

- [agents](../agents/) - AI agent framework
- [fpf](../fpf/) - Functional programming framework
- [llm](../llm/) - LLM integration

## Navigation

- **Source**: [src/codomyrmex/cerebrum/](../../../src/codomyrmex/cerebrum/)
- **Parent**: [docs/modules/](../README.md)
