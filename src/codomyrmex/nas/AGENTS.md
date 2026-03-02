# NAS -- Agent Integration Guide

## Module Purpose

Provides neural architecture search capabilities for AI agents that need to explore model design spaces, compare architectures, or recommend model configurations.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `nas_sample_architecture` | Sample a random architecture from default space | `seed: int` | `{n_layers, d_model, n_heads, d_ff, dropout, activation, total_params_estimate}` |
| `nas_random_search` | Run random NAS with size-based heuristic | `n_trials: int`, `seed: int` | `{best_config, best_score, total_evaluated}` |

## Agent Use Cases

### Architecture Exploration
An agent can sample random architectures to understand the search space and parameter tradeoffs.

### Model Size Optimization
Use `nas_random_search` to find architectures that balance model size and capacity.

### Design Space Analysis
Agents can repeatedly sample to build statistical profiles of the architecture space.

## Example Agent Workflow

```
1. Agent receives: "Suggest a transformer architecture around 10M parameters"
2. Agent calls: nas_random_search(n_trials=50, seed=42)
3. Response: {"best_config": {"n_layers": 4, "d_model": 256, ...}, "best_score": -0.12}
4. Agent presents: "Recommended: 4-layer, 256-dim transformer (~10.5M params)"
```
