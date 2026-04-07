# Codomyrmex — `src/codomyrmex/tests/unit`

**Status**: Active | **Last updated**: April 2026

## Purpose

Pytest suite for production code under `src/codomyrmex/`. See [SPEC.md](SPEC.md) for zero-mock rules, markers, and coverage gates.

## Layout

| Location | Role |
|----------|------|
| `<module>/` | Primary home for tests targeting `codomyrmex.<module>` (e.g. `cerebrum/`, `cloud/`, `agentic_memory/`). |
| `hermes/` | Hermes client, session, templates, provider router, monitoring, gateway, and related unit tests. |
| `agents/hermes/` | MCP tool entrypoints and Hermes CLI orchestration. |
| `agents/test_agents_hermes_client.py` | `HermesClient` argument-building and execution paths (complements `hermes/test_hermes_client.py`). |
| Unit root | Cross-package smoke, milestone releases, and shared infra (see below). |

### Root-only files (not misplaced)

- `conftest.py` — shared fixtures (`src_root`, `project_root`, `minimal_project`, `minimal_git_repo`, `ollama_base_url`, `container_registry_url`, `requires_ollama`, `requires_docker`).
- `test_coverage_smoke.py` — import/instantiation sweep for historically low-coverage packages.
- `test_v1_*.py`, `test_v130_foundations.py`, `test_v131_intelligence.py`, `test_v132_execution.py` — release milestone tests (`scripts/maintenance/release_audit.py` still globs `test_dir.glob("test_v1_*.py")` at unit root; no `milestones/` subfolder as of this refresh).
- `test_credential_rotation.py`, `test_rate_limiter.py`, and other small tests that do not map 1:1 to a single module folder.

### Grouped under module trees (hygiene pass)

- `audio/test_vad.py`, `audio/test_audio_streaming.py`
- `vision/test_vision.py`
- `cloud/test_cost_hooks.py`
- `cloud/test_cloud_package_exports.py` (package re-exports; formerly `test_cloud_coverage.py`)
- `cli/test_cli_package_handlers.py` (formerly `test_cli_coverage.py`)
- `collaboration/test_collaboration_package_surface.py`, `config_management/test_config_management_package_surface.py`, `data_visualization/test_data_visualization_package_surface.py`, `documentation/test_documentation_package_surface.py`, `git_operations/test_git_operations_package_surface.py`, `physical_management/test_physical_management_package_surface.py`

### Removed as redundant with deeper per-module tests

- Root `test_agentic_memory_coverage.py`, `test_cerebrum_coverage.py`, `test_cerebrum_deep_coverage.py`, `test_cloud_deep_coverage.py`, and the four `test_generated_*.py` scaffolding files at unit root.

## Dependencies

`uv run pytest`. Optional extras per module — root `pyproject.toml`.

## Development guidelines

- Add new tests under the matching `<module>/` directory.
- Hermes: client/session/templates in `hermes/`; MCP-focused tests in `agents/hermes/`.
- Follow [SPEC.md](SPEC.md): real instances and skips for missing services; see SPEC for monkeypatch policy nuance.

## Navigation

- [README.md](README.md) — how to run subsets.
- [SPEC.md](SPEC.md) — behavioral contract.
- [Parent `tests/`](../README.md)
- [Repository root](../../../../README.md)
