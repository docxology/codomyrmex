# Documentation Scripts Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Scripts for documentation generation, maintenance, and quality improvement including docstring fixers, architecture diagram generation, and spec file updates.

## Functional Requirements

- **fix_missing_docstrings.py**: Prepends placeholder docstrings to __init__.py files missing them
- **generate_architecture_diagram.py**: Auto-generates Mermaid architecture diagrams from static import analysis
- **remediate_documentation.py**: Remediates documentation quality issues identified by audit scripts
- **update_root_docs.py**: Updates root-level documentation files with current module information
- **update_spec_md.py**: Updates SPEC.md files across modules with current API specifications


## Execution

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/docs/generate_architecture_diagram.py
```

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
