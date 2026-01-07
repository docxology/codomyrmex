# cerebrum

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [scripts](scripts/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling. Provides case-based reasoning combined with Bayesian probabilistic inference for cognitive modeling, code reasoning, and AI enhancement. Integrates case-based reasoning, Bayesian inference, and active inference based on free energy principle.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `FPF_INTEGRATION_SUMMARY.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `active_inference.py` – File
- `bayesian.py` – File
- `cases.py` – File
- `composition_visualizer.py` – File
- `concordance_visualizer.py` – File
- `config.py` – File
- `core.py` – File
- `docs/` – Subdirectory
- `exceptions.py` – File
- `fpf_combinatorics.py` – File
- `fpf_orchestration.py` – File
- `models.py` – File
- `scripts/` – Subdirectory
- `tests/` – Subdirectory
- `transformations.py` – File
- `utils.py` – File
- `visualization.py` – File
- `visualization_base.py` – File
- `visualization_theme.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.cerebrum import (
    CerebrumEngine,
    Case,
    CaseBase,
    BayesianNetwork,
    InferenceEngine,
)

# Create a cerebrum engine
engine = CerebrumEngine()

# Create and add cases
case = Case(
    features={"complexity": 0.8, "size": 100},
    solution="Use caching",
    outcome="success"
)
case_base = CaseBase()
case_base.add_case(case)

# Create Bayesian network
network = BayesianNetwork()
network.add_node("complexity", prior=0.5)
network.add_node("performance", parents=["complexity"])

# Perform inference
inference = InferenceEngine(network)
result = inference.infer(evidence={"complexity": 0.8})
print(f"Inference result: {result}")

# Use reasoning engine
reasoning = engine.reason(case, context={})
print(f"Reasoning result: {reasoning.confidence}")
```

