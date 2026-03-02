# Genomics -- Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `genomics` submodule provides genetic algorithm primitives: a `Genome` dataclass for individual genetic representation and a `Population` class that manages tournament selection, single-point crossover, Gaussian mutation, and elitism across generations.

## Key Components

| Component | Kind | Description |
|-----------|------|-------------|
| `Genome` | dataclass | Fixed-length vector of gene values in [0, 1] with mutation, crossover, and fitness scoring |
| `Population` | class | Evolutionary simulation with tournament selection, crossover, mutation, and elitism |

## Operating Contracts

- **Gene values**: All gene values are clamped to [0.0, 1.0].
- **Default fitness**: Mean gene value (higher is better). Override by subclassing `Genome.fitness_score()`.
- **Elitism**: `Population.evolve()` preserves the best individual from each generation.
- **Tournament selection**: Selects `tournament_size` random candidates, picks the fittest.
- **Mutation**: Per-gene probability; mutated genes receive Gaussian perturbation (sigma=0.1), clamped to [0, 1].
- **Crossover**: Single-point; both parents must have equal genome length or `ValueError` is raised.
- **No MCP tools**: This submodule has no `@mcp_tool` decorators; access is via direct Python import only.

## Integration Points

- **Parent module**: `bio_simulation` re-exports `Genome` and `Population`.
- **Ant colony sibling**: Genome parameters can encode ant behavioral traits for co-evolutionary experiments.
- **Data visualization**: `Population.history` returns per-generation fitness dicts suitable for line plots.

## Navigation

- **Parent**: [bio_simulation/AGENTS.md](../AGENTS.md)
- **Siblings**: [SPEC.md](SPEC.md), [README.md](README.md), [PAI.md](PAI.md)
