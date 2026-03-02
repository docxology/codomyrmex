# Cerebrum Inference -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview

This module implements two complementary probabilistic reasoning systems: classical Bayesian network inference and active inference based on the free energy principle. Both share the `Distribution` data type for representing probability distributions.

## 2. Data Types

### Distribution

```
Distribution(values: list[Any], probabilities: list[float])
```

- Auto-normalizes probabilities in `__post_init__`.
- `sample(n)` -- draw `n` samples via `numpy.random.choice`.
- `expectation()` -- weighted mean (numeric values only; raises `ValueError` otherwise).
- `mode()` -- value with highest probability.

### BeliefState

```
BeliefState(states: dict[str, float], observations: dict[str, Any])
```

- `normalize()` -- re-normalize state probabilities to sum to 1.
- `entropy()` -- Shannon entropy of the state distribution.

## 3. Bayesian Network API

### BayesianNetwork

| Method | Signature | Behavior |
|--------|-----------|----------|
| `add_node` | `(node: str, values: list, prior: list[float] | None)` | Registers node; raises `NetworkStructureError` on duplicate |
| `add_edge` | `(parent: str, child: str)` | Directed edge; validates both nodes exist |
| `set_cpt` | `(node: str, cpt: dict[tuple, dict[Any, float]])` | Sets conditional probability table; validates parent config length |
| `get_topological_order` | `() -> list[str]` | DFS-based topological sort |
| `to_dict` | `() -> dict` | Serializable representation |

### InferenceEngine

Constructor: `InferenceEngine(network: BayesianNetwork, method: str = "variable_elimination")`

| Method | Signature | Notes |
|--------|-----------|-------|
| `infer` | `(query: dict, evidence: dict | None) -> dict[str, Distribution]` | Dispatches to method-specific implementation |
| `compute_marginal` | `(variable: str, evidence: dict | None) -> Distribution` | Single-variable convenience wrapper |
| `update_beliefs` | `(evidence: dict) -> dict[str, Distribution]` | Queries all non-evidence variables |

**Inference methods**:
- `variable_elimination` -- exact brute-force enumeration over joint probability (suitable for small networks).
- `mcmc` -- Gibbs sampling with configurable `n_samples` (default 10000).

### PriorBuilder

| Method | Signature | Notes |
|--------|-----------|-------|
| `build_prior_from_cases` | `(cases: list, variable: str, feature_extractor: callable) -> Distribution` | Counts value frequencies across cases |

## 4. Active Inference API

### VariationalFreeEnergy

Constructor: `VariationalFreeEnergy(precision: float = 1.0)`

| Method | Returns | Formula |
|--------|---------|---------|
| `compute(beliefs, observations, likelihood)` | `float` | F = accuracy + complexity/precision |
| `compute_expected_free_energy(beliefs, policy, transition_model, observation_model)` | `float` | EFE = expected_complexity + expected_ambiguity |

### PolicySelector

Constructor: `PolicySelector(exploration_weight: float = 0.1)`

| Method | Returns | Strategy |
|--------|---------|----------|
| `select_policy(policies, efes, temperature)` | `str` | Softmax over negative EFE values |
| `select_greedy(policies, efes)` | `str` | Argmin of EFE values |

### ActiveInferenceAgent

Constructor: `ActiveInferenceAgent(states, observations, actions, precision, policy_horizon, exploration_weight)`

| Method | Signature | Behavior |
|--------|-----------|----------|
| `set_transition_model` | `(model: dict)` | P(s'|s, a) keyed as `"{state}_{action}"` |
| `set_observation_model` | `(model: dict)` | P(o|s) keyed by state |
| `predict` | `(observation: dict | None) -> dict[str, float]` | Bayesian belief update or current beliefs |
| `select_action` | `(state: dict | None) -> str` | EFE-based policy selection |
| `update_beliefs` | `(observation: dict)` | Updates internal `BeliefState` |
| `compute_free_energy` | `(beliefs, observations) -> float` | Delegates to `VariationalFreeEnergy` |
| `reset` | `()` | Resets to uniform beliefs |

## 5. Dependencies

- **Internal**: `cerebrum.core.exceptions` (InferenceError, NetworkStructureError, ActiveInferenceError), `cerebrum.core.utils` (softmax), `logging_monitoring`
- **External**: `numpy`, `math`

## 6. Constraints

- Variable elimination complexity is O(d^n) where d is domain size and n is number of variables -- use only for small networks.
- MCMC convergence is not guaranteed for all network topologies; agents should validate posterior normalization.
- Transition model keys follow the format `"{state}_{action}"` -- agents must match this convention.

## Navigation

- **Parent**: [cerebrum/](../README.md)
- **Project root**: [../../../../README.md](../../../../README.md)
