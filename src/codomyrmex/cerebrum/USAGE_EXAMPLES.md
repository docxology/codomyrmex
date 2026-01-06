# CEREBRUM - Usage Examples

This document provides practical usage examples for the CEREBRUM module.

## Basic Case-Based Reasoning

### Creating and Using Cases

```python
from codomyrmex.cerebrum import CerebrumEngine, Case, CerebrumConfig
from codomyrmex.logging_monitoring import setup_logging

# Setup logging
setup_logging()

# Create engine
config = CerebrumConfig(case_similarity_threshold=0.7, max_retrieved_cases=10)
engine = CerebrumEngine(config)

# Add cases
case1 = Case(
    case_id="code_review_001",
    features={"complexity": 5, "language": "python", "lines": 50},
    outcome="approved",
    metadata={"reviewer": "ai_agent"}
)

case2 = Case(
    case_id="code_review_002",
    features={"complexity": 3, "language": "python", "lines": 30},
    outcome="approved",
    metadata={"reviewer": "human"}
)

case3 = Case(
    case_id="code_review_003",
    features={"complexity": 8, "language": "python", "lines": 200},
    outcome="rejected",
    metadata={"reviewer": "ai_agent", "reason": "too_complex"}
)

engine.add_case(case1)
engine.add_case(case2)
engine.add_case(case3)

# Query similar cases
query = Case(
    case_id="query_001",
    features={"complexity": 6, "language": "python", "lines": 75}
)

result = engine.reason(query)
print(f"Prediction: {result.prediction}")
print(f"Confidence: {result.confidence}")
print(f"Retrieved {len(result.retrieved_cases)} similar cases")
```

## Bayesian Inference

### Creating a Bayesian Network

```python
from codomyrmex.cerebrum import BayesianNetwork, InferenceEngine

# Create network
network = BayesianNetwork(name="code_quality")

# Add nodes
network.add_node("complexity", values=["low", "medium", "high"], prior=[0.3, 0.5, 0.2])
network.add_node("test_coverage", values=["low", "high"], prior=[0.4, 0.6])
network.add_node("quality", values=["good", "bad"])

# Add edges
network.add_edge("complexity", "quality")
network.add_edge("test_coverage", "quality")

# Set conditional probability tables
network.set_cpt("quality", {
    ("low", "low"): {"good": 0.3, "bad": 0.7},
    ("low", "high"): {"good": 0.9, "bad": 0.1},
    ("medium", "low"): {"good": 0.5, "bad": 0.5},
    ("medium", "high"): {"good": 0.8, "bad": 0.2},
    ("high", "low"): {"good": 0.1, "bad": 0.9},
    ("high", "high"): {"good": 0.6, "bad": 0.4},
})

# Perform inference
inference = InferenceEngine(network, method="variable_elimination")

# Query quality given evidence
evidence = {"complexity": "high", "test_coverage": "high"}
result = inference.compute_marginal("quality", evidence)

print(f"Quality distribution:")
for value, prob in zip(result.values, result.probabilities):
    print(f"  {value}: {prob:.3f}")
```

## Active Inference

### Creating an Active Inference Agent

```python
from codomyrmex.cerebrum import ActiveInferenceAgent

# Create agent
agent = ActiveInferenceAgent(
    states=["code_good", "code_bad"],
    observations=["test_pass", "test_fail"],
    actions=["approve", "reject", "request_changes"],
    precision=1.0,
    policy_horizon=3
)

# Set transition model
agent.set_transition_model({
    "code_good_approve": {"code_good": 0.9, "code_bad": 0.1},
    "code_good_reject": {"code_good": 0.8, "code_bad": 0.2},
    "code_good_request_changes": {"code_good": 0.95, "code_bad": 0.05},
    "code_bad_approve": {"code_good": 0.2, "code_bad": 0.8},
    "code_bad_reject": {"code_good": 0.3, "code_bad": 0.7},
    "code_bad_request_changes": {"code_good": 0.6, "code_bad": 0.4},
})

# Set observation model
agent.set_observation_model({
    "code_good": {"test_pass": 0.9, "test_fail": 0.1},
    "code_bad": {"test_pass": 0.3, "test_fail": 0.7},
})

# Update beliefs with observation
agent.update_beliefs({"test_pass": True})

# Select action
action = agent.select_action()
print(f"Selected action: {action}")

# Compute free energy
free_energy = agent.compute_free_energy()
print(f"Free energy: {free_energy:.3f}")
```

## Model Transformation

### Adapting Models to Cases

```python
from codomyrmex.cerebrum import CerebrumEngine, Case, Model

# Create engine and model
engine = CerebrumEngine()
model = engine.create_model("code_quality_model", "case_based")

# Create case for adaptation
case = Case(
    case_id="adaptation_case",
    features={"complexity": 7, "language": "python"},
    outcome="needs_review"
)

# Adapt model to case
adapted_model = engine.transform_model(
    model,
    "adapt_to_case",
    case=case
)

print(f"Original model: {model.name}")
print(f"Adapted model: {adapted_model.name}")
```

### Learning from Feedback

```python
from codomyrmex.cerebrum import CerebrumEngine, Model

# Create engine and model
engine = CerebrumEngine()
model = engine.create_model("prediction_model", "bayesian")

# Learn from feedback
feedback = {
    "outcome": "success",
    "error": 0.1,
    "expected": "success"
}

learned_model = engine.transform_model(
    model,
    "learn_from_feedback",
    feedback=feedback
)

print(f"Learned model: {learned_model.name}")
```

## Integration with FPF Module

### Comprehensive FPF Analysis

```python
from codomyrmex.cerebrum.fpf_orchestration import FPFOrchestrator

# Create orchestrator (will fetch FPF from GitHub)
orchestrator = FPFOrchestrator(output_dir="output/fpf_analysis")

# Run comprehensive analysis
results = orchestrator.run_comprehensive_analysis()

# Access results
print(f"Analyzed {results['fpf_statistics']['total_patterns']} patterns")
print(f"Created {results['case_based_reasoning']['total_cases']} cases")
print(f"Critical patterns: {len(results['fpf_analysis']['critical_patterns'])}")
```

### Combinatorics Analysis

```python
from codomyrmex.cerebrum.fpf_combinatorics import FPFCombinatoricsAnalyzer

# Create analyzer
analyzer = FPFCombinatoricsAnalyzer(output_dir="output/combinatorics")

# Run combinatorics analysis
results = analyzer.run_comprehensive_combinatorics()

# Access results
print(f"Pattern pairs analyzed: {results['pattern_pairs']['total_pairs']}")
print(f"Dependency chains found: {results['dependency_chains']['total_chains']}")
print(f"Strong concept co-occurrences: {len(results['concept_cooccurrence']['strong_pairs'])}")
```

## Integration with Other Modules

### Integration with ai_code_editing

Use case-based reasoning to enhance code generation:

```python
from codomyrmex.cerebrum import CerebrumEngine, Case
from codomyrmex.agents.ai_code_editing import generate_code_snippet

# Create case from code generation request
case = Case(
    case_id="code_gen_001",
    features={"language": "python", "complexity": "medium"},
    outcome="generated_code"
)

# Reason about similar code generation patterns
result = engine.reason(case)
# Use result to enhance prompt or select model
```

### Integration with pattern_matching

Use case-based reasoning for pattern recognition:

```python
from codomyrmex.cerebrum import Case, CaseBase

# Create cases from code patterns
pattern_case = Case(
    case_id="pattern_001",
    features={"pattern_type": "singleton", "language": "python"},
    outcome="design_pattern"
)

# Retrieve similar patterns
similar = case_base.retrieve_similar(pattern_case, k=5)
```

## Visualization

### Visualizing Bayesian Networks

```python
from codomyrmex.cerebrum import BayesianNetwork, ModelVisualizer

# Create network
network = BayesianNetwork(name="example")
network.add_node("A", values=[0, 1])
network.add_node("B", values=[0, 1])
network.add_edge("A", "B")

# Visualize
visualizer = ModelVisualizer()
fig = visualizer.visualize_network(network)
fig.savefig("network.png")
```

### Visualizing Case Similarity

```python
from codomyrmex.cerebrum import Case, CaseBase, CaseVisualizer

# Create case base and add cases
case_base = CaseBase()
# ... add cases ...

# Retrieve similar cases
query = Case(case_id="query", features={"x": 1, "y": 2})
similar = case_base.retrieve_similar(query, k=10)

# Visualize
visualizer = CaseVisualizer()
fig = visualizer.plot_case_similarity(similar, query_case=query)
fig.savefig("case_similarity.png")
```

### Visualizing Inference Results

```python
from codomyrmex.cerebrum import BayesianNetwork, InferenceEngine, InferenceVisualizer

# Create network and perform inference
network = BayesianNetwork(name="example")
# ... setup network ...

inference = InferenceEngine(network)
results = inference.infer({"quality": None}, {"complexity": "high"})

# Visualize
visualizer = InferenceVisualizer()
fig = visualizer.plot_inference_results(results)
fig.savefig("inference_results.png")
```

## Advanced Usage

### Combining Case-Based and Bayesian Reasoning

```python
from codomyrmex.cerebrum import (
    CerebrumEngine, Case, BayesianNetwork, CerebrumConfig
)

# Create engine with Bayesian network
engine = CerebrumEngine()

# Setup Bayesian network
network = BayesianNetwork(name="quality_network")
network.add_node("complexity", values=["low", "high"])
network.add_node("quality", values=["good", "bad"])
network.add_edge("complexity", "quality")
network.set_cpt("quality", {
    ("low",): {"good": 0.9, "bad": 0.1},
    ("high",): {"good": 0.3, "bad": 0.7},
})

engine.set_bayesian_network(network)

# Add cases
engine.add_case(Case(
    case_id="case1",
    features={"complexity": "low"},
    outcome="good"
))

# Reason with both case-based and Bayesian inference
query = Case(case_id="query", features={"complexity": "high"})
result = engine.reason(query)

print(f"Prediction: {result.prediction}")
print(f"Confidence: {result.confidence}")
print(f"Bayesian results: {result.inference_results}")
```

## Running Comprehensive FPF Analysis

### Command Line

```bash
# Basic analysis
python -m codomyrmex.cerebrum.scripts.run_fpf_analysis

# Comprehensive analysis with combinatorics
python -m codomyrmex.cerebrum.scripts.run_comprehensive_fpf_analysis

# With custom FPF spec
python -m codomyrmex.cerebrum.scripts.run_comprehensive_fpf_analysis \
    --fpf-spec path/to/FPF-Spec.md \
    --output-dir output/my_analysis
```

### Python API

```python
from codomyrmex.cerebrum.fpf_orchestration import FPFOrchestrator
from codomyrmex.cerebrum.fpf_combinatorics import FPFCombinatoricsAnalyzer

# Main orchestration
orchestrator = FPFOrchestrator(output_dir="output/fpf_analysis")
results = orchestrator.run_comprehensive_analysis()

# Combinatorics
combinatorics = FPFCombinatoricsAnalyzer(output_dir="output/combinatorics")
combinatorics_results = combinatorics.run_comprehensive_combinatorics()
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
