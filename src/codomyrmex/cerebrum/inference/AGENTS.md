# Cerebrum Inference -- Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Probabilistic inference engine providing Bayesian network reasoning and active inference for the cerebrum subsystem. Agents use this module to construct graphical models, perform exact and approximate inference, and implement free-energy-based action selection.

## Key Components

| File | Class / Export | Role |
|------|---------------|------|
| `bayesian.py` | `Distribution` | Probability distribution with `sample()`, `expectation()`, `mode()` |
| `bayesian.py` | `BayesianNetwork` | Directed graphical model -- `add_node()`, `add_edge()`, `set_cpt()`, `get_topological_order()` |
| `bayesian.py` | `InferenceEngine` | Posterior computation via `variable_elimination` or `mcmc` -- `infer()`, `compute_marginal()`, `update_beliefs()` |
| `bayesian.py` | `PriorBuilder` | Constructs `Distribution` from case data -- `build_prior_from_cases()` |
| `active_inference.py` | `BeliefState` | State-observation belief container -- `normalize()`, `entropy()` |
| `active_inference.py` | `VariationalFreeEnergy` | Free energy calculator -- `compute()`, `compute_expected_free_energy()` |
| `active_inference.py` | `PolicySelector` | Action selection -- `select_policy()` (softmax), `select_greedy()` (argmin EFE) |
| `active_inference.py` | `ActiveInferenceAgent` | Full agent loop -- `predict()`, `select_action()`, `update_beliefs()`, `compute_free_energy()`, `reset()` |

## Agent Operating Contract

1. **Network construction** -- Build a `BayesianNetwork`, add nodes with value domains and optional priors, add directed edges, then set conditional probability tables via `set_cpt()`.
2. **Inference** -- Wrap the network in an `InferenceEngine(network, method)`. Call `infer(query, evidence)` to get posterior `Distribution` objects. Choose `variable_elimination` for small exact networks or `mcmc` for approximate sampling.
3. **Active inference** -- Instantiate `ActiveInferenceAgent(states, observations, actions)`. Provide transition and observation models via `set_transition_model()` / `set_observation_model()`. Call `select_action()` for EFE-based policy selection and `update_beliefs()` after each observation.
4. **Prior construction** -- Use `PriorBuilder.build_prior_from_cases()` with a feature extractor callable to derive empirical priors from case libraries.

## Error Handling

- `InferenceError` -- raised by `InferenceEngine` for unknown methods, missing query variables, or degenerate distributions.
- `NetworkStructureError` -- raised by `BayesianNetwork` for duplicate nodes, missing nodes on edge creation, or CPT dimension mismatches.
- `ActiveInferenceError` -- raised by `PolicySelector` and `ActiveInferenceAgent` for empty policy lists or length mismatches.

All exceptions originate from `codomyrmex.cerebrum.core.exceptions`.

## Dependencies

- **Internal**: `codomyrmex.cerebrum.core.exceptions`, `codomyrmex.cerebrum.core.utils` (`softmax`), `codomyrmex.logging_monitoring`
- **External**: `numpy`

## Testing Guidance

- Construct small networks (3-5 nodes) and verify posterior distributions sum to 1.0 after `infer()`.
- Test `ActiveInferenceAgent` by setting deterministic transition/observation models and confirming `select_action()` returns the lowest-EFE action.
- Validate `PriorBuilder` output distributions match empirical frequencies of input cases.
- No mocks -- use real `BayesianNetwork` and `InferenceEngine` instances.

## Navigation

- **Parent**: [cerebrum/](../README.md)
- **Sibling**: [visualization/](../visualization/AGENTS.md)
- **Project root**: [../../../../README.md](../../../../README.md)
