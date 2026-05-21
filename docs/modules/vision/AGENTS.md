# Vision Module — Agent Coordination

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Docs path**: `docs/modules/vision`
- **Source path**: [../../../src/codomyrmex/vision/](../../../src/codomyrmex/vision/)
- **Human overview**: [README.md](README.md)
- **Functional spec**: [SPEC.md](SPEC.md)
- **Repository agents**: [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Coordinate documentation and review work for visual document processing. The source package owns extraction logic, VLM integration, and result models; this docs folder provides the module-level map.

## Operating Contracts

- Keep provider-specific behavior isolated in `vlm_client.py` or a provider adapter rather than spreading it across extraction modules.
- Keep data-shape changes synchronized with [../../../src/codomyrmex/vision/API_SPECIFICATION.md](../../../src/codomyrmex/vision/API_SPECIFICATION.md).
- Prefer deterministic fixtures for annotation/PDF extraction tests; record provider assumptions when VLM calls are involved.

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Readme**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Source AGENTS**: [../../../src/codomyrmex/vision/AGENTS.md](../../../src/codomyrmex/vision/AGENTS.md)
