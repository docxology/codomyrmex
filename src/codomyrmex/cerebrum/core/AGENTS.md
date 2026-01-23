# Codomyrmex Agents - src/codomyrmex/cerebrum/core

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Core reasoning engine module for the CEREBRUM cognitive framework. Implements case-based reasoning with Bayesian inference integration, model management, and case transformation capabilities. This module provides the foundational reasoning infrastructure that orchestrates case storage, retrieval, similarity computation, and hybrid reasoning combining case-based and probabilistic approaches.

## Active Components

- `core.py` - Main CEREBRUM engine orchestration (CerebrumEngine, ReasoningEngine, ModelManager)
- `cases.py` - Case management for case-based reasoning (Case, CaseBase, CaseRetriever)
- `models.py` - Model base classes and result structures (Model, ModelBase, ReasoningResult)
- `config.py` - Configuration management for CEREBRUM engine
- `transformations.py` - Model transformation utilities (AdaptationTransformer, LearningTransformer, TransformationManager)
- `exceptions.py` - Exception classes for error handling (CerebrumError, ModelError, CaseNotFoundError, InvalidCaseError)
- `utils.py` - Utility functions (compute_cosine_similarity, compute_euclidean_distance, normalize_features, softmax)

## Key Classes

### CerebrumEngine (core.py)
Main orchestration engine that integrates all CEREBRUM components:
- Manages CaseBase for storing and retrieving cases
- Coordinates ModelManager for cognitive model lifecycle
- Integrates optional BayesianNetwork for probabilistic inference
- Supports ActiveInferenceAgent for free energy principle-based reasoning
- Provides unified `reason()` interface for hybrid reasoning

### Case (cases.py)
Dataclass representing a case in case-based reasoning:
- `case_id`: Unique identifier
- `features`: Dictionary of problem description features
- `context`: Additional contextual information
- `outcome`: Solution or result (optional)
- `metadata`: Additional case metadata

### CaseBase (cases.py)
Collection of cases with similarity search capabilities:
- Supports euclidean and cosine similarity metrics
- Provides `retrieve_similar()` for k-nearest neighbor retrieval
- Handles case CRUD operations (add, get, remove, update)
- Serializable to/from dictionary format

### CaseRetriever (cases.py)
Retrieves similar cases using configurable weighting strategies:
- `distance`: Weight by similarity score directly
- `frequency`: Weight by case usage frequency
- `hybrid`: Combined distance and frequency weighting

### ReasoningEngine (core.py)
Combines case retrieval with probabilistic inference:
- Retrieves similar cases based on query
- Computes weighted predictions from case outcomes
- Integrates Bayesian inference when network is available
- Returns comprehensive ReasoningResult with predictions and confidence

### ModelManager (core.py)
Manages multiple cognitive models:
- Creates, retrieves, and removes named models
- Provides model listing and lifecycle management

### Model (models.py)
Base dataclass for cognitive models:
- `name`: Model identifier
- `model_type`: Type classification
- `parameters`: Model configuration parameters
- `metadata`: Additional model metadata

### ReasoningResult (models.py)
Dataclass containing reasoning operation results:
- `prediction`: Predicted outcome
- `confidence`: Confidence score [0, 1]
- `evidence`: Supporting evidence
- `retrieved_cases`: List of similar cases used
- `inference_results`: Bayesian inference results (if applicable)
- `metadata`: Additional result metadata

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- Cases must have non-empty case_id and at least one feature
- Similarity scores are normalized to [0, 1] range (higher = more similar)
- ReasoningEngine lazily initializes when first reason() call is made
- BayesianNetwork and ActiveInferenceAgent are optional integrations
- All components support serialization to/from dictionary format
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Inference Module**: `../inference/` - BayesianNetwork, InferenceEngine, ActiveInferenceAgent implementations
- **Visualization Module**: `../visualization/` - ModelVisualizer, CaseVisualizer for rendering
- **FPF Integration**: `../fpf/` - CEREBRUM-FPF orchestration and combinatorics analysis
- **Parent Directory**: [cerebrum](../README.md) - CEREBRUM framework documentation
- **Project Root**: ../../../../README.md - Main project documentation
