# Agent Instructions for `codomyrmex.bio_simulation`

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, biological model design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, simulation output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Build colony simulations, configure genomics pipelines, full implementation access during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Review biological model architecture, validate simulation fidelity patterns, inspect population dynamics design

### QATester Agent
**Use Cases**: Validate simulation outputs against expected distributions, verify colony lifecycle correctness, population genetics accuracy testing

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md) | [Parent](../AGENTS.md)
