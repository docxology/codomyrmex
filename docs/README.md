# Codomyrmex Documentation

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Overview

Comprehensive documentation for the Codomyrmex modular coding workspace — a production-grade ecosystem with **128 top-level modules**, **600** production `@mcp_tool` decorators (see [reference/inventory.md](reference/inventory.md)), and **39 agent packages** under `src/codomyrmex/agents/` (see [agents/](agents/)).

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

| Section | Purpose | Files |
|:---|:---|---:|
| [agents/](agents/) | **39 agent packages** — Claude, Gemini, Jules, Hermes ([skill preload / registry](agents/hermes/skills.md)), and 35 more | 121 |
| [agi/](agi/) | AGI theory, perspectives, emergence models | 14 |
| [bio/](bio/) | Biological simulation documentation | 15 |
| [cognitive/](cognitive/) | Cognitive architecture, Bayesian inference, active inference | 11 |
| [compliance/](compliance/) | Regulatory compliance, audit frameworks | 5 |
| [deployment/](deployment/) | Deployment guides, CI/CD, containerization | 5 |
| [development/](development/) | Developer guides, environment setup, testing strategy | 10 |
| [examples/](examples/) | Executable examples and tutorials | 8 |
| [getting-started/](getting-started/) | Quick start, installation, first steps | 9 |
| [integration/](integration/) | Cross-module integration patterns | 11 |
| [modules/](modules/) | Module-level documentation (128 top-level packages under `src/codomyrmex/`) | 9+ |
| [pai/](pai/) | PAI infrastructure, dashboard, skills, memory | 11 |
| [plans/](plans/) | Project roadmap and release plans | 6 |
| [project/](project/) | Project standards, contributing, architecture | 9 |
| [project_orchestration/](project_orchestration/) | Workflow orchestration, multi-agent coordination | 11 |
| [reference/](reference/) | API reference, CLI tools, configuration | 16 |
| [security/](security/) | Security policies, threat models, audit guides | 11 |
| [skills/](skills/) | Agent skill creation and management | 9 |
| [assets/](assets/) | Static assets (images, diagrams) | 2 |

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
