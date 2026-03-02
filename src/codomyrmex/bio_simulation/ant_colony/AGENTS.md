# Ant Colony -- Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `ant_colony` submodule provides a discrete-time ant colony simulation with pheromone-based foraging. Agents use it for swarm intelligence experiments, emergent behavior analysis, and optimization algorithm prototyping.

## Key Components

| Component | Kind | Description |
|-----------|------|-------------|
| `Ant` | dataclass | Autonomous foraging agent with position, energy, carrying capacity, and pheromone trail |
| `AntState` | enum | Behavioral states: `FORAGING`, `RETURNING`, `IDLE` |
| `Colony` | class | Simulation orchestrator managing ant population, food collection, and pheromone decay |
| `Environment` | class | Grid-based world with pheromone map, food sources, and obstacles |
| `FoodSource` | dataclass | Localized food deposit at a grid position |

## Operating Contracts

- **Stateful simulation**: `Colony.simulate_step()` advances the simulation by one tick; call repeatedly for multi-step runs.
- **Pheromone decay**: Environment pheromones decay multiplicatively each tick (default rate 0.95); cells below 0.01 are pruned.
- **Energy model**: Ants consume 0.5 energy per movement step; dead ants (energy <= 0) are skipped.
- **Carry capacity**: Each ant can carry a maximum of 10 food units.
- **No MCP tools**: This submodule has no `@mcp_tool` decorators; access is via direct Python import only.

## Integration Points

- **Parent module**: `bio_simulation` re-exports `Ant`, `AntState`, `Colony`, `Environment`.
- **Genomics sibling**: Can be combined with `bio_simulation.genomics` to evolve ant behavioral parameters.
- **Data visualization**: Colony statistics (`get_stats()`) produce dict output suitable for charting.

## Navigation

- **Parent**: [bio_simulation/AGENTS.md](../AGENTS.md)
- **Siblings**: [SPEC.md](SPEC.md), [README.md](README.md), [PAI.md](PAI.md)
