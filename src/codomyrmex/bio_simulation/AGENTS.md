# Agent Instructions for `codomyrmex.bio_simulation`

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Context

The Bio-Simulation module provides high-fidelity ant colony simulation. It is used for studying emergent behavior patterns that inform the Codomyrmex agent architecture.

## Usage Guidelines

1. **Importing**: Import from the module root for most uses.

   ```python
   from codomyrmex.bio_simulation import Colony, Ant, AntState, Environment, Genome, Population
   ```

2. **Colony Simulation**: Create colonies with `Colony(population=N)` and advance time with `colony.step(hours=H)`. Each hour corresponds to 60 ticks.

3. **Genomics**: Use `Genome.random()` for synthetic genomes with default traits (speed, strength, perception, endurance).

4. **Zero-Mock Policy**: Tests must instantiate real objects. No mocking of simulation state is allowed.

5. **Performance**: Large populations (> 100k) may be slow. Use smaller populations for quick experiments.

6. **Safety**: Dead ants are automatically removed from `colony.ants` during `step()`.

7. **MCP Tools**: Use `bio_simulation_run_colony` and `bio_simulation_evolve_population` exposed in `mcp_tools.py` for agentic interactions and retrieving stats/distributions easily via the MCP framework.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
