# Colony Kernel — Module Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: June 2026

## Purpose

The Colony Kernel is the control plane for Codomyrmex's artificial ecology thesis. Rather than coordinating agents through centralised command, it models the collective as a colony where:

- **Modules** are organisms with assigned roles, earned trust scores, and finite lifespans
- **Agents** are actors whose behavioral history is encoded in persistent trust profiles
- **The pheromone field** is the colony's shared memory of what works and what breaks

The kernel exposes 8 MCP tools for agent interaction.

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │          ColonyKernel               │
                    │  (top-level integration class)       │
                    └──────────┬──────────────────────────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        │          │           │           │          │
   ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐
   │Pheromone│ │Resource│ │Actu-   │ │Conseq- │ │Role    │
   │Store    │ │Ledger  │ │ation   │ │uence   │ │Adapter │
   │         │ │        │ │Gate    │ │Memory  │ │        │
   └─────────┘ └────────┘ └────────┘ └────────┘ └────────┘
                                         │
                                    ┌────▼────┐
                                    │Pruning  │
                                    │Daemon   │
                                    └─────────┘
```

## Gate Scoring Model

The ActuationGate computes a composite score in [0.0, 1.0]:

```mermaid
flowchart TD
    P["Pheromone Pressure<br/>sense(SUCCESS) - sense(FAILURE) - 0.5×sense(RISK)"]
    R["Rollback Quality<br/>bool(rollback_plan.strip())"]
    T["Trust Component<br/>profile.trust_score"]
    E["Evidence Quality<br/>bool(proposal.evidence)"]
    FP["Falsification Penalty<br/>max severity weight from findings"]

    subgraph scoring["Base Score Calculation"]
        P -->|"× 0.30"| BS["base_score"]
        R -->|"× 0.30"| BS
        T -->|"× 0.25"| BS
        E -->|"× 0.15"| BS
    end

    BS -->|"× (1.0 - falsification_penalty)"| GS["gate_score"]

    GS -->|"≥ 0.75"| EX["EXECUTE"]
    GS -->|"0.50 – 0.74"| HOLD["HOLD"]
    GS -->|"< 0.50"| REF["REFUSE"]

    SANDBOX["SANDBOX role"] -->|"always"| REF
    CRITICAL["CRITICAL finding"] -->|"always"| REF
    BUDGET["Budget exceeded"] -->|"always"| HOLD

    style EX fill:#0f766e,color:#fff
    style HOLD fill:#b45309,color:#fff
    style REF fill:#dc2626,color:#fff
    style GS fill:#1e3a8a,color:#fff
```

Formula:
```
base_score = pressure × 0.30 + rollback × 0.30 + trust × 0.25 + evidence × 0.15
gate_score = base_score × (1.0 - falsification_penalty)
```

## Trust Lifecycle

```mermaid
stateDiagram-v2
    [*] --> SANDBOX : agent registered<br/>(trust = 0.1)

    SANDBOX --> REPAIR_ANT : trust ≥ 0.20<br/>AND proposals ≥ 3
    REPAIR_ANT --> MEMORY_ANT : trust ≥ 0.35
    MEMORY_ANT --> DISPATCHER : trust ≥ 0.50
    DISPATCHER --> GUARD_ANT : trust ≥ 0.70

    REPAIR_ANT --> SANDBOX : trust < 0.15<br/>(demotion)
    MEMORY_ANT --> REPAIR_ANT : trust < 0.20
    DISPATCHER --> MEMORY_ANT : trust < 0.35
    GUARD_ANT --> DISPATCHER : trust < 0.50

    state SANDBOX {
        [*] --> NoWrite : gate_score = 0.0
        NoWrite --> REFUSE : unconditional
    }

    state REPAIR_ANT {
        [*] --> CanWrite : patch, test, doc
    }

    state GUARD_ANT {
        [*] --> CanVeto : security review<br/>gate audit
    }
```

Delta formula:
```
delta = +0.04  if tests_passed
delta = -0.08  otherwise
delta += -0.05  if repair_needed
delta += human_feedback × 0.03
```

## Pheromone Signal Types

```mermaid
graph LR
    subgraph signals["Signal Taxonomy"]
        FAILURE["FAILURE<br/>decay: NORMAL (1.0)"]
        SUCCESS["SUCCESS<br/>decay: SLOW (0.2)"]
        RISK["RISK<br/>decay: NORMAL (1.0)"]
        NEED["NEED<br/>decay: NORMAL (1.0)"]
        DEPENDENCY["DEPENDENCY<br/>decay: SLOW (0.2)"]
        HUMAN_PRIORITY["HUMAN_PRIORITY<br/>decay: SLOW (0.2)"]
    end

    subgraph sources["Source Trust Multipliers"]
        HUM["HUMAN → ×2.0"]
        TST["TEST → ×1.5"]
        SEC["SECURITY → ×1.3"]
        AGT["AGENT → ×1.0"]
        RNT["RUNTIME → ×1.0"]
    end

    subgraph evaporation["Evaporation Model"]
        FAST["FAST (3.0)<br/>Urgent/transient<br/>Clears in ~3 ticks"]
        NORMAL["NORMAL (1.0)<br/>Standard signals<br/>Clears in ~10 ticks"]
        SLOW["SLOW (0.2)<br/>Persistent memory<br/>Clears in ~50 ticks"]
    end

    FAILURE --> NORMAL
    SUCCESS --> SLOW
    RISK --> NORMAL
    NEED --> NORMAL
    DEPENDENCY --> SLOW
    HUMAN_PRIORITY --> SLOW

    HUM --> HUMAN_PRIORITY
    TST --> SUCCESS
    SEC --> FAILURE

    style SUCCESS fill:#0f766e,color:#fff
    style FAILURE fill:#dc2626,color:#fff
    style HUMAN_PRIORITY fill:#7c3aed,color:#fff
    style DEPENDENCY fill:#1d4ed8,color:#fff
```

Compound key format: `"{location}:{signal_type.value}"` (e.g. `"codomyrmex.git_operations.core:failure"`).

## MCP Tool Surface

All 8 tools route through a module-level `ColonyKernel` singleton. State persists for the lifetime of the MCP server process.

| Tool | Input | Output |
|------|-------|--------|
| `colony_propose_action` | agent_id, action_type, target, rationale, rollback_plan, evidence | GateResult (decision, gate_score, reason, required_evidence) |
| `colony_record_outcome` | agent_id, action_type, target, actual_outcome, tests_passed, human_feedback | status, consequence_id, trust_score, role |
| `colony_agent_profile` | agent_id | AgentTrustProfile (role, trust_score, total_proposals, consequence_history) |
| `colony_status` | (none) | pheromone_summary, budget_usage, role_distribution, recent_consequences, pruning_candidates_count |
| `colony_pheromone_query` | location, signal_type | list of ColonySignal dicts |
| `colony_falsify_plan` | plan_json | findings, severity_score, recommendation |
| `colony_pruning_report` | (none) | candidates, total_candidates, generated_at |
| `colony_tick` | (none) | post-tick colony_status |

## Invariants

1. **Zero-mock**: All tests use real ColonyKernel instances; no unittest.mock.
2. **Idempotent registration**: `register_all()` is idempotent.
3. **Star topology**: `models.py` is the centre; no cross-subsystem imports.
4. **Trust clamping**: Trust scores are always in [0.0, 1.0].
5. **Budget enforcement**: Any single dimension exceeded → HOLD.
6. **SANDBOX block**: SANDBOX agents always receive REFUSE.
7. **Pruning is read-only**: PruningDaemon never writes or deletes.
8. **DEPENDENCY on record**: `record_outcome` always deposits DEPENDENCY signal.

## Test Coverage

```bash
uv run pytest src/codomyrmex/tests/unit/colony_kernel/ -v
# 456 tests, 0 failures
```

## Navigation

- **Source**: [src/codomyrmex/colony_kernel/](../../src/codomyrmex/colony_kernel/)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Tests**: [src/codomyrmex/tests/unit/colony_kernel/](../../src/codomyrmex/tests/unit/colony_kernel/)
