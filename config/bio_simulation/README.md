# Bio Simulation Configuration

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Ant colony simulation with pheromone-based foraging and genomics/genetic algorithm integration. Provides Colony, Environment, Genome, and Population models.

## Configuration Options

The bio_simulation module operates with sensible defaults and does not require environment variable configuration. Simulation parameters (colony size, environment dimensions, pheromone decay rate) are set through constructor arguments on Colony and Environment.

## PAI Integration

PAI agents interact with bio_simulation through direct Python imports. Simulation parameters (colony size, environment dimensions, pheromone decay rate) are set through constructor arguments on Colony and Environment.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep bio_simulation

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/bio_simulation/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
