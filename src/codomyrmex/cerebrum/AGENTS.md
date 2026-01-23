# Codomyrmex Agents — src/codomyrmex/cerebrum

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

CEREBRUM (Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling) is a Specialized Layer module providing case-based reasoning combined with Bayesian probabilistic inference for cognitive modeling, code reasoning, and AI enhancement.

## Active Components

### Core Engine

- `core/` - Core reasoning engine and models
  - Key Classes: `CerebrumEngine`, `ModelManager`, `ReasoningEngine`
  - Key Functions: `reason()`, `create_cerebrum_engine()`

### Case Management

- `core/case.py` - Case storage and retrieval
  - Key Classes: `Case`, `CaseBase`, `CaseRetriever`
  - Key Functions: `create_case()`, `retrieve_similar()`

### Inference

- `inference/` - Bayesian and active inference
  - Key Classes: `BayesianNetwork`, `InferenceEngine`, `Distribution`, `PriorBuilder`
  - Key Classes: `ActiveInferenceAgent`, `BeliefState`, `VariationalFreeEnergy`, `PolicySelector`

### Visualization

- `visualization/` - Visualization components
  - Key Classes: `ModelVisualizer`, `CaseVisualizer`, `InferenceVisualizer`

### FPF Integration

- `fpf/` - First Principles Framework integration
  - Key Classes: `FPFOrchestrator`, `FPFCombinatoricsAnalyzer`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `CerebrumEngine` | core | Main orchestrator for reasoning |
| `Case` | core | Individual case representation |
| `CaseBase` | core | Case storage and management |
| `CaseRetriever` | core | Similar case retrieval |
| `BayesianNetwork` | inference | Probabilistic graphical model |
| `InferenceEngine` | inference | Bayesian inference operations |
| `ActiveInferenceAgent` | inference | Free energy minimizing agent |
| `BeliefState` | inference | Agent belief representation |
| `ModelVisualizer` | visualization | Reasoning process visualization |
| `compute_cosine_similarity()` | core/utils | Similarity computation |

## Operating Contracts

1. **Logging**: Uses `logging_monitoring` for reasoning traces
2. **Visualization**: Integrates with `data_visualization` for output
3. **Pattern Integration**: Can use `pattern_matching` for case retrieval
4. **Agent Enhancement**: Provides reasoning capabilities to `agents` module
5. **Error Handling**: Raises `CerebrumError` subclasses for specific failures

## Exception Hierarchy

- `CerebrumError` - Base exception
  - `CaseError` - Case-related errors
    - `CaseNotFoundError` - Case not found
    - `InvalidCaseError` - Invalid case structure
  - `InferenceError` - Inference failures
    - `BayesianInferenceError` - Bayesian network errors
    - `ActiveInferenceError` - Active inference errors
  - `ModelError` - Model-related errors
  - `TransformationError` - Transformation failures
  - `VisualizationError` - Visualization failures

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agents |
| fpf | [../fpf/AGENTS.md](../fpf/AGENTS.md) | Functional programming |
| data_visualization | [../data_visualization/AGENTS.md](../data_visualization/AGENTS.md) | Visualization |
| pattern_matching | [../pattern_matching/AGENTS.md](../pattern_matching/AGENTS.md) | Pattern analysis |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| core/ | Core engine and case management |
| inference/ | Bayesian and active inference |
| visualization/ | Visualization components |
| fpf/ | FPF integration |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tools
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Code examples
- [SPEC.md](SPEC.md) - Functional specification
