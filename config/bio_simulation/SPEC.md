# Bio Simulation Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Ant colony simulation with pheromone-based foraging and genomics/genetic algorithm integration. Provides Colony, Environment, Genome, and Population models. This specification documents the configuration schema and constraints.

## Configuration Schema

The bio_simulation module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Simulation parameters (colony size, environment dimensions, pheromone decay rate) are set through constructor arguments on Colony and Environment. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Simulation parameters (colony size, environment dimensions, pheromone decay rate) are set through constructor arguments on Colony and Environment.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/bio_simulation/SPEC.md)
