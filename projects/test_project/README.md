# test_project — Codomyrmex Reference Implementation

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The **test_project** is the authoritative "Mega-Seed" reference implementation for the Codomyrmex ecosystem. It demonstrates real, production-ready integration with all core modules — no mocks, no placeholders, no fallbacks. Use it as a validated template for new Codomyrmex-powered projects.

## Quick Start

```bash
cd projects/test_project

# Install dependencies (uses local codomyrmex as editable)
uv sync

# Run the full demo (analysis → visualization → reporting → pipeline)
uv run python run_demo.py

# Run the test suite
uv run pytest tests/ -v
```

## What It Demonstrates

| Capability | Codomyrmex Module | Source File |
| :--- | :--- | :--- |
| Structured logging | `logging_monitoring` | `src/main.py` |
| Unified configuration | `config_management` | `src/main.py`, `src/pipeline.py` |
| Event-driven architecture | `events` | `src/main.py`, `src/pipeline.py` |
| Static code analysis | `static_analysis` | `src/analyzer.py` |
| Pattern recognition | `pattern_matching` | `src/analyzer.py` |
| DAG-based orchestration | `orchestrator` | `src/pipeline.py` |
| Multi-format serialization | `serialization` | `src/reporter.py`, `src/pipeline.py` |
| Input validation | `validation` | `src/pipeline.py` |
| Structured exceptions | `exceptions` | `src/pipeline.py` |
| Performance profiling | `performance` | `src/pipeline.py` |
| Data visualization | `data_visualization` | `src/visualizer.py` |
| Multi-format reporting | `documentation` | `src/reporter.py` |
| Agent registry + memory | `agents`, `agentic_memory` | `src/agent_brain.py` |
| Git operations + history | `git_operations`, `git_analysis` | `src/git_workflow.py` |
| Full-text + fuzzy search | `search`, `scrape`, `formal_verification` | `src/knowledge_search.py` |
| Security + cryptography | `security`, `crypto`, `maintenance`, `system_discovery` | `src/security_audit.py` |
| MCP discovery + skills | `model_context_protocol`, `skills`, `plugin_system` | `src/mcp_explorer.py` |
| LLM + swarm coordination | `llm`, `collaboration` | `src/llm_inference.py` |

**Coverage**: ~28 modules across Foundation, Core, Service, and Extended layers (~23% of 141 auto-discovered modules).

## Directory Structure

```text
test_project/
├── .codomyrmex/       # Project state and orchestration config
├── config/            # YAML configuration
│   ├── settings.yaml  # Core project settings
│   ├── modules.yaml   # Module enablement and overrides
│   └── workflows.yaml # DAG workflow definitions
├── src/               # Source modules
│   ├── main.py           # Entry point — logging, config, events
│   ├── analyzer.py       # Code analysis — static_analysis, pattern_matching
│   ├── visualizer.py     # Visualization — data_visualization
│   ├── reporter.py       # Reporting — documentation, serialization
│   ├── pipeline.py       # Orchestration — orchestrator, events, performance
│   ├── agent_brain.py    # Agents + agentic_memory
│   ├── git_workflow.py   # git_operations + git_analysis
│   ├── knowledge_search.py # search + scrape + formal_verification
│   ├── security_audit.py # security + crypto + maintenance + system_discovery
│   ├── mcp_explorer.py   # model_context_protocol + skills + plugin_system
│   └── llm_inference.py  # llm + collaboration
├── data/              # Input/output data
├── reports/           # Generated reports, dashboards, visualizations
├── tests/             # Pytest suite (100% zero-mock)
├── pyproject.toml     # uv-optimized project definition
└── run_demo.py        # Single-entrypoint demonstration script
```

## Test Suite

The project maintains a 100% rigorous zero-mock test suite:

- **Unit tests**: `test_analyzer.py`, `test_visualizer.py`, `test_reporter.py`, `test_pipeline.py`
- **Integration tests**: `test_codomyrmex_integration.py` — authentically verifies real imports and construction of all integrated modules, executing real Codomyrmex routines.

```bash
uv run pytest tests/ -v --tb=short
```

## Companion Documentation

| File        | Purpose                                     |
| :---------- | :------------------------------------------ |
| [SPEC.md](SPEC.md) | Functional specification & interface contracts |
| [AGENTS.md](AGENTS.md) | Agent coordination & operating contracts    |
| [PAI.md](PAI.md) | Personal AI context & guidelines            |

## Navigation

- **Parent**: [projects/](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Codomyrmex Source**: [../../src/codomyrmex/](../../src/codomyrmex/)
