# Codomyrmex Agents - src/codomyrmex/cerebrum/inference

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Probabilistic inference module for the CEREBRUM cognitive framework. Implements Bayesian network reasoning with variable elimination and MCMC inference methods, plus active inference based on the free energy principle. This module provides the probabilistic foundations for belief updating, uncertainty quantification, and decision-making under uncertainty.

## Active Components

- `bayesian.py` - Bayesian network and inference engine (BayesianNetwork, InferenceEngine, PriorBuilder, Distribution)
- `active_inference.py` - Active inference agent based on free energy principle (ActiveInferenceAgent, VariationalFreeEnergy, PolicySelector, BeliefState)

## Key Classes

### BayesianNetwork (bayesian.py)
Probabilistic graphical model representing variable dependencies:
- `add_node()`: Add random variable with possible values and optional prior
- `add_edge()`: Add directed dependency from parent to child node
- `set_cpt()`: Set conditional probability table for a node
- `get_topological_order()`: Get nodes in dependency order (parents before children)
- Stores nodes, edges, parents, and CPTs as Distribution objects

### Distribution (bayesian.py)
Represents a probability distribution over discrete values:
- `values`: List of possible values
- `probabilities`: Corresponding probabilities (auto-normalized)
- `sample()`: Draw random samples from distribution
- `expectation()`: Compute expected value for numeric distributions
- `mode()`: Get most probable value

### InferenceEngine (bayesian.py)
Performs probabilistic inference on Bayesian networks:
- Supports `variable_elimination` (exact) and `mcmc` (approximate) methods
- `infer()`: Compute posterior distributions given evidence
- `compute_marginal()`: Get marginal distribution of single variable
- `update_beliefs()`: Update all variable beliefs given new evidence
- Uses joint probability computation and Gibbs sampling

### PriorBuilder (bayesian.py)
Constructs prior distributions from case data:
- `build_prior_from_cases()`: Extract prior from case outcomes
- Uses frequency counting to estimate probabilities
- Integrates with case-based reasoning for informed priors

### ActiveInferenceAgent (active_inference.py)
Implements active inference based on the free energy principle:
- Manages states, observations, and available actions
- `set_transition_model()`: Define state transition probabilities P(s'|s,a)
- `set_observation_model()`: Define observation probabilities P(o|s)
- `predict()`: Predict state distribution given observations (Bayesian update)
- `select_action()`: Choose action minimizing expected free energy
- `update_beliefs()`: Update belief state based on new observations
- `compute_free_energy()`: Calculate variational free energy

### BeliefState (active_inference.py)
Represents agent's belief state in active inference:
- `states`: Dictionary mapping state names to probabilities
- `observations`: Recorded observations
- `normalize()`: Ensure probabilities sum to 1
- `entropy()`: Compute belief distribution entropy

### VariationalFreeEnergy (active_inference.py)
Computes variational free energy for active inference:
- `compute()`: Calculate F = accuracy + complexity/precision
- `compute_expected_free_energy()`: Evaluate EFE for policy selection
- Implements simplified free energy principle calculations

### PolicySelector (active_inference.py)
Selects actions/policies based on expected free energy:
- `select_policy()`: Softmax selection over EFE values
- `select_greedy()`: Choose policy with lowest EFE
- Configurable exploration weight and temperature

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- BayesianNetwork nodes must be added before edges referencing them
- CPT configurations must match parent node count and values
- Probabilities are automatically normalized in Distribution
- InferenceEngine queries must reference existing network nodes
- ActiveInferenceAgent requires transition and observation models before action selection
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Core Module**: `../core/` - CerebrumEngine integrates BayesianNetwork and ActiveInferenceAgent
- **Visualization Module**: `../visualization/` - ModelVisualizer renders Bayesian networks
- **FPF Integration**: `../fpf/` - Uses Bayesian inference for FPF pattern importance
- **Parent Directory**: [cerebrum](../README.md) - CEREBRUM framework documentation
- **Project Root**: ../../../../README.md - Main project documentation
