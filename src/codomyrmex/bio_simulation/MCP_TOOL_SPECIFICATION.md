# Bio-Simulation - MCP Tool Specification

This document outlines the specification for tools within the Bio-Simulation module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: Active MCP Tools

The Bio-Simulation module exposes tools for integrating biological simulation runs and genomics analysis into an external agent's context using the Model Context Protocol (MCP).

### Tool: `bio_simulate_colony`

- **Purpose**: Instantiates and steps an ant colony simulation.
- **Parameters**:
  - `population` (int): Number of ant agents to spawn.
  - `hours` (int): Number of hours to advance the simulation.
- **Returns**: A dictionary containing statistics of the simulated colony including life/death counts, food collected, and state distributions.

### Tool: `bio_analyze_genetics`

- **Purpose**: Instantiates and evolves a population of genomes using a genetic algorithm.
- **Parameters**:
  - `population_size` (int): Total genomes in the population.
  - `generations` (int): Number of generations to evolve.
- **Returns**: A dictionary detailing trait distribution statistics (mean, std, min, max) for standard traits.

For details on how to use the bio_simulation functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
