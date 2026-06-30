# colony_kernel skill

> Custom skill definition for the Colony Kernel — teaches agents how to govern actions through the Codomyrmex artificial ecology control plane.

## Overview

This directory contains the machine-readable and prose skill definition for the Colony Kernel. It is consumed by the Codomyrmex skills system to expose the Colony Kernel's 8 MCP tools to AI agents with appropriate trigger phrases, identity context, usage patterns, and anti-pattern warnings.

The skill wraps the Colony Kernel source module (`src/codomyrmex/colony_kernel/`) and does not contain Python code. Its job is to describe — for an AI agent loading this skill — how to propose actions, record outcomes, query pheromones, evaluate plans, and interpret gate verdicts.

## Key Files

| File | Role |
|------|------|
| `skill.yaml` | Entry point: id, version, trigger phrases, agent identity prompt, inline patterns, anti-patterns, handoff routes |
| `patterns.md` | Canonical usage patterns with annotated examples (propose→gate→record→tick, pre-flight falsification, trust-aware dispatch) |
| `anti-patterns.md` | Misuse patterns to avoid: skipping `record_outcome`, ignoring HOLD, manual role assignment |
| `decisions.md` | Design rationale for skill-level choices |
| `validations.yaml` | Pre-invocation validation rules |
| `sharp-edges.yaml` | Known pitfalls with mitigations |
| `collaboration.yaml` | Peer skill relationships and handoff routing |

## Integration with the Skills System

When the Codomyrmex skills system scans `src/codomyrmex/skills/skills/custom/`, it loads `skill.yaml` for each subdirectory. The `triggers:` list in `skill.yaml` is matched against agent messages. On match, the `identity:` prompt is injected and the agent is given access to the Colony Kernel MCP tools.

```python
# The skills system loads this skill when a trigger phrase matches:
# "colony kernel", "actuation gate", "colony propose", etc.
# See skill.yaml triggers: list for the full set.

# Agents invoke Colony Kernel tools via MCP:
result = colony_propose_action(
    agent_id="engineer-1",
    action_type="patch_file",
    target="codomyrmex.git_operations.core",
    rationale="Fix off-by-one error in branch name parser",
    rollback_plan="git revert HEAD~1",
    evidence={"test_ids": ["test_slash_in_name"]},
)
# result["decision"] → "execute" | "hold" | "refuse"
```

## Related

- **Source module**: [../../../../colony_kernel/](../../../../colony_kernel/)
- **Module docs**: [../../../../../../docs/modules/colony_kernel/](../../../../../../docs/modules/colony_kernel/)
- **Agent coordination**: [AGENTS.md](AGENTS.md)
