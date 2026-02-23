# Agent Instructions for `codomyrmex.bio_simulation`

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Context

The Bio-Simulation module provides high-fidelity ant colony simulation with individual agent behavior, pheromone signaling, and population genomics. It is used for studying emergent behavior patterns that inform the Codomyrmex agent architecture.

## Usage Guidelines

1. **Importing**: Import from the module root.

   ```python
   from codomyrmex.bio_simulation import Colony, Ant, AntState, Environment, Genome, Population
   ```

2. **Colony Simulation**: Create colonies with `Colony(population=N)` and advance time with `colony.step(hours=H)`. Each step processes agent state machines, pheromone diffusion, and resource depletion.

3. **Genomics**: Use `Genome.random()` for synthetic genomes. `Population` tracks allele frequencies and trait distributions across generations.

4. **Zero-Mock Policy**: Tests must instantiate real `Colony` and `Population` objects — no mocking of simulation state. Use small populations (N < 100) for test speed.

5. **Performance**: Colony simulation is CPU-bound. For populations > 10,000, consider using `step(hours=1)` increments instead of large time jumps.

## Key Files

| File | Purpose |
|------|---------|
| `ant_colony/colony.py` | Colony lifecycle and population dynamics |
| `ant_colony/ant.py` | Individual agent behavior and state machine |
| `ant_colony/environment.py` | Spatial environment and resource management |
| `genomics/genome.py` | Genome representation and expression |
| `genomics/population.py` | Population genetics simulation |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md) | [Parent](../AGENTS.md)
