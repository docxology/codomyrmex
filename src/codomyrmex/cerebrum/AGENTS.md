# Codomyrmex Agents — src/codomyrmex/cerebrum

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [CEREBRUM Agents](AGENTS.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

CEREBRUM module providing case-based reasoning combined with Bayesian probabilistic inference for cognitive modeling, code reasoning, and AI enhancement. This module enables intelligent reasoning by retrieving similar past cases and applying Bayesian inference to make predictions, adapt models, and learn from experience.

The cerebrum module serves as the cognitive modeling layer, supporting both case-based reasoning and probabilistic inference for unified modeling across domains.

## Module Overview

### Key Capabilities
- **Case-Based Reasoning**: Retrieve and reason from similar past cases
- **Bayesian Inference**: Perform probabilistic inference on Bayesian networks
- **Active Inference**: Implement active inference agents based on free energy principle
- **Model Transformation**: Adapt and learn models from new cases and feedback
- **Visualization**: Visualize networks, case similarity, and inference results

### Key Features
- Flexible similarity metrics (Euclidean, cosine)
- Multiple inference methods (variable elimination, MCMC)
- Case weighting strategies (distance, frequency, hybrid)
- Model adaptation and learning
- Integration with other codomyrmex modules

## Function Signatures

### Core Engine Functions

```python
def __init__(self, config: Optional[CerebrumConfig] = None) -> None
```

Initialize CEREBRUM engine.

**Parameters:**
- `config` (Optional[CerebrumConfig]): Configuration object

**Returns:** None

```python
def create_model(self, name: str, model_type: str, config: Optional[dict[str, Any]] = None) -> Model
```

Create a new cognitive model.

**Parameters:**
- `name` (str): Model name
- `model_type` (str): Type of model
- `config` (Optional[dict[str, Any]]): Model configuration

**Returns:** `Model` - Created model

**Raises:**
- `ModelError`: If model already exists or configuration is invalid

```python
def add_case(self, case: Case) -> None
```

Add a case to the case base.

**Parameters:**
- `case` (Case): Case to add

**Returns:** None

**Raises:**
- `InvalidCaseError`: If case is invalid

```python
def reason(self, case: Case, context: Optional[dict[str, Any]] = None) -> ReasoningResult
```

Perform reasoning on a case.

**Parameters:**
- `case` (Case): Query case
- `context` (Optional[dict[str, Any]]): Additional context

**Returns:** `ReasoningResult` - Reasoning result with prediction and confidence

```python
def learn_from_case(self, case: Case, outcome: Any) -> None
```

Learn from a case by updating the case base.

**Parameters:**
- `case` (Case): Case to learn from
- `outcome` (Any): Observed outcome

**Returns:** None

```python
def transform_model(self, model: Model, transformation: str, **kwargs) -> Model
```

Transform a model through adaptation or learning.

**Parameters:**
- `model` (Model): Model to transform
- `transformation` (str): Transformation type
- `**kwargs`: Transformation parameters

**Returns:** `Model` - Transformed model

**Raises:**
- `TransformationError`: If transformation fails

### Case Management Functions

```python
def __init__(self, similarity_metric: str = "euclidean") -> None
```

Initialize case base.

**Parameters:**
- `similarity_metric` (str): Similarity metric ("euclidean", "cosine")

**Returns:** None

```python
def add_case(self, case: Case) -> None
```

Add a case to the case base.

**Parameters:**
- `case` (Case): Case to add

**Returns:** None

```python
def retrieve_similar(self, query: Case, k: int = 10, threshold: float = 0.0) -> list[tuple[Case, float]]
```

Retrieve k most similar cases to the query.

**Parameters:**
- `query` (Case): Query case
- `k` (int): Number of cases to retrieve
- `threshold` (float): Minimum similarity threshold

**Returns:** `list[tuple[Case, float]]` - List of (case, similarity) tuples

```python
def compute_similarity(self, case1: Case, case2: Case) -> float
```

Compute similarity between two cases.

**Parameters:**
- `case1` (Case): First case
- `case2` (Case): Second case

**Returns:** `float` - Similarity score in [0, 1]

### Bayesian Inference Functions

```python
def __init__(self, name: str = "bayesian_network") -> None
```

Initialize Bayesian network.

**Parameters:**
- `name` (str): Network name

**Returns:** None

```python
def add_node(self, node: str, values: list[Any], prior: Optional[list[float]] = None) -> None
```

Add a node to the network.

**Parameters:**
- `node` (str): Node name
- `values` (list[Any]): Possible values for the node
- `prior` (Optional[list[float]]): Prior probabilities

**Returns:** None

**Raises:**
- `NetworkStructureError`: If node already exists or prior is invalid

```python
def add_edge(self, parent: str, child: str) -> None
```

Add a directed edge from parent to child.

**Parameters:**
- `parent` (str): Parent node name
- `child` (str): Child node name

**Returns:** None

**Raises:**
- `NetworkStructureError`: If nodes don't exist or edge already exists

```python
def infer(self, query: dict[str, Any], evidence: Optional[dict[str, Any]] = None) -> dict[str, Distribution]
```

Perform inference to compute posterior distributions.

**Parameters:**
- `query` (dict[str, Any]): Variables to query
- `evidence` (Optional[dict[str, Any]]): Observed evidence

**Returns:** `dict[str, Distribution]` - Posterior distributions

**Raises:**
- `InferenceError`: If inference fails

```python
def compute_marginal(self, variable: str, evidence: Optional[dict[str, Any]] = None) -> Distribution
```

Compute marginal distribution of a variable.

**Parameters:**
- `variable` (str): Variable name
- `evidence` (Optional[dict[str, Any]]): Optional evidence

**Returns:** `Distribution` - Marginal distribution

### Active Inference Functions

```python
def __init__(
    self,
    states: list[str],
    observations: list[str],
    actions: list[str],
    precision: float = 1.0,
    policy_horizon: int = 5,
    exploration_weight: float = 0.1
) -> None
```

Initialize active inference agent.

**Parameters:**
- `states` (list[str]): List of possible states
- `observations` (list[str]): List of possible observations
- `actions` (list[str]): List of possible actions
- `precision` (float): Precision parameter for free energy
- `policy_horizon` (int): Planning horizon
- `exploration_weight` (float): Exploration vs exploitation weight

**Returns:** None

```python
def predict(self, observation: Optional[dict[str, Any]] = None) -> dict[str, float]
```

Predict state distribution given observation.

**Parameters:**
- `observation` (Optional[dict[str, Any]]): Optional observation to condition on

**Returns:** `dict[str, float]` - Predicted state distribution

```python
def select_action(self, state: Optional[dict[str, Any]] = None) -> str
```

Select action based on expected free energy.

**Parameters:**
- `state` (Optional[dict[str, Any]]): Optional current state

**Returns:** `str` - Selected action

```python
def update_beliefs(self, observation: dict[str, Any]) -> None
```

Update beliefs based on new observation.

**Parameters:**
- `observation` (dict[str, Any]): New observation

**Returns:** None

```python
def compute_free_energy(
    self, beliefs: Optional[BeliefState] = None, observations: Optional[dict[str, Any]] = None
) -> float
```

Compute variational free energy.

**Parameters:**
- `beliefs` (Optional[BeliefState]): Belief state
- `observations` (Optional[dict[str, Any]]): Observations

**Returns:** `float` - Free energy value

### Transformation Functions

```python
def transform(
    self, model: Model, transformation_type: str, transformer_name: Optional[str] = None, **kwargs
) -> Model
```

Transform a model.

**Parameters:**
- `model` (Model): Model to transform
- `transformation_type` (str): Type of transformation
- `transformer_name` (Optional[str]): Specific transformer to use
- `**kwargs`: Transformation parameters

**Returns:** `Model` - Transformed model

**Raises:**
- `TransformationError`: If transformation fails

```python
def adapt_to_case(self, model: Model, case: Case) -> Model
```

Adapt model to a new case.

**Parameters:**
- `model` (Model): Model to adapt
- `case` (Case): Case to adapt to

**Returns:** `Model` - Adapted model

```python
def learn_from_feedback(self, model: Model, feedback: dict[str, Any]) -> Model
```

Learn from feedback.

**Parameters:**
- `model` (Model): Model to update
- `feedback` (dict[str, Any]): Feedback dictionary

**Returns:** `Model` - Updated model

### Visualization Functions

```python
def visualize_network(self, network: BayesianNetwork) -> Figure
```

Visualize Bayesian network structure.

**Parameters:**
- `network` (BayesianNetwork): Bayesian network to visualize

**Returns:** `Figure` - Matplotlib figure

**Raises:**
- `VisualizationError`: If matplotlib is not available

```python
def plot_case_similarity(
    self, cases: list[tuple[Case, float]], query_case: Optional[Case] = None
) -> Figure
```

Plot case similarity scores.

**Parameters:**
- `cases` (list[tuple[Case, float]]): List of (case, similarity) tuples
- `query_case` (Optional[Case]): Optional query case for reference

**Returns:** `Figure` - Matplotlib figure

```python
def plot_inference_results(self, results: dict[str, Any]) -> Figure
```

Plot inference results.

**Parameters:**
- `results` (dict[str, Any]): Inference results dictionary

**Returns:** `Figure` - Matplotlib figure

## Data Structures

### Case

```python
@dataclass
class Case:
    case_id: str
    features: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    outcome: Optional[Any] = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

Represents a case in case-based reasoning.

### Model

```python
@dataclass
class Model:
    name: str
    model_type: str
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
```

Represents a cognitive model.

### ReasoningResult

```python
@dataclass
class ReasoningResult:
    prediction: Any
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)
    retrieved_cases: list[Any] = field(default_factory=list)
    inference_results: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
```

Result of a reasoning operation.

### Distribution

```python
@dataclass
class Distribution:
    values: list[Any]
    probabilities: list[float]
```

Represents a probability distribution.

### BeliefState

```python
@dataclass
class BeliefState:
    states: dict[str, float] = field(default_factory=dict)
    observations: dict[str, Any] = field(default_factory=dict)
```

Represents a belief state in active inference.

## Integration Points

### With `ai_code_editing`
- Use case-based reasoning to retrieve similar code generation patterns
- Apply Bayesian inference to predict code quality
- Enhance prompts with case-based context

### With `language_models`
- Use active inference to optimize LLM interactions
- Apply Bayesian methods for model selection
- Learn from LLM response patterns

### With `pattern_matching`
- Use case-based reasoning for pattern recognition
- Apply Bayesian inference for pattern confidence
- Learn new patterns from code analysis

### With `data_visualization`
- Visualize Bayesian networks and case structures
- Plot inference results and model performance
- Create interactive model exploration tools

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)

