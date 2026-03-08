# Personal AI Infrastructure — Scripts Context

**Module**: scripts
**Version**: v1.1.9
**Status**: Active

## Context

The `scripts/` directory contains **thin orchestrators only** — entry-point wrappers that import and invoke business logic from `src/codomyrmex/` modules. No substantial logic, data models, or core functionality exists here.

## Thin Orchestrator Principle

> [!IMPORTANT]
> All logic MUST live in `src/codomyrmex/`. Scripts are just CLI wrappers.

| What Goes Here | What Goes in `src/codomyrmex/` |
|----------------|-------------------------------|
| CLI argument parsing | Business logic |
| Environment setup (`sys.path`) | Data models |
| Config file loading | API implementations |
| Dashboard launch commands | Server code, route handlers |
| Audit/test runners | Validation, analysis, generation |

## Key Scripts → Source Mappings

| Script | Imports From |
|--------|-------------|
| `scripts/pai/dashboard.py` | `codomyrmex.agents.pai.pm.server` |
| `scripts/pai/generate_skills.py` | `codomyrmex.skills.skill_generator` |
| `scripts/pai/update_pai_skill.py` | `codomyrmex.skills.skill_updater` |
| `scripts/pai/validate_pai_integration.py` | `codomyrmex.agents.pai.pai_bridge` |
| `scripts/website/launch_dashboard.py` | `codomyrmex.website.server` |

## AI Strategy

As an AI agent working with this module:

1. **Never add logic here** — import from `src/codomyrmex/` instead
2. **Thin wrappers**: Each script should be ≤50 lines (parse args → import → call → exit)
3. **Error handling**: Wrap external calls in try/except and log using `logging_monitoring`
4. **Testing**: Tests live in `src/codomyrmex/tests/`, not alongside scripts

## Key Files

- `__init__.py`: Package marker with thin orchestrator docstring
- `SPEC.md`: Technical specification for the orchestrator pattern
- `README.md`: Human-readable directory guide

## Navigation

- **Self**: [PAI.md](PAI.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **README**: [README.md](README.md)
- **Source Code**: [../src/codomyrmex/](../src/codomyrmex/)
- **PAI Docs**: [../docs/pai/](../docs/pai/)
