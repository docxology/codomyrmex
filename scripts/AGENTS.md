# Codomyrmex Agents — scripts

## Purpose

Maintenance and automation utilities for Codomyrmex project management.

## Active Components

### Documentation Management

- `check_docs_status.py` – Check documentation status across the entire repository.
- `documentation_status_summary.py` – Generate comprehensive documentation status summaries.
- `generate_missing_readmes.py` – Generate README.md files for directories with AGENTS.md.

### Code Quality & Maintenance

- `add_logging.py` – Automated logging injection across modules.
- `enhance_documentation.py` – Documentation enhancement and docstring generation.
- `fix_imports_simple.py` – Import statement cleanup and optimization.
- `fix_imports.py` – Advanced import management and dependency resolution.
- `fix_syntax_errors.py` – Syntax error detection and automated repair.

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints

- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
