# Codomyrmex Documentation

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Comprehensive documentation for the Codomyrmex modular coding workspace — a production-grade ecosystem with **130 top-level modules**, **610** production `@mcp_tool` decorators (see [reference/inventory.md](reference/inventory.md)), and **39 agent packages** under `src/codomyrmex/agents/` (see [agents/](agents/)).

## Documentation Map

### Top-Level References

| Document | Description |
|:---|:---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, layers, module graph (448 lines) |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Dependency compatibility, version constraints |
| [PAI.md](PAI.md) | Personal AI Infrastructure documentation hub |
| [PAI_DASHBOARD.md](PAI_DASHBOARD.md) | Dashboard functionality matrix (Admin :8787, PM :8888) |
| [SPEC.md](SPEC.md) | Functional specification |
| [index.md](index.md) | Documentation site entry point |
| [reference/inventory.md](reference/inventory.md) | Repo metrics (modules, MCP tools, tests) — refresh via `scripts/doc_inventory.py` |

### Documentation Sections

Volatile counts (module totals, MCP decorators, and test collection) are kept in [reference/inventory.md](reference/inventory.md) and refreshed with `uv run python scripts/doc_inventory.py`. The table below describes ownership instead of duplicating fast-drifting per-folder file counts.

| Section | Purpose | Ownership |
|:---|:---|:---|
| [agents/](agents/) | Agent package docs — Claude, Gemini, Jules, Hermes ([skill preload / registry](agents/hermes/skills.md)), and related integrations | Mirrors `src/codomyrmex/agents/` plus docs-only agent guidance |
| [agi/](agi/) | AGI theory, perspectives, emergence models | Narrative documentation |
| [bio/](bio/) | Biological simulation documentation | Narrative + module-adjacent guides |
| [cognitive/](cognitive/) | Cognitive architecture, Bayesian inference, active inference | Narrative + module-adjacent guides |
| [compliance/](compliance/) | Regulatory compliance, audit frameworks | Policy/reference documentation |
| [deployment/](deployment/) | Deployment guides, CI/CD, containerization | Operational documentation |
| [development/](development/) | Developer guides, environment setup, testing strategy | Contributor documentation |
| [examples/](examples/) | Executable examples and tutorials | Example walkthroughs |
| [getting-started/](getting-started/) | Quick start, installation, first steps | User onboarding |
| [integration/](integration/) | Cross-module integration patterns | Integration guidance |
| [modules/](modules/) | Module-level documentation for top-level packages under `src/codomyrmex/` | Mirrors source modules; see [modules/AGENTS.md](modules/AGENTS.md) |
| [pai/](pai/) | PAI infrastructure, dashboard, skills, memory | PAI guides and references |
| [plans/](plans/) | Project roadmap and release plans | Planning records |
| [project/](project/) | Project standards, contributing, architecture | Repository governance |
| [project_orchestration/](project_orchestration/) | Workflow orchestration, multi-agent coordination | Orchestration guides |
| [reference/](reference/) | API reference, CLI tools, configuration | Generated and curated references |
| [security/](security/) | Security policies, threat models, audit guides | Security documentation |
| [skills/](skills/) | Agent skill creation and management | Skill authoring/reference |
| [assets/](assets/) | Static assets (images, diagrams) | Documentation assets |

## Authoritative Numbers

Volatile counts that appear in prose must be sourced from these files — never hard-coded:

| Metric | Authoritative source |
|:---|:---|
| Test count (colony_kernel scope) | `RESULT_TEST_COUNT` in `output/data/manuscript_variables.json` |
| Gate weights (budget/risk/trust/completeness) | `docs/manuscript/config.yaml` → `experiment.gate_score_weights` (0.30 / 0.30 / 0.25 / 0.15) |
| Colony kernel subsystems (8) | `src/codomyrmex/colony_kernel/*` standalone modules plus `kernel.py` coordinator — PheromoneStore, ResourceLedger, ActuationGate, ConsequenceMemory, RoleAdapter, PruningDaemon, FalsificationWorker, ColonyKernel |
| MCP tools (8) | `src/codomyrmex/colony_kernel/mcp_tools.py` |
| Falsification attack vector name | `CIRCULAR_ARCHITECTURE` (not `CIRCULAR_DEPS`) |
| Module, MCP decorator, and file totals | [reference/inventory.md](reference/inventory.md) — refresh with `uv run python scripts/doc_inventory.py` |

## Quick Navigation

### For Users
- **Start Here**: [getting-started/quickstart.md](getting-started/quickstart.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Reference**: [reference/api.md](reference/api.md)
- **Examples**: [examples/](examples/)

### For Developers
- **Environment Setup**: [development/environment-setup.md](development/environment-setup.md)
- **Testing Strategy**: [development/testing-strategy.md](development/testing-strategy.md)
- **Code Review & SARIF**: [development/code-review-and-sarif.md](development/code-review-and-sarif.md) — local `scripts/review/` helpers and Bandit SARIF triage
- **Contributing**: [project/contributing.md](project/contributing.md)

### For Agents
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **Agent Integrations**: [agents/](agents/)
- **PAI Infrastructure**: [pai/](pai/)
- **Module Documentation**: [modules/](modules/)

## Navigation

- **Project Root**: [README.md](../README.md)
- **Root AGENTS.md**: [AGENTS.md](../AGENTS.md)
- **Source Code**: [src/codomyrmex/](../src/codomyrmex/)
