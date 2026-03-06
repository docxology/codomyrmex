# Documentation Scripts -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Scripts for documentation generation, maintenance, and quality improvement including docstring fixers, architecture diagram generation, and spec file updates.

## Scripts Available

- **fix_missing_docstrings.py**: Prepends placeholder docstrings to __init__.py files missing them
- **generate_architecture_diagram.py**: Auto-generates Mermaid architecture diagrams from static import analysis
- **remediate_documentation.py**: Remediates documentation quality issues identified by audit scripts
- **update_root_docs.py**: Updates root-level documentation files with current module information
- **update_spec_md.py**: Updates SPEC.md files across modules with current API specifications


## Agent Instructions

1. Run scripts from the repository root directory using `uv run python scripts/docs/<script>`
2. Ensure prerequisites are installed: `uv sync`
3. Scripts are demonstration/utility tools and do not modify production state

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md)
