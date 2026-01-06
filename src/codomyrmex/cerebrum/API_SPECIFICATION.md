# CEREBRUM - API Specification

**Version**: v0.1.0 | **Last Updated**: January 2026

## Overview

This document provides a complete API reference for the CEREBRUM module, including all classes, methods, and data structures.

## Core Classes

### CerebrumEngine

Main orchestrator for case-based reasoning and Bayesian inference.

#### Methods

##### `__init__(config: Optional[CerebrumConfig] = None) -> None`

Initialize CEREBRUM engine.

**Parameters:**
- `config` (Optional[CerebrumConfig]): Configuration object

**Returns:** None

##### `create_model(name: str, model_type: str, config: Optional[dict[str, Any]] = None) -> Model`

Create a new cognitive model.

**Parameters:**
- `name` (str): Model name (must be unique)
- `model_type` (str): Type of model (e.g., "case_based", "bayesian")
- `config` (Optional[dict[str, Any]]): Model configuration parameters

**Returns:** `Model` - Created model

**Raises:**
- `ModelError`: If model already exists

##### `add_case(case: Case) -> None`

Add a case to the case base.

**Parameters:**
- `case` (Case): Case to add

**Returns:** None

**Raises:**
- `InvalidCaseError`: If case is invalid

##### `reason(case: Case, context: Optional[dict[str, Any]] = None) -> ReasoningResult`

Perform reasoning on a case.

**Parameters:**
- `case` (Case): Query case
- `context` (Optional[dict[str, Any]]): Additional context

**Returns:** `ReasoningResult` - Reasoning result with prediction and confidence

##### `learn_from_case(case: Case, outcome: Any) -> None`

Learn from a case by updating the case base.

**Parameters:**
- `case` (Case): Case to learn from
- `outcome` (Any): Observed outcome

**Returns:** None

##### `transform_model(model: Model, transformation: str, **kwargs) -> Model`

Transform a model through adaptation or learning.

**Parameters:**
- `model` (Model): Model to transform
- `transformation` (str): Transformation type ("adapt_to_case", "learn_from_feedback", etc.)
- `**kwargs`: Transformation-specific parameters

**Returns:** `Model` - Transformed model

**Raises:**
- `TransformationError`: If transformation fails

##### `set_bayesian_network(network: BayesianNetwork) -> None`

Set Bayesian network for probabilistic inference.

**Parameters:**
- `network` (BayesianNetwork): Bayesian network

**Returns:** None

##### `set_active_inference_agent(agent: ActiveInferenceAgent) -> None`

Set active inference agent.

**Parameters:**
- `agent` (ActiveInferenceAgent): Active inference agent

**Returns:** None

## Case Management

### Case

Represents a case in case-based reasoning.

#### Attributes

- `case_id` (str): Unique case identifier
- `features` (dict[str, Any]): Feature dictionary
- `context` (dict[str, Any]): Additional context
- `outcome` (Optional[Any]): Outcome or solution
- `metadata` (dict[str, Any]): Additional metadata

#### Methods

##### `to_dict() -> dict[str, Any]`

Convert case to dictionary.

**Returns:** `dict[str, Any]` - Case as dictionary

##### `from_dict(data: dict[str, Any]) -> Case`

Create case from dictionary.

**Parameters:**
- `data` (dict[str, Any]): Case data

**Returns:** `Case` - Case object

### CaseBase

Collection of cases with similarity search.

#### Methods

##### `add_case(case: Case) -> None`

Add a case to the case base.

**Parameters:**
- `case` (Case): Case to add

**Returns:** None

##### `retrieve_similar(query: Case, k: int = 10, threshold: float = 0.0) -> list[tuple[Case, float]]`

Retrieve k most similar cases.

**Parameters:**
- `query` (Case): Query case
- `k` (int): Number of cases to retrieve
- `threshold` (float): Minimum similarity threshold

**Returns:** `list[tuple[Case, float]]` - List of (case, similarity) tuples

##### `compute_similarity(case1: Case, case2: Case) -> float`

Compute similarity between two cases.

**Parameters:**
- `case1` (Case): First case
- `case2` (Case): Second case

**Returns:** `float` - Similarity score in [0, 1]

### CaseRetriever

Retrieves similar cases using various strategies.

#### Methods

##### `retrieve(query: Case, k: int = 10, threshold: float = 0.0) -> list[tuple[Case, float]]`

Retrieve similar cases.

**Parameters:**
- `query` (Case): Query case
- `k` (int): Number of cases to retrieve
- `threshold` (float): Minimum similarity threshold

**Returns:** `list[tuple[Case, float]]` - List of (case, weight) tuples

## Bayesian Inference

### BayesianNetwork

Represents a Bayesian network (probabilistic graphical model).

#### Methods

##### `add_node(node: str, values: list[Any], prior: Optional[list[float]] = None) -> None`

Add a node to the network.

**Parameters:**
- `node` (str): Node name
- `values` (list[Any]): Possible values
- `prior` (Optional[list[float]]): Prior probabilities

**Returns:** None

**Raises:**
- `NetworkStructureError`: If node already exists

##### `add_edge(parent: str, child: str) -> None`

Add a directed edge.

**Parameters:**
- `parent` (str): Parent node name
- `child` (str): Child node name

**Returns:** None

**Raises:**
- `NetworkStructureError`: If nodes don't exist

##### `set_cpt(node: str, cpt: dict[tuple, dict[Any, float]]) -> None`

Set conditional probability table.

**Parameters:**
- `node` (str): Node name
- `cpt` (dict[tuple, dict[Any, float]]): Conditional probability table

**Returns:** None

### InferenceEngine

Performs probabilistic inference.

#### Methods

##### `infer(query: dict[str, Any], evidence: Optional[dict[str, Any]] = None) -> dict[str, Distribution]`

Perform inference.

**Parameters:**
- `query` (dict[str, Any]): Variables to query
- `evidence` (Optional[dict[str, Any]]): Observed evidence

**Returns:** `dict[str, Distribution]` - Posterior distributions

**Raises:**
- `InferenceError`: If inference fails

##### `compute_marginal(variable: str, evidence: Optional[dict[str, Any]] = None) -> Distribution`

Compute marginal distribution.

**Parameters:**
- `variable` (str): Variable name
- `evidence` (Optional[dict[str, Any]]): Optional evidence

**Returns:** `Distribution` - Marginal distribution

### Distribution

Represents a probability distribution.

#### Attributes

- `values` (list[Any]): Possible values
- `probabilities` (list[float]): Probabilities (normalized)

#### Methods

##### `sample(n: int = 1) -> list[Any]`

Sample from the distribution.

**Parameters:**
- `n` (int): Number of samples

**Returns:** `list[Any]` - Samples

##### `expectation() -> float`

Compute expectation (for numeric values).

**Returns:** `float` - Expected value

**Raises:**
- `ValueError`: If values are not numeric

##### `mode() -> Any`

Get the most probable value.

**Returns:** `Any` - Mode value

## Active Inference

### ActiveInferenceAgent

Implements active inference agent.

#### Methods

##### `predict(observation: Optional[dict[str, Any]] = None) -> dict[str, float]`

Predict state distribution.

**Parameters:**
- `observation` (Optional[dict[str, Any]]): Optional observation

**Returns:** `dict[str, float]` - Predicted state distribution

##### `select_action(state: Optional[dict[str, Any]] = None) -> str`

Select action based on expected free energy.

**Parameters:**
- `state` (Optional[dict[str, Any]]): Optional current state

**Returns:** `str` - Selected action

##### `update_beliefs(observation: dict[str, Any]) -> None`

Update beliefs based on observation.

**Parameters:**
- `observation` (dict[str, Any]): New observation

**Returns:** None

##### `compute_free_energy(beliefs: Optional[BeliefState] = None, observations: Optional[dict[str, Any]] = None) -> float`

Compute variational free energy.

**Parameters:**
- `beliefs` (Optional[BeliefState]): Belief state
- `observations` (Optional[dict[str, Any]]): Observations

**Returns:** `float` - Free energy value

## Model Transformation

### TransformationManager

Manages model transformations.

#### Methods

##### `transform(model: Model, transformation_type: str, transformer_name: Optional[str] = None, **kwargs) -> Model`

Transform a model.

**Parameters:**
- `model` (Model): Model to transform
- `transformation_type` (str): Type of transformation
- `transformer_name` (Optional[str]): Specific transformer
- `**kwargs`: Transformation parameters

**Returns:** `Model` - Transformed model

## Visualization

### ModelVisualizer

Visualizes Bayesian networks.

#### Methods

##### `visualize_network(network: BayesianNetwork) -> Figure`

Visualize Bayesian network structure.

**Parameters:**
- `network` (BayesianNetwork): Network to visualize

**Returns:** `Figure` - Matplotlib figure

### CaseVisualizer

Visualizes case similarity.

#### Methods

##### `plot_case_similarity(cases: list[tuple[Case, float]], query_case: Optional[Case] = None) -> Figure`

Plot case similarity scores.

**Parameters:**
- `cases` (list[tuple[Case, float]]): Cases with similarities
- `query_case` (Optional[Case]): Optional query case

**Returns:** `Figure` - Matplotlib figure

## Configuration

### CerebrumConfig

Configuration for CEREBRUM engine.

#### Attributes

- `case_similarity_threshold` (float): Minimum similarity threshold
- `max_retrieved_cases` (int): Maximum cases to retrieve
- `case_weighting_strategy` (str): Weighting strategy
- `inference_method` (str): Inference method
- `adaptation_rate` (float): Model adaptation rate
- `learning_rate` (float): Learning rate

## Exceptions

- `CerebrumError`: Base exception
- `CaseError`: Case-related errors
- `CaseNotFoundError`: Case not found
- `InvalidCaseError`: Invalid case
- `BayesianInferenceError`: Bayesian inference errors
- `InferenceError`: Inference failures
- `NetworkStructureError`: Network structure errors
- `ActiveInferenceError`: Active inference errors
- `ModelError`: Model-related errors
- `TransformationError`: Transformation errors
- `VisualizationError`: Visualization errors



## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
