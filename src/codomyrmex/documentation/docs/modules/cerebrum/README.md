<!-- readme: generated -->

# cerebrum

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/cerebrum/`

## Overview

CEREBRUM Module for Codomyrmex.

Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling.

This module provides case-based reasoning combined with Bayesian probabilistic
inference for cognitive modeling, code reasoning, and AI enhancement.

Integration:
    pass
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called).
- Can integrate with `ai_code_editing` for code reasoning.
- Can integrate with `pattern_matching` for pattern-based case retrieval.
- Uses `data_visualization` for model visualization.

Available classes:
    pass
- CerebrumEngine: Main orchestrator for case-based reasoning and Bayesian inference
- Case, CaseBase, CaseRetriever: Case management and retrieval
- BayesianNetwork, InferenceEngine: Bayesian inference capabilities
- ActiveInferenceAgent: Active inference based on free energy principle
- Model, ReasoningResult: Model and result structures
- TransformationManager: Model transformation and adaptation
- ModelVisualizer, CaseVisualizer: Visualization tools

Available functions:
    pass
- create_cerebrum_engine: Create a new CEREBRUM engine instance
- create_case: Create a case from features
- create_bayesian_network: Create a Bayesian network

## Public Exports

`cerebrum` exports 56 public symbols via `__all__`:

`ActiveInferenceAgent`, `ActiveInferenceError`, `AdaptationTransformer`, `BayesianInferenceError`, `BayesianNetwork`, `BeliefState`, `Case`, `CaseBase`, `CaseError`, `CaseNotFoundError`, `CaseRetriever`, `CaseVisualizer`, `CerebrumConfig`, `CerebrumEngine`, `CerebrumError`, `ChainExecutionResult`, `CompositionVisualizer`, `ConcordanceVisualizer`, `Decision`, `DecisionModule`, `Distribution`, `FreeEnergyLoop`, `HierarchicalPlan`, `HierarchicalPlanner` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../cerebrum/](../../../../cerebrum/)
