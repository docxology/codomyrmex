# Cerebrum Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling (CEREBRUM). Combines case-based reasoning with Bayesian probabilistic inference for cognitive modeling, code reasoning, and AI enhancement. Provides a full pipeline from case storage and retrieval through Bayesian network inference and active inference agents based on the free energy principle, with visualization tools for models, cases, and inference results.

## Key Exports

### Core Engine

- **`CerebrumEngine`** -- Main orchestrator coordinating case-based reasoning and Bayesian inference pipelines
- **`ModelManager`** -- Manages model lifecycle (creation, storage, retrieval, versioning)
- **`ReasoningEngine`** -- Executes reasoning workflows combining case retrieval with probabilistic inference

### Case Management

- **`Case`** -- Dataclass representing a single case with features, solution, and metadata
- **`CaseBase`** -- Collection of cases supporting storage, retrieval, and similarity-based lookup
- **`CaseRetriever`** -- Retrieves the most relevant cases from a CaseBase given a query

### Bayesian Inference

- **`BayesianNetwork`** -- Directed acyclic graph of probabilistic variables with conditional probability tables
- **`InferenceEngine`** -- Runs inference queries on a BayesianNetwork (exact and approximate methods)
- **`Distribution`** -- Probability distribution representation for network variables
- **`PriorBuilder`** -- Utility for constructing prior distributions from data or domain knowledge

### Active Inference

- **`ActiveInferenceAgent`** -- Agent that selects actions to minimize variational free energy
- **`BeliefState`** -- Represents the agent's current beliefs about the environment
- **`VariationalFreeEnergy`** -- Computes free energy for belief evaluation and action selection
- **`PolicySelector`** -- Selects optimal policies based on expected free energy

### Models and Results

- **`Model` / `ModelBase`** -- Model structures used by the reasoning engine
- **`ReasoningResult`** -- Container for reasoning output including confidence and explanation

### Transformations

- **`ModelTransformer`** -- Base class for model transformation operations
- **`AdaptationTransformer`** -- Adapts models based on new evidence or domain shifts
- **`LearningTransformer`** -- Updates model parameters from training data
- **`TransformationManager`** -- Orchestrates sequences of model transformations

### Visualization

- **`ModelVisualizer`** -- Renders model structures as diagrams
- **`CaseVisualizer`** -- Visualizes case distributions and similarity spaces
- **`InferenceVisualizer`** -- Plots inference results and belief updates

### Configuration and Utilities

- **`CerebrumConfig`** -- Configuration dataclass for engine parameters
- **`compute_hash()`** -- Hash computation for case deduplication
- **`normalize_features()`** -- Feature vector normalization
- **`compute_euclidean_distance()` / `compute_cosine_similarity()`** -- Distance metrics for case similarity
- **`softmax()`** -- Softmax transformation for probability normalization

### Exceptions

- **`CerebrumError`** -- Base exception for all CEREBRUM errors
- **`CaseError` / `CaseNotFoundError` / `InvalidCaseError`** -- Case-related exceptions
- **`BayesianInferenceError` / `InferenceError` / `NetworkStructureError`** -- Inference exceptions
- **`ActiveInferenceError`** -- Active inference agent exceptions
- **`ModelError` / `TransformationError` / `VisualizationError`** -- Model and visualization exceptions

### Optional Integration

- **`FPFOrchestrator`** -- Orchestrates First Principles Framework integration (requires fpf submodule)
- **`FPFCombinatoricsAnalyzer`** -- Combinatorial analysis of FPF patterns (requires fpf submodule)

## Directory Contents

- `core/` -- Engine, case management, model definitions, transformers, configuration, exceptions, and utilities
- `inference/` -- Bayesian network, inference engine, active inference agent, belief states, and priors
- `visualization/` -- Model, case, and inference visualizers
- `fpf/` -- Optional FPF integration (orchestrator and combinatorics analyzer)
- `visualization_base.py` -- Base classes for visualization components
- `visualization_theme.py` -- Theming support for visualization output

## Quick Start

```python
from codomyrmex.cerebrum import BaseNetworkVisualizer, BaseChartVisualizer

# Create a BaseNetworkVisualizer instance
basenetworkvisualizer = BaseNetworkVisualizer()

# Use BaseChartVisualizer for additional functionality
basechartvisualizer = BaseChartVisualizer()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cerebrum -v
```

## Navigation

- **Full Documentation**: [docs/modules/cerebrum/](../../../docs/modules/cerebrum/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
