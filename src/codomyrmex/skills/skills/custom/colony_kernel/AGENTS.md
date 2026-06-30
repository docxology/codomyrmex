# AGENTS.md — src/codomyrmex/skills/skills/custom/colony_kernel

> Technical reference for AI agents and contributors working in this skill directory.

## Purpose

Holds the Colony Kernel custom skill definition — the machine-readable and prose description of how agents should load, invoke, and extend the Colony Kernel's 8 MCP tools.

## Key Files

| File | Purpose |
|------|---------|
| `skill.yaml` | Skill entry point: id, version, layer, owned capabilities, trigger phrases, agent identity prompt, inline patterns, anti-patterns, and handoff routes |
| `patterns.md` | Proven usage patterns for the colony control plane, with annotated code examples and Mermaid sequence diagrams |
| `anti-patterns.md` | Common misuse patterns (skipping `record_outcome`, ignoring HOLD, manual role assignment) with explanations and corrective guidance |
| `decisions.md` | Design decisions for the skill itself: why these trigger phrases, why this identity prompt, tradeoffs in the handoff routing |
| `validations.yaml` | Validation rules that verify a skill invocation is complete before execution: required fields, trust thresholds, MCP tool availability checks |
| `sharp-edges.yaml` | Known pitfalls with mitigations: budget underestimation, SANDBOX bypass attempts, stale pheromone misread |
| `collaboration.yaml` | Collaboration graph: which other skills this skill pairs with (`agentic-memory`, `model-context-protocol`, `orchestrator`) and how handoffs are initiated |

## Conventions

- `skill.yaml` is the authoritative entry point. All other files in this directory are referenced from it.
- Trigger phrases in `skill.yaml` must remain in sync with the `triggers:` list in any parent skill index. Do not add trigger phrases that overlap with unrelated skills.
- `patterns.md` and `anti-patterns.md` use the same YAML-headed structure as `skill.yaml` for machine parsing, but include prose-and-code examples for human readers.
- `validations.yaml` rules apply at invocation time. Rules that require a live MCP server connection are marked `requires_mcp: true` and skipped in dry-run mode.
- Updates to `sharp-edges.yaml` must include a `mitigation` field — bare problem statements without mitigations are not accepted.
- This directory does not contain Python source. Source lives in `src/codomyrmex/colony_kernel/`.

## Invariants

- `skill.yaml` version must be bumped (semver patch) whenever trigger phrases, the identity prompt, or handoff routes change.
- `collaboration.yaml` entries must reference skills that exist in `src/codomyrmex/skills/skills/` — no forward-references to unimplemented skills.
- `validations.yaml` must have at least one rule that verifies the Colony Kernel MCP server is reachable before write-path invocations.

## Navigation

- **Source**: [../../../../colony_kernel/](../../../../colony_kernel/)
- **Module docs**: [../../../../../../docs/modules/colony_kernel/](../../../../../../docs/modules/colony_kernel/)
- **Scope document**: [../../../../../../docs/todo/COLONY_KERNEL.md](../../../../../../docs/todo/COLONY_KERNEL.md)
- **Skills index**: [../](../)
