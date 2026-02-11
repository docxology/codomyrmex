# Personal AI Infrastructure - File-Specific Rules Context

**Directory**: `cursorrules/file-specific/`
**Status**: Active | **Last Updated**: February 2026

## Overview

File-type specific cursor rules with the **highest priority** in the rule hierarchy. Contains **6 rules** for specific file patterns. Mandatory policies (Zero-Mock, UV, RASP, Python ≥ 3.10) apply to all file types.

## Statistics

| Category | Count |
|----------|-------|
| File-specific rules | 6 |

## AI Context

When working with file-specific rules:

1. **Highest Priority**: These rules override all other rule categories
2. **File Types**: Python, YAML, JSON, README.md, SPEC, CHANGELOG
3. **Scope**: Applied based on the file type being edited
4. **Mandatory Policies**: Zero-Mock, UV-Only, RASP, Python ≥ 3.10 apply unconditionally

## Key Policies

- **Zero-Mock**: Python test files must use real implementations — no mocks
- **UV**: Python files use `uv run pytest` and reference `pyproject.toml`
- **RASP**: README.md and SPEC must follow RASP documentation patterns

## Key Files

- `python.cursorrules`: Python coding standards (PEP 8, type hints, docstrings)
- `yaml.cursorrules`: YAML formatting rules (2-space indent, schema validation)
- `json.cursorrules`: JSON structure rules (2-space indent, valid schema)
- `README.md.cursorrules`: README documentation rules (RASP compliance)
- `SPEC.cursorrules`: Specification file rules (Mermaid diagrams)
- `CHANGELOG.cursorrules`: Changelog formatting rules (Keep a Changelog)

## Navigation

- **Parent**: [../README.md](../README.md)
- **Agent Guidelines**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
