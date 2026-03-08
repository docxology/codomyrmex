# Cerebrum -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Case-Based Reasoning
- Cases shall have feature dictionaries for similarity-based retrieval.
- CaseRetriever shall support cosine similarity and Euclidean distance metrics.
- CaseBase shall store and index cases for efficient retrieval.

### FR-2: Bayesian Inference
- BayesianNetwork shall support directed acyclic graphs with conditional probability tables.
- InferenceEngine shall compute posterior distributions given evidence.

### FR-3: Active Inference
- ActiveInferenceAgent shall implement the free energy principle.
- BeliefState shall track the agent's beliefs about the environment.
- PolicySelector shall choose actions that minimize expected free energy.

### FR-4: Model Transformations
- ModelTransformer, AdaptationTransformer, LearningTransformer shall support model adaptation.
- TransformationManager shall orchestrate transformation chains.

## Interface Contracts

```python
def query_knowledge_base(query: str) -> dict
def add_case_reference(case: dict) -> dict
```

## Navigation

- **Source**: [src/codomyrmex/cerebrum/](../../../../src/codomyrmex/cerebrum/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
