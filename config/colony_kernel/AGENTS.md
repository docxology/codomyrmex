# Codomyrmex Agents — config/colony_kernel

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Static configuration files for the ColonyKernel — the central coordination
substrate responsible for agent trust scoring, budget enforcement, pheromone
dynamics, and proposal gate decisions.

## Active Components

- `kernel.yaml` — Top-level `ColonyKernelConfig`: db path, repo root, budget caps,
  pheromone parameters, and gate thresholds.
- `roles.yaml` — Role promotion thresholds and per-role action-type allowlists
  governing when an agent is elevated from `sandbox` to a named role.
- `decay_rates.yaml` — Named pheromone decay-rate multipliers and per-signal-type
  default tier assignments.
- `README.md` — Human-readable reference: what each file controls and how to
  override values for alternate deployments.

## Operating Contracts

- Maintain alignment between config values, the `ColonyKernelConfig` Pydantic
  schema, and any unit tests that assert on default values.
- Never lower a trust threshold without a corresponding gate-audit confirming the
  change does not admit under-trusted agents to sensitive roles.
- `db_path: null` is reserved for in-memory test runs; production deployments
  must set an absolute path before first use.
- Budget period (`period_seconds`) must be positive and non-zero; the kernel
  treats a zero period as a configuration error and refuses to start.
- Ensure Model Context Protocol interfaces remain available for sibling agents
  that query the kernel for its active configuration at runtime.
- Record outcomes in shared telemetry and update TODO queues when threshold
  values are changed.

## Key Files

- `AGENTS.md` — Agent coordination and navigation (this file)
- `README.md` — Directory overview and override instructions
- `kernel.yaml` — Primary kernel config (budget, pheromone, gate)
- `roles.yaml` — Role thresholds and defaults
- `decay_rates.yaml` — Decay-rate multipliers and signal defaults

## Dependencies

- Inherits dependencies from the parent `config/` module.
- Consumed by `src/codomyrmex/colony_kernel/` at startup via
  `ColonyKernelConfig.from_config_dir()`.
- Tests that assert on default values must import from
  `codomyrmex.colony_kernel.config` — never hard-code numeric literals.
- See `pyproject.toml` for global dependencies.

## Development Guidelines

- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).
- When adding a new config key, update the `ColonyKernelConfig` Pydantic model,
  this `AGENTS.md`, `README.md`, and any relevant test fixtures in the same PR.

## Navigation Links

- **Parent Directory**: [config](../README.md) - Parent directory documentation
- **Project Root**: ../../README.md - Main project documentation
