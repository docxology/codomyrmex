# Personal AI Infrastructure - Module Rules Context

**Directory**: `cursorrules/modules/`
**Status**: Active | **Last Updated**: February 2026

## Overview

Module-specific cursor rules that supplement `general.cursorrules`. Contains **60 rules** organized across 7 categories. All rules inherit mandatory policies from `general.cursorrules §2`.

## Statistics

| Category | Count |
|----------|-------|
| Security & Identity | 7 |
| AI & Agents | 7 |
| Infrastructure | 9 |
| Development Tools | 14 |
| Metrics & Testing | 5 |
| Documentation & Build | 5 |
| Operations | 7 |
| Specialized | 6 |
| **Total** | **60** |

## AI Context

When working with module rules:

1. **Priority**: Higher than cross-module and general, lower than file-specific
2. **Convention**: Each module has a matching `.cursorrules` file
3. **Structure**: All follow the standard 8-section template
4. **Dependencies**: All reference `pyproject.toml` for dependency management (uv)
5. **Mandatory Policies**: Zero-Mock, UV-Only, RASP, Python ≥ 3.10 — encoded in every rule

## Key Policies

- **Zero-Mock**: All testing sections mandate real implementations with environment-gated tests
- **UV**: All Key Files sections reference `pyproject.toml` — no `requirements.txt`
- **RASP**: Every module directory needs README, AGENTS, SPEC, PAI
- **Python ≥ 3.10**: Type hints, Google-style docstrings, modern syntax

## Navigation

- **Parent**: [../README.md](../README.md)
- **Agent Guidelines**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
