# Personal AI Infrastructure — Model Ops Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model Operations module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.model_ops import Dataset, DatasetSanitizer, FineTuningJob, evaluation, training, create_evaluator
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `evaluation` | Function/Constant | Evaluation |
| `training` | Function/Constant | Training |
| `Dataset` | Class | Dataset |
| `DatasetSanitizer` | Class | Datasetsanitizer |
| `FineTuningJob` | Class | Finetuningjob |
| `Evaluator` | Class | Evaluator |
| `TaskType` | Class | Tasktype |
| `EvaluationResult` | Class | Evaluationresult |
| `Metric` | Class | Metric |
| `AccuracyMetric` | Class | Accuracymetric |
| `PrecisionMetric` | Class | Precisionmetric |
| `RecallMetric` | Class | Recallmetric |
| `F1Metric` | Class | F1metric |
| `ConfusionMatrix` | Class | Confusionmatrix |

*Plus 9 additional exports.*


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
