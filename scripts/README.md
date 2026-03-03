# Scripts Directory

Utility, demo, and module-specific scripts for Codomyrmex development and operations.

## Structure

| Directory | Purpose |
|:---|:---|
| `audits/` | Codebase audits: documentation, exports, imports, RASP compliance |
| `demos/` | Module demos: defense, identity, market, privacy, wallet |
| `docs/` | Documentation tooling: docstring fixes, architecture diagrams, root doc updates |
| `pai/` | PAI integration: docs, skill updates, validation |
| `performance/` | Benchmarks and mutation testing |
| `verification/` | Phase verification scripts (phase 1–3, secure agent system) |
| `website/` | Dashboard and website utilities |
| `agents/` | Agent subsystem examples and utilities |
| `llm/` | LLM provider examples (OpenRouter, Ollama, streaming) |
| `maintenance/` | Maintenance and housekeeping utilities |
| `<module>/` | Per-module example scripts (one dir per `src/codomyrmex/` module) |

## Root Files

| File | Purpose |
|:---|:---|
| `run_all_scripts.py` | Master orchestrator — discovers and runs scripts |
| `config.yaml` | Shared script configuration |
| `__init__.py` | Package marker |

## Quick Start

```bash
# Run a specific audit
uv run python scripts/audits/audit_rasp.py

# Run a demo
uv run python scripts/demos/demo_wallet.py

# Run all scripts
uv run python scripts/run_all_scripts.py

# Launch the dashboard
uv run python scripts/website/launch_dashboard.py
```
