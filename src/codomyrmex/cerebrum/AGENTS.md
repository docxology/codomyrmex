# Codomyrmex Agents — src/codomyrmex/cerebrum

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [scripts](scripts/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling. Provides case-based reasoning combined with Bayesian probabilistic inference for cognitive modeling, code reasoning, and AI enhancement. Integrates case-based reasoning, Bayesian inference, and active inference based on free energy principle.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `FPF_INTEGRATION_SUMMARY.md` – FPF integration documentation
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `active_inference.py` – Active inference implementation
- `bayesian.py` – Bayesian inference capabilities
- `cases.py` – Case management and retrieval
- `composition_visualizer.py` – Composition visualization
- `concordance_visualizer.py` – Concordance visualization
- `config.py` – Configuration management
- `core.py` – Core engine and orchestrator
- `docs/` – Directory containing docs components
- `exceptions.py` – Custom exceptions
- `fpf_combinatorics.py` – FPF combinatorics analysis
- `fpf_orchestration.py` – FPF orchestration
- `models.py` – Model and result structures
- `scripts/` – Directory containing scripts components
- `tests/` – Directory containing tests components
- `transformations.py` – Model transformation and adaptation
- `utils.py` – Utility functions
- `visualization.py` – Visualization tools
- `visualization_base.py` – Visualization base classes
- `visualization_theme.py` – Visualization themes

## Key Classes and Functions

### CerebrumEngine (`core.py`)
- `CerebrumEngine(config: Optional[CerebrumConfig] = None)` – Main orchestrator for case-based reasoning and Bayesian inference
- `create_model(name: str, model_type: str, config: Optional[dict] = None) -> Model` – Create a new cognitive model
- `add_case(case: Case) -> None` – Add a case to the case base
- `reason(case: Case, context: Optional[dict] = None) -> ReasoningResult` – Perform reasoning on a case
- `learn_from_case(case: Case, outcome: Any) -> None` – Learn from a case
- `transform_model(model: Model, transformation: str, **kwargs) -> Model` – Transform a model

### CaseBase (`cases.py`)
- `CaseBase()` – Case storage and management
- `Case` (dataclass) – Case representation with features, context, and outcomes
- `CaseRetriever()` – Case retrieval with similarity matching

### BayesianNetwork (`bayesian.py`)
- `BayesianNetwork()` – Bayesian network structure
- `InferenceEngine()` – Bayesian inference engine
- `Distribution` – Probability distribution
- `PriorBuilder()` – Prior distribution builder

### ActiveInferenceAgent (`active_inference.py`)
- `ActiveInferenceAgent()` – Active inference based on free energy principle
- `BeliefState` – Belief state representation
- `VariationalFreeEnergy` – Free energy calculation
- `PolicySelector()` – Policy selection

### Model (`models.py`)
- `Model` (dataclass) – Cognitive model representation
- `ReasoningResult` (dataclass) – Reasoning result with prediction and confidence

### TransformationManager (`transformations.py`)
- `TransformationManager()` – Model transformation management
- `AdaptationTransformer()` – Adapt models to new cases
- `LearningTransformer()` – Learn from feedback

### Visualization (`visualization.py`)
- `ModelVisualizer()` – Visualize cognitive models
- `CaseVisualizer()` – Visualize cases
- `InferenceVisualizer()` – Visualize inference results

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation