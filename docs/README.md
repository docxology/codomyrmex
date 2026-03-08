# 📚 Codomyrmex Documentation

> **Version**: v1.1.9 | **Modules**: 128 | **Tests**: 21,000+ collected | **Ruff**: 0 violations

This directory contains all documentation for the Codomyrmex ecosystem — a modular, extensible Python workspace for autonomous software engineering, personal AI infrastructure, and multi-agent orchestration.

---

## Documentation Map

### 🚀 Getting Started

| Guide | Description |
|-------|-------------|
| [Quickstart](getting-started/quickstart.md) | Install and run in 5 minutes |
| [Full Setup](getting-started/full-setup.md) | Complete environment configuration |
| [Tutorials](getting-started/tutorials/) | Step-by-step walkthroughs |

### 🏗️ Architecture & Design

| Document | Description |
|----------|-------------|
| [Architecture](ARCHITECTURE.md) | System architecture, module hierarchy, data flow |
| [Specification](SPEC.md) | Functional spec, design principles, quality standards |
| [Agents](AGENTS.md) | Agent coordination, PAI bridge, MCP tools |

### 🤖 AI & Agents

| Section | Description |
|---------|-------------|
| [Agent Framework](agents/) | 13 agent providers, LLM clients, orchestration |
| [PAI Infrastructure](pai/) | Personal AI bridge, trust gateway, dashboards |
| [PAI Dashboard](PAI_DASHBOARD.md) | 15-tab SPA dashboard guide |
| [AGI Research](agi/) | Theoretical AGI frameworks, RASP patterns |

### 🧬 Research Domains

| Section | Description |
|---------|-------------|
| [Bio-Inspired](bio/) | Ant colony, swarm, stigmergic patterns |
| [Cognitive Science](cognitive/) | Active inference, signal theory, belief networks |
| [Security](security/) | STRIDE model, cognitive security, threat assessment |

### 🔧 Development

| Section | Description |
|---------|-------------|
| [Dev Guides](development/) | Testing, linting (ruff), type checking (ty), CI/CD |
| [Integration](integration/) | Module integration patterns, MCP bridge |
| [Examples](examples/) | Code examples and usage patterns |
| [Reference](reference/) | API reference, troubleshooting |

### 📦 Modules & Deployment

| Section | Description |
|---------|-------------|
| [Module Docs](modules/) | Per-module README, SPEC, AGENTS, PAI docs |
| [Deployment](deployment/) | Cloud, Docker, production configurations |
| [Compliance](compliance/) | Regulatory and licensing |
| [Skills](skills/) | Skill system and PAI integration |

### 📋 Project Management

| Section | Description |
|---------|-------------|
| [Project](project/) | Contributing, governance, roadmap |
| [Orchestration](project_orchestration/) | Jules swarms, multi-agent coordination |
| [Plans](plans/) | Release planning and roadmaps |

---

## Quality Metrics (v1.1.9)

| Metric | Value |
|--------|-------|
| Python modules | **128** auto-discovered |
| MCP tools | **474** `@mcp_tool` decorators |
| Test suite | **21,000+** collected |
| Ruff violations | **0** (triaged from 119k) |
| ty diagnostics | **971** (target < 1,000 met) |
| Coverage | ~35% (`fail_under=40`) |
| Documentation pages | **1,029+** |
| Zero-Mock compliance | **100%** |
| Build backend | **uv_build** (PEP 517) |

---

## Building the Docs

```bash
# Install docs dependencies
uv sync --extra docs

# Serve locally (with live reload)
uv run mkdocs serve

# Build static site (strict mode catches broken refs)
uv run mkdocs build --strict

# Or use justfile
just docs-serve
just docs-build
```

---

*Navigation: [Repository Root](../README.md) | [CHANGELOG](../CHANGELOG.md) | [TODO](../TODO.md)*
