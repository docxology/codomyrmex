# Personal AI Infrastructure — Model Ops Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model Operations module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.model_ops import Dataset, DatasetSanitizer, FineTuningJob, vector_store, optimization, registry
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `vector_store` | Function/Constant | Feature store |
| `optimization` | Function/Constant | Optimization |
| `registry` | Function/Constant | Registry |
| `evaluation` | Function/Constant | Evaluation |
| `training` | Function/Constant | Training |
| `Dataset` | Class | Dataset |
| `DatasetSanitizer` | Class | Datasetsanitizer |
| `FineTuningJob` | Class | Finetuningjob |
| `Evaluator` | Class | Evaluator |
| `Scorer` | Class | Scorer |
| `ExactMatchScorer` | Class | Exactmatchscorer |
| `ContainsScorer` | Class | Containsscorer |
| `LengthScorer` | Class | Lengthscorer |
| `RegexScorer` | Class | Regexscorer |

*Plus 29 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Model Ops Contribution |
|-------|------------------------------|
| **THINK** | Analysis and reasoning |
| **BUILD** | Artifact creation and code generation |
| **LEARN** | Learning and knowledge capture |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
