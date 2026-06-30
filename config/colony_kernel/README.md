# colony_kernel

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Static configuration for the ColonyKernel — the central coordination substrate that
manages agent trust, budget limits, pheromone dynamics, and gate thresholds. These
YAML files are loaded at kernel startup and validated against the
`ColonyKernelConfig` Pydantic model before any agent activity begins.

## Directory Contents

- `kernel.yaml` — Top-level `ColonyKernelConfig`: database path, repository root,
  budget caps, pheromone tuning parameters, and gate accept/hold thresholds.
- `roles.yaml` — Role promotion thresholds and per-role action-type allowlists.
  Controls which trust score and action history an agent needs before it is
  promoted from `sandbox` to `guard_ant`, `repair_ant`, `memory_ant`, or
  `dispatcher`.
- `decay_rates.yaml` — Named decay-rate multipliers (`FAST`, `NORMAL`, `SLOW`)
  applied to `pheromone.evaporation_per_tick`, plus the default tier assigned to
  each signal type (`FAILURE`, `SUCCESS`, `RISK`, etc.).
- `README.md` — This document.
- `AGENTS.md` — Agent coordination and navigation.

## What Each File Controls

### kernel.yaml

| Section | Controls |
|---|---|
| `db_path` | SQLite file path; `null` = in-memory (tests only) |
| `repo_root` | Working-tree root passed to all file-system tools |
| `budget.*` | Hard caps on LLM calls, wall time, risk exposure, and doc debt per `period_seconds` |
| `pheromone.*` | Evaporation rate, reinforcement delta, and strength floor/ceiling for the shared pheromone map |
| `gate.*` | Trust and pheromone thresholds that classify an incoming proposal as EXECUTE, HOLD, or HARD_REFUSE |

### roles.yaml

| Section | Controls |
|---|---|
| `thresholds.<role>.min_trust` | Minimum trust score required for promotion to this role |
| `thresholds.<role>.required_action_types` | Action types the agent must have executed at least once |
| `thresholds.dispatcher.min_total_proposals` | Minimum lifetime proposals before dispatcher eligibility |
| `thresholds.dispatcher.min_acceptance_rate` | Acceptance rate floor for dispatcher eligibility |
| `thresholds.sandbox.max_trust` | Trust ceiling above which an agent is no longer sandbox-only |
| `defaults.new_agent_trust` | Trust assigned to a newly registered agent |
| `defaults.new_agent_role` | Role assigned to a newly registered agent |

### decay_rates.yaml

| Key | Controls |
|---|---|
| `FAST` / `NORMAL` / `SLOW` | Multipliers on `pheromone.evaporation_per_tick` |
| `signal_defaults.<type>` | Which tier is used for a given signal type unless explicitly overridden at emission time |

## Overriding Values

All three files are loaded by `ColonyKernel` via
`ColonyKernelConfig.from_config_dir(path)`. To override for a specific
deployment:

1. **Environment variable** — Set `CODOMYRMEX_KERNEL_CONFIG_DIR` to an
   alternate directory containing any subset of these files. Missing files fall
   back to the packaged defaults here.
2. **Per-file override** — Copy only the file you need to change into the
   override directory. Files not present in the override directory are loaded
   from this directory.
3. **Programmatic** — Pass a `ColonyKernelConfig` instance directly to
   `ColonyKernel(config=...)` to skip file loading entirely (useful in tests).

For production deployments set `db_path` to an absolute path such as
`~/.codomyrmex/colony.db` so the colony state survives process restarts.

## Navigation

- **Parent Directory**: [config](../README.md)
- **Project Root**: ../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.
