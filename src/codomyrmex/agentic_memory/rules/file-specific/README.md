# File-Specific Cursor Rules

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

File-specific rules that take highest priority in the rule hierarchy. These rules apply based on file type and override module-specific and general rules when there's a conflict.

## Rule List (6 rules)

| Rule | Applies To | Key Requirements |
|------|------------|------------------|
| `python.cursorrules` | `*.py` files | PEP 8, type hints, docstrings |
| `yaml.cursorrules` | `*.yaml`, `*.yml` files | Schema validation, 2-space indent |
| `json.cursorrules` | `*.json` files | Schema validation, 2-space indent |
| `CHANGELOG.cursorrules` | `CHANGELOG.md` | Keep a Changelog format |
| `SPEC.cursorrules` | `SPEC.md` | Mermaid diagrams, sections |
| `README.md.cursorrules` | `README.md` | RASP compliance, navigation |

## Rule Hierarchy (Highest Priority)

```
file-specific/ ← You are here (highest priority, 6 rules)
    ↓
modules/ (60 rules)
    ↓
cross-module/ (8 rules)
    ↓
general.cursorrules (lowest priority)
```

## Usage

When editing a file, check if a file-specific rule applies:

| File | Rule Applied |
|------|--------------|
| `src/module/utils.py` | `python.cursorrules` |
| `config/settings.yaml` | `yaml.cursorrules` |
| `package.json` | `json.cursorrules` |
| `CHANGELOG.md` | `CHANGELOG.cursorrules` |
| `module/SPEC.md` | `SPEC.cursorrules` |
| `module/README.md` | `README.md.cursorrules` |

## Quick Reference

### Python Standards

- PEP 8 compliance
- Type hints on all functions
- Google-style docstrings
- ≥80% test coverage

### YAML/JSON Standards

- 2-space indentation
- Schema validation where available
- Comments for complex configurations (YAML only)

### Documentation Standards

- RASP pattern (README, AGENTS, SPEC, PAI)
- Keep a Changelog format for CHANGELOGs
- Mermaid diagrams in SPECs

## Companion Files

- [**AGENTS.md**](AGENTS.md) - Agent guidelines for file-specific work
- [**SPEC.md**](SPEC.md) - Functional specification
- [**PAI.md**](PAI.md) - AI infrastructure context

## Navigation

- **Parent**: [../README.md](../README.md)
- **Module Rules**: [../modules/](../modules/)
- **Cross-Module**: [../cross-module/](../cross-module/)
- **Project Root**: [../../README.md](../../README.md)
