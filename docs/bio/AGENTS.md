# Bio-Inspired Design — Agent Coordination

**Section**: `docs/bio` | **Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Bio-inspired design documentation drawing precise structural parallels between ant colony behavior, cognitive science, and the software architecture patterns used in Codomyrmex. These essays are the theoretical substrate underlying the platform's multi-agent coordination philosophy.

## Key Capabilities

- **Stigmergic coordination models** — Event-driven pub/sub as computational pheromone trails (see [stigmergy.md](./stigmergy.md))
- **Eusocial role assignment** — Agent specialization via response-threshold dynamics (see [eusociality.md](./eusociality.md))
- **Swarm intelligence patterns** — Quorum sensing, ACO, flocking for collective decisions (see [swarm_intelligence.md](./swarm_intelligence.md))
- **Active inference agents** — Free energy minimization as agent action policy (see [free_energy.md](./free_energy.md))
- **Immune defense models** — Self/non-self discrimination, danger signals, layered defense (see [immune_system.md](./immune_system.md))
- **Adaptive memory** — Forgetting as feature, multi-store architecture (see [memory_and_forgetting.md](./memory_and_forgetting.md))

## Agent Usage Patterns

Agents interacting with Codomyrmex should use these documents as **design heuristics**:

| When Designing... | Consult... | Because... |
|-------------------|-----------|------------|
| Multi-agent task allocation | [eusociality.md](./eusociality.md) | Response-threshold model avoids central authority |
| Event-based coordination | [stigmergy.md](./stigmergy.md) | Indirect communication via shared environment |
| System-wide health monitoring | [superorganism.md](./superorganism.md) | Colony-level metrics reveal emergent pathologies |
| Security architecture | [immune_system.md](./immune_system.md) | Layered defense with danger-signal detection |
| Cache/memory strategy | [memory_and_forgetting.md](./memory_and_forgetting.md) | Forgetting optimizes retrieval relevance |
| Predictive monitoring | [free_energy.md](./free_energy.md) | Active inference preempts reactive correction |
| Plugin/integration design | [symbiosis.md](./symbiosis.md) | Holobiont model for composite system boundaries |

## Integration Points

- **Docs**: [README.md](README.md) — Series overview and reading order
- **Bio Simulation**: [../modules/bio_simulation/](../modules/bio_simulation/) — Computational ant colony models
- **Embodiment**: [../modules/embodiment/](../modules/embodiment/) — Sensor/actuator bridge (ROS2)
- **Agents**: [../modules/agents/](../modules/agents/) — Multi-agent framework integration
- **SPEC**: [SPEC.md](SPEC.md) — Formal biological-software analogies

## Testing Guidelines

Bio documentation is reference-only; no executable tests. However, the architectural mappings herein should be validated against the modules they reference — if a mapping claims a module implements a pattern, the module's tests should exercise that pattern.
