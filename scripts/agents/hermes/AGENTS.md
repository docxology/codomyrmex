# Codomyrmex Agents — scripts/agents/hermes

**Version**: v3.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Thin orchestrators and automation utilities for the Hermes Agent.

These scripts are lightweight wrappers combining the core `HermesClient` with system-wide configuration (`config/agents/hermes.yaml`) to produce structured execution logs and interpretability views — with zero business logic overhead.

## Active Components

| Script | Purpose | Key Helpers |
| --- | --- | --- |
| **`setup_hermes.py`** | Pre-flight environment check | `_check_imports()`, `_check_config()`, `_check_backends()`, `_check_session_storage()` |
| **`run_hermes.py`** | Submit a real prompt to Hermes | `_load_hermes_client()`, `_print_client_info()`, `_execute_prompt()` |
| **`observe_hermes.py`** | View recent session history from SQLite | `_print_session()` |
| **`evaluate_orchestrators.py`** | AI-powered thin-orchestrator code review | `run_script()`, `assess_script()`, `extract_json_from_response()` |
| **`dispatch_hermes.py`** | Sweep eval JSONs → dispatch improvements | `_load_eval_results()`, `_build_dispatch_prompt()`, `_dispatch_hermes()`, `_dispatch_shell()` |

## Operating Contracts

1. **Thin Execution**: These scripts perform zero core business logic. They ingest config, instantiate clients, call client methods, and log output.
2. **Configuration Adherence**: All defaults (model, backend, DB paths) derive from `config/agents/hermes.yaml`.
3. **Session Awareness**: `run_hermes.py` uses the persistence layer (`HermesClient.chat_session`) by default.
4. **Modular Helpers**: Each `main()` function is a clean orchestration loop — every meaningful operation is delegated to a named helper function.
5. **Consistent Import Bootstrap**: All scripts use `try: from codomyrmex … except ImportError: sys.path.insert(…)` — not a bare `import codomyrmex` probe.

## Navigation Links

- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
- **🧪 Tests**: [test_hermes_orchestrators.py](../../../../src/codomyrmex/tests/unit/agents/test_hermes_orchestrators.py)
