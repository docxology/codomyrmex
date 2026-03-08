# Bio Simulation -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Ant Colony Simulation
- Individual ant agents with state machine behavior (SEARCHING, CARRYING, RETURNING).
- Grid environment with pheromone deposition, diffusion, and evaporation.
- Colony-level orchestration stepping all ants per simulation tick.

### FR-2: Genomics
- Genome representation supporting crossover and mutation operators.
- Population management with fitness-based selection.

## Interface Contracts

```python
class Ant:
    state: AntState
    def step(self, environment: Environment) -> None: ...

class Colony:
    def __init__(self, environment: Environment, num_ants: int): ...
    def step(self) -> None: ...

class Environment:
    def __init__(self, width: int, height: int): ...

class Genome:
    genes: list[float]
    def crossover(self, other: Genome) -> Genome: ...
    def mutate(self, rate: float) -> None: ...

class Population:
    def __init__(self, size: int, genome_length: int): ...
    def evolve(self, generations: int) -> Genome: ...
```

## Navigation

- **Source**: [src/codomyrmex/bio_simulation/](../../../../src/codomyrmex/bio_simulation/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
