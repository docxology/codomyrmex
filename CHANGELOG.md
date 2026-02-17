# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-02-17

### Added

- `EphemeralServer` utility for local HTTP testing (`tests/utils/ephemeral_server.py`)
- `pytest-benchmark` baselines for import time and AST parsing
- Benchmarks test suite (`tests/benchmarks/test_benchmarks.py`)

### Changed

- Networking tests now use local `EphemeralServer` instead of external `httpbin.org`
- Bumped version to 0.1.4 in `pyproject.toml` and `__init__.py`
- Updated roadmap: v0.1.5–7 focus on modularity/testing/orchestration, v0.1.8–9 cognitive, v0.2.0 stable swarm

## [0.1.2] - 2026-02-17

### Added

- MCP HTTP transport with FastAPI server and 33 registered tools
- Web UI for interactive MCP tool testing (`http://localhost:8080/`)
- Health, tools, resources, and prompts HTTP endpoints
- 30 unit tests for MCP HTTP server
- Website live dashboard with auto-refresh and MCP integration card
- `scripts/update_pai_docs.py` — batch PAI.md updater for all modules
- `scripts/update_root_docs.py`, `scripts/update_spec_md.py` — root doc automation
- `scripts/finalize_root_docs.py` — documentation finalization tooling
- Comprehensive GitHub workflow suite for CI/CD
- Documentation validation and remediation scripts
- Pre-commit hook configuration
- Security scanning workflows
- RASP documentation pattern (README, AGENTS, SPEC, PAI) defined across all 78 modules
- PAI integration documentation suite (`docs/pai/`)
- Skills documentation suite (`docs/skills/`)
- UOR (Universal Object Reference) module with PrismEngine, EntityManager, UORGraph
- Model evaluation metrics module (`model_ops/evaluation/metrics.py`)
- Data visualization modules: bar charts, line plots, components, reports
- Claude integration tests (`test_claude_integration.py`)
- UOR comprehensive test suite (`test_uor.py`)
- Backward-compatibility shims for cerebrum visualization and agents education

### Changed

- Migrated dependency management to UV
- Standardized test paths to `src/codomyrmex/tests/`
- Unified tests: migrated root `/tests/` to `src/codomyrmex/tests/unit/`
- PAI.md files for all 78 modules now include accurate exports from `__init__.py`, algorithm phase mapping, and navigation
- Root PAI.md rewritten as actual PAI system bridge documentation (v0.2.0)
- Agent system documentation expanded with provider comparison and three-tier agent architecture
- Standardized module count to 78 across all root documentation
- Test coverage target standardized to ≥80% across all documentation
- PAI bridge, trust gateway, and MCP bridge improved
- Rate limiter enhanced with `consume()` method and `initial_tokens` parameter
- Skills, security governance, and telemetry module exports refined

### Fixed

- Resolved all ruff linting errors across test files and analyzer modules
- Workflow test paths now correctly reference `src/codomyrmex/tests/unit/`
- Workflow-status filename mapping now correctly maps workflow names to filenames
- Module count inconsistencies resolved (was 94/95/105/106 in different docs, now consistently 104)
- Fixed `test_curriculum` calling convention (keyword-only args)
- Fixed `test_documentation_accuracy` to use actual API signatures for `create_line_plot`, `pyrefly_runner`, MCP schemas, visualization charts, and build orchestrator
- Fixed `test_analysis_security_cicd` to handle dataclass return types from `analyze_file` and `scan_vulnerabilities`
- Fixed `test_real_github_repos` helper function incorrectly collected as pytest test
- Version string in `src/__init__.py` updated from stale `0.1.0` to `0.1.2`
- Removed stale `deep_audit.py` and `polish_exports.py`

## [0.1.0] - 2026-02-05

### Added

- Initial project structure
- Core module framework
- Basic documentation with README.md and AGENTS.md patterns
- GitHub workflow templates
