# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- RASP documentation pattern (README, AGENTS, SPEC, PAI) defined across all 104 modules

### Changed

- Migrated dependency management to UV
- Standardized test paths to `src/codomyrmex/tests/`
- Unified tests: migrated root `/tests/` to `src/codomyrmex/tests/unit/`
- PAI.md files for all 104 modules now include accurate exports from `__init__.py`, algorithm phase mapping, and navigation
- Root PAI.md rewritten as actual PAI system bridge documentation (v0.2.0)
- Agent system documentation expanded with provider comparison and three-tier agent architecture
- Standardized module count to 104 across all root documentation
- Test coverage target standardized to ≥80% across all documentation

### Fixed

- Resolved all ruff linting errors across test files and analyzer modules
- Workflow test paths now correctly reference `src/codomyrmex/tests/unit/`
- Workflow-status filename mapping now correctly maps workflow names to filenames
- Module count inconsistencies resolved (was 94/95/105/106 in different docs, now consistently 104)

## [0.1.0] - 2026-02-05

### Added

- Initial project structure
- Core module framework
- Basic documentation with README.md and AGENTS.md patterns
- GitHub workflow templates
