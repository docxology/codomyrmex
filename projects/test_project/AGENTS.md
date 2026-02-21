# Codomyrmex Agents — projects/test_project

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Authoritative "Mega-Seed" reference implementation demonstrating maximal, real (zero-mock) integration of Codomyrmex modules. Serves as both a validation suite and a template for new projects.

## Active Components

| Component | Type | Description |
| :--- | :--- | :--- |
| `src/main.py` | Entry point | Logging, config, events integration |
| `src/analyzer.py` | Analysis | Static analysis and pattern matching |
| `src/visualizer.py` | Visualization | Dashboard generation via `data_visualization` |
| `src/reporter.py` | Reporting | Multi-format output (HTML, JSON, Markdown) via `serialization` |
| `src/pipeline.py` | Orchestration | DAG-based workflow with `performance` profiling and structured `exceptions` |
| `config/` | Configuration | YAML settings, modules, workflows |
| `tests/` | Test suite | Unit tests + zero-mock integration tests |
| `run_demo.py` | Demo | Single-entrypoint full demonstration |

## Integrated Codomyrmex Modules

### Foundation Layer

- `logging_monitoring` — Structured JSON logging
- `config_management` — Unified YAML configuration
- `performance` — Pipeline execution profiling
- `environment_setup` — Python version validation

### Core Layer

- `static_analysis` — Code quality and metrics
- `pattern_matching` — Code pattern recognition
- `data_visualization` — Charts and dashboards
- `validation` — Schema-driven input validation

### Service Layer

- `orchestrator` — DAG-based pipeline execution
- `documentation` — Report generation

### Utility Layer

- `serialization` — JSON/YAML data encoding
- `events` — Pub/Sub event bus
- `exceptions` — Structured error hierarchy
- `llm` — LLM provider integration (tested)

## Operating Contracts

1. **Zero-Mock Policy**: All integrations use real module logic. No mocking, no stubs.
2. **Quadruple Play**: Maintain README, AGENTS, SPEC, PAI at every key directory level.
3. **Preserve Template Nature**: Changes must maintain the demonstration/reference character.
4. **Layer Discipline**: Respect the codomyrmex layer architecture for imports.
5. **Test Coverage**: Every new integration gets both a unit test and an integration test.

## Agent Workflows

| Task | Entry Point | Details |
| :--- | :--- | :--- |
| Run analysis | `uv run python run_demo.py` | Full demo: analyze → visualize → report → pipeline |
| Run tests | `uv run pytest tests/ -v` | 60+ tests, all zero-mock |
| Run pipeline only | `uv run python -m src.main --pipeline src/` | DAG-based pipeline execution |

## Navigation Links

- **📁 Parent Directory**: [projects](../README.md) — Parent directory documentation
- **🏠 Project Root**: [../../README.md](../../README.md) — Main project documentation
- **📖 Specification**: [SPEC.md](SPEC.md) — Functional specification
- **🤖 AI Context**: [PAI.md](PAI.md) — Personal AI Infrastructure
