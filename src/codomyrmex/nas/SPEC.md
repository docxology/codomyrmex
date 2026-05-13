# NAS -- Technical Specification


**Version**: v0.1.0 | **Status**: Active | **Last Updated**: May 2026

## Architecture

### Search Space

The `NASSearchSpace` defines categorical choices for each architecture dimension. Sampling respects the constraint that `d_model % n_heads == 0`.

### ArchConfig

Stores a sampled architecture with a `total_params_estimate` property:
```
params = n_layers * (4 * d_model^2 + 2 * d_model * d_ff) + d_model * 32000
```

### Random Search

1. Sample n_trials random architectures
2. Evaluate each with the pluggable eval_fn
3. Return the highest-scoring config

### Evolutionary Search

1. Initialize random population of population_size configs
2. For each generation:
   a. Sort by score, keep top 50%
   b. Mutate top configs to refill population
   c. Evaluate new population
3. Return best config from final generation

### Mutation

Randomly selects one dimension to change:
- `n_layers`: replace with random choice from space
- `d_model`: replace and re-select compatible n_heads
- `dropout`: replace with random choice
- `activation`: replace with random choice

## Limitations

- No weight-sharing or supernet-based search
- No hardware-aware evaluation (latency, memory)
- Evolutionary search uses simple tournament selection (top-50%)
- No crossover operator (mutation only)
- Parameter estimate assumes transformer encoder architecture

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../README.md)
