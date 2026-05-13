# Hermes documentation assets


**Version**: v0.1.0 | **Status**: Active | **Last Updated**: May 2026

Static files for the Hermes doc suite (diagram sources, exported PNG/SVG, screenshots).

## Navigation

- **Hermes docs index**: [../README.md](../README.md)
- **Architecture diagrams (Mermaid)**: defined inline in [../architecture.md](../architecture.md), [../gateway.md](../gateway.md), [../sessions.md](../sessions.md), [../codomyrmex_integration.md](../codomyrmex_integration.md)
- **Codomyrmex skill preload spec**: [../skills.md](../skills.md)

Add exported renders here only when a maintainer workflow requires a non-Mermaid artifact; prefer keeping diagrams as fenced `mermaid` blocks in the Markdown sources so they stay versioned with the text.

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.
