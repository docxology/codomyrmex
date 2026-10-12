# Changelog for Documentation

All notable changes to this module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Package-wide README/AGENTS auditing with portable receipts.
- Fail-closed module enrichment and placeholder-repair CLIs.
- Dry-run-first MCP PAI generation with content hashes and execution receipts.
- Real missing-file counts for MCP RASP compliance results.
- Initial Docusaurus setup (`docusaurus.config.js`, `sidebars.js`, `package.json`).
- `documentation_website.py` script for managing Docusaurus lifecycle (checkenv, install, start, build, serve, assess).
- `MCP_TOOL_SPECIFICATION.md` defining `trigger_documentation_build` and `check_documentation_environment` tools.
- Basic `README.md` for the documentation module.
- Created comprehensive API specification for documentation functions.
- Implemented security guidelines for documentation operations.
- Added usage examples for common documentation workflows.
- Initial directory structure including `docs/`, `src/css/`, `static/img/`.
- Example tutorial `docs/modules/documentation/docs/tutorials/example_tutorial.md` (now named "Adding a New Module to Documentation").

### Changed

- The repository's authoritative reader-facing build is strict MkDocs;
  package-local Docusaurus helpers remain available but are not the release
  documentation gate.
- `generate_module_docs` now validates a single top-level package name, defaults
  to `dry_run=True`, and accurately reports its PAI-only scope.
- Enhanced README.md with detailed Docusaurus setup instructions and usage examples.
- Refined `API_SPECIFICATION.md` with context for CLI/MCP tools and conceptual Python API.
- Implemented comprehensive security guidelines for documentation operations and access control.
- Added comprehensive usage examples for documentation website management and automation.

### Fixed

- Rejected traversal-shaped documentation MCP module names.
- Removed stale public examples with nonexistent signatures and corrected the
  `audit_rasp()` exit-code contract.

## Navigation

- [Module overview](README.md)
- [Repository changelog](../../../CHANGELOG.md)
