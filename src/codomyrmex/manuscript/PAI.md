# Personal AI Infrastructure - Manuscript Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The manuscript module gives PAI-driven workflows a tested, importable path to
compute manuscript token variables and regenerate publication figures without
shelling out to ad-hoc scripts.

## PAI Capabilities

| Capability | Purpose |
| :--- | :--- |
| Token computation | Derive manuscript variables from live repository state |
| Variable injection | Feed computed variables into the manuscript build pipeline |
| Figure generation | Regenerate every publication figure deterministically |

## Key Exports

| Export | Type | Purpose |
| :--- | :--- | :--- |
| `compute_variables` | Function | Compute manuscript token variables |
| `inject_via_infrastructure` | Function | Inject variables into the manuscript build |
| `figures.main` | Function | Run all figure generators |
| `figures.FIGURES` | Registry | Enumerate available figure generators |

## PAI Algorithm Phase Mapping

| Phase | Manuscript Contribution |
| :--- | :--- |
| **EXECUTE** | Recompute token variables and figures after source changes |
| **VERIFY** | Confirm manuscript claims match live repository state |

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Module README**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
