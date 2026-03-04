# Simulation Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Discrete event simulation and agent-based modeling. Provides simulation environments, event scheduling, and statistical analysis of simulation results.

## Configuration Options

The simulation module operates with sensible defaults and does not require environment variable configuration. Simulation parameters (time step, duration, random seed) are set per-simulation run. Event schedulers support priority queues.

## PAI Integration

PAI agents interact with simulation through direct Python imports. Simulation parameters (time step, duration, random seed) are set per-simulation run. Event schedulers support priority queues.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep simulation

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/simulation/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
