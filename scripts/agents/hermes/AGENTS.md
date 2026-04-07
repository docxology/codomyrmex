# Codomyrmex Agents — scripts/agents/hermes

**Version**: v3.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Thin orchestrators and automation utilities for the Hermes Agent, aligned with **Hermes Agent v0.2.0** (v2026.3.12).

These scripts are lightweight wrappers combining the core `HermesClient` with system-wide configuration (`config/agents/hermes.yaml`) to produce structured execution logs and interpretability views — with zero business logic overhead.

## Active Components

| Script | Purpose | Key Helpers |
| --- | --- | --- |
| **`setup_hermes.py`** | Pre-flight environment check | `_check_imports()`, `_check_config()`, `_check_backends()`, `_check_session_storage()`, `_check_hermes_version()`, `_check_hermes_doctor()` |
| **`run_hermes.py`** | Submit a real prompt to Hermes | `_load_hermes_client()`, `_print_client_info()`, `_execute_prompt()`, `_format_response()` |
| **`observe_hermes.py`** | View/search session history from SQLite | `_print_session()`, `_load_sorted_sessions()`, `_resolve_db_path()` |
| **`evaluate_orchestrators.py`** | AI-powered thin-orchestrator code review | `run_script()`, `assess_script()`, `extract_json_from_response()` |
| **`dispatch_hermes.py`** | Sweep eval JSONs → dispatch improvements | `_load_eval_results()`, `_build_dispatch_prompt()`, `_dispatch_hermes()`, `_dispatch_shell()` |

## v0.2.0 Alignment

- **Version detection**: `setup_hermes.py` detects CLI version and reports v0.2.0+ feature availability
- **`hermes doctor`**: Runs comprehensive health diagnostics during setup
- **Named sessions**: `run_hermes.py --name "task-name"` creates or resumes by name
- **Quiet mode**: `run_hermes.py --quiet/-Q` for CI/CD pipelines (raw output only)
- **Session search**: `observe_hermes.py --search "query"` filters by name substring
- **Schema migration**: SQLite store auto-migrates pre-v0.2.0 databases (adds `name` column)

## Operating Contracts

1. **Thin Execution**: These scripts perform zero core business logic. They ingest config, instantiate clients, call client methods, and log output.
2. **Configuration Adherence**: All defaults (model, backend, DB paths) derive from `config/agents/hermes.yaml`.
3. **Session Awareness**: `run_hermes.py` uses the persistence layer (`HermesClient.chat_session`) by default.
4. **Modular Helpers**: Each `main()` function is a clean orchestration loop — every meaningful operation is delegated to a named helper function.
5. **Consistent Import Bootstrap**: All scripts use `try: from codomyrmex … except ImportError: sys.path.insert(…)` — not a bare `import codomyrmex` probe.

## Navigation Links

- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../README.md](../../../README.md) - Main project documentation
- **🧪 Tests**: [test_hermes_orchestrators.py](../../../src/codomyrmex/tests/unit/agents/test_hermes_orchestrators.py)
