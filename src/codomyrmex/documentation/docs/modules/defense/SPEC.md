# Defense -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

- Detect configured prompt-exploit substrings and classify them as `ThreatLevel` values.
- Maintain exploit and honeytoken metrics through `ActiveDefense`.
- Create, list, and detect honeytokens with `HT-` identifiers.
- Process requests through containment, blocklist, rate-limit, custom-rule, and cognitive-exploit checks.
- Engage rabbit-hole containment for high-risk cognitive exploit attempts.
- Expose MCP wrappers for exploit detection, request processing, and threat reporting.

## Non-Functional Requirements

- Tests use real local instances and follow the zero-mock policy.
- Runtime behavior is in-process and deterministic except for honeytoken IDs and poison phrase sampling.
- Compatibility imports through `codomyrmex.defense` and `codomyrmex.security.ai_safety` remain supported.

## Navigation

- **Source**: [../../../../defense/README.md](../../../../defense/README.md)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.
