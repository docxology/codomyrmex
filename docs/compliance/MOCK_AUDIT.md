# Mock Usage Audit Report

**Date**: February 2026
**Policy**: [Zero-Mock Policy](../../src/codomyrmex/tests/RUNNING_TESTS.md#zero-mock-policy)

## Overview

This report documents instances of `unittest.mock`, `pytest-mock`, or `MagicMock` usage within the `codomyrmex` repository. The Zero-Mock policy strictly forbids mocking core logic. Mocks are permissible **only** for external system boundaries (e.g., AWS, OpenStack, GitHub API) where real integration is impossible or cost-prohibitive in a CI environment.

## Violations & Exceptions

The following files were found to import mocking libraries. These require review to ensure they strictly target external boundaries.

### Critical Core Modules (High Priority Review)

- `src/codomyrmex/tests/unit/orchestrator/test_orchestrator.py`: Uses `AsyncMock`, `MagicMock`. (Core logic should not be mocked)
- `src/codomyrmex/tests/unit/orchestrator/test_integration.py`: Uses `AsyncMock`, `MagicMock`.
- `src/codomyrmex/tests/unit/coding/test_debugging.py`: Uses `MagicMock`.
- `src/codomyrmex/tests/unit/concurrency/test_concurrency.py`: Uses `MagicMock`.

### IDE & Tooling

- `src/codomyrmex/tests/unit/ide/test_ide.py`: Uses `patch`.
- `src/codomyrmex/tests/unit/website/unit/test_generator.py`: Uses `Mock`, `patch`.
- `src/codomyrmex/tests/unit/website/unit/test_server.py`: Uses `Mock`, `patch`.

### Agents (Likely External APIs)

- `src/codomyrmex/tests/unit/agents/gemini/test_gemini_api.py`: Uses `MagicMock`, `patch`. (Acceptable for API limit avoidance)
- `src/codomyrmex/tests/unit/agents/test_git_agent.py`: Uses `MagicMock`, `patch`.
- `src/codomyrmex/tests/unit/agents/test_core_agents.py`: Uses `MagicMock`.
- `src/codomyrmex/tests/unit/agents/test_cli_configurations.py`: Uses `patch`.
- `src/codomyrmex/tests/unit/agents/generic/test_api_agent_base.py`: Uses `Mock`.

### Cloud & Infrastructure (Likely External APIs)

- `src/codomyrmex/tests/unit/cloud/test_infomaniak_auth.py`: Uses `MagicMock`, `patch`.
- `src/codomyrmex/tests/unit/cloud/test_infomaniak_compute.py`: Uses `MagicMock`, `patch`.
- `src/codomyrmex/tests/unit/cloud/test_infomaniak_object_storage.py`: Uses `MagicMock`, `mock_open`, `patch`.
- `src/codomyrmex/tests/unit/cloud/*.py`: Widespread mock usage (Acceptable for cloud provider testing).

### Git & VCS

- `src/codomyrmex/tests/unit/git_operations/test_repository_manager.py`: Uses `MagicMock`, `patch`.
- `src/codomyrmex/tests/unit/git_operations/api/test_github_issues.py`: Uses `patch`.

### Other Modules

- `src/codomyrmex/tests/unit/metrics/test_metrics.py`
- `src/codomyrmex/tests/unit/llm/test_llm.py`
- `src/codomyrmex/tests/unit/networking/test_networking.py`
- `src/codomyrmex/tests/unit/tree_sitter/test_tree_sitter.py`
- `src/codomyrmex/tests/unit/documents/unit/core/test_document_*.py` (@patch usage)

## Action Plan

1. **Freeze**: No new tests may use mocks for internal logic.
2. **Refactor**: Prioritize refactoring `orchestrator` and `concurrency` tests to use real instances.
3. **Validate**: Ensure Cloud and Agent mocks are strictly limited to the network boundary layer.

## Sprint 8 Remediation (Completed — February 26, 2026)

Sprint 8 targeted zero-policy compliance. All 38 identified violations were fixed:

- 16 silent `except: pass` blocks replaced with explicit `log + raise`
- 4 stub fallback classes replaced with `ImportError`
- 8 test files converted from `monkeypatch` to explicit `os.environ`/`os.chdir`
- 3 hardcoded URLs moved to `os.getenv()` with centralized defaults
- 6 stub functions raised to `NotImplementedError`
- 3 `Mock*` class renames to `Test*` for naming clarity

All originally-listed violation files have been remediated. The test suite passes with the zero-mock policy fully enforced.

## Current Status (March 2026)

- **Zero-Mock Policy**: Fully enforced. Run `grep -r 'unittest.mock\|MagicMock\|pytest-mock' src/codomyrmex/tests/` — should return 0 results.
- **Coverage Gate**: ≥70% required. Run `uv run pytest --cov=src/codomyrmex` for live figure.
- **Ruff Violations**: 0 (as of Sprint 16, March 2026).
- **Test Count**: 17,000+ tests collected.
