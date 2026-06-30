# Colony Kernel — PAI Algorithm Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: June 2026

## Overview

The Colony Kernel is Codomyrmex's emergent control plane: it governs what
agents are allowed to do (actuation gate), how they earn the right to do
more (trust + role system), what the environment currently needs (pheromone
pressure), and what outcomes looked like in practice (consequence memory).

This document maps each PAI Algorithm phase to the Colony Kernel subsystem
that serves it, explains how colony roles map to PAI agent types, describes
how the resource ledger maps to PAI effort tiers, and provides the MCP tool
call sequence a PAI agent should follow at each phase.

---

## PAI Algorithm Phase Mapping

### OBSERVE → Pheromone Pressure Query

The OBSERVE phase gathers current state before forming any plan. In the colony,
"current state" is encoded in the pheromone field: which modules carry FAILURE
or NEED signals, which carry DEPENDENCY signals (actively used), and which have
gone quiet (stale, pruning candidates).

**Subsystem**: `pheromone_store.PheromoneStore` + `kernel.ColonyKernel.pheromone_query`

A PAI agent at OBSERVE reads the colony's stigmergic field to answer:
- What is failing? (`SignalType.FAILURE` at high strength)
- What needs attention? (`SignalType.NEED`)
- What is actively depended on? (`SignalType.DEPENDENCY`)
- What is stale and pruning-eligible? (`SignalType.SUCCESS == 0.0` + no recent `DEPENDENCY`)

The OBSERVE phase also runs the pruning daemon to surface dead-code candidates
before any plan is formed. Pruning reports feed directly into ISA criteria
(see the end-to-end example below).

**MCP tools**:
```
colony_pheromone_query(location="codomyrmex.<module>", signal_type="failure")
colony_pheromone_query(location="codomyrmex.<module>", signal_type="need")
colony_status()          # broad snapshot: top-5 signals, active traces, tick
colony_pruning_report()  # stale/broken modules from PruningDaemon
```

**Key signals to check at OBSERVE**:

| Signal type | Meaning for OBSERVE | Decay rate |
|-------------|---------------------|------------|
| `FAILURE` | Something broke here recently | FAST (0.30/tick) |
| `NEED` | Explicit attention request deposited | NORMAL (0.10/tick) |
| `RISK` | Caution marker, not yet a failure | NORMAL |
| `DEPENDENCY` | Actively imported/called | SLOW (0.02/tick) |
| `HUMAN_PRIORITY` | Operator-injected, highest trust weight | SLOW |
| `SUCCESS` | Previous action worked here | FAST |

Trust source weighting during OBSERVE: `HUMAN` signals carry a 2x weight in
gate scoring. When reading pheromone pressure, give operator-deposited signals
(`SignalSource.HUMAN`) priority over `SignalSource.AGENT`.

---

### THINK → FalsificationWorker

The THINK phase produces a plan. Before committing to any approach, the
colony applies adversarial review via `FalsificationWorker`. This maps
exactly to PAI's THINK phase goal: generate a plan and then attack it.

**Subsystem**: `falsification_worker.FalsificationWorker`

`FalsificationWorker.evaluate_plan` applies five attack vectors to any plan
dict. A plan that clears all five attack vectors with a `severity_score < 0.4`
receives `recommendation: "execute"` — it passes the THINK-phase gate.

**The five attack vectors**:

| Attack vector | What it tests | Severity if triggered |
|---|---|---|
| `missing_rollback` | No rollback strategy | HIGH |
| `underfunded_budget` | `llm_calls == 0` and `runtime_seconds == 0` | MEDIUM |
| `circular_dependency` | `target == agent_id` (self-referential loop) | HIGH |
| `untested_assumption` | No evidence and rationale < 50 chars | MEDIUM |
| `blast_radius` | High-risk action type or `risk_level > 0.6` | MEDIUM or HIGH |

**Composite scoring**:
- `severity_score < 0.4` → `"execute"` (THINK phase: proceed to EXECUTE)
- `0.4 ≤ severity_score < 0.75` → `"hold"` (THINK phase: revise the plan)
- `severity_score ≥ 0.75` → `"refuse"` (THINK phase: abort, re-approach)

**MCP tool**:
```python
colony_falsify_plan(plan_json='{"action_type": "patch_file",
  "target": "codomyrmex.git_operations.core",
  "rationale": "Fix rebase conflict causing CI failure (see run #1042)",
  "rollback_plan": "git revert <sha>; restore from backup branch",
  "evidence": {"ci_run": "1042", "error": "MergeConflictError"},
  "budget_estimate": {"llm_calls": 3, "runtime_seconds": 30.0}}')
```

The THINK phase should call `colony_falsify_plan` for every candidate
approach before selecting one. The approach with the lowest `severity_score`
and `recommendation: "execute"` is the plan to carry forward.

---

### EXECUTE → Actuation Gate

The EXECUTE phase submits the approved plan as an `ActionProposal` to the
actuation gate. The gate is the colony's hard chokepoint: no action reaches
the environment without passing three sequential checks.

**Subsystem**: `kernel.ColonyKernel.propose_action` (the actuation gate)

**Gate checks in order**:

1. **Falsification** (weight 0.4): Re-runs `FalsificationWorker` on the serialised
   proposal. A fresh evaluation on the fully-populated `ActionProposal` object
   may catch issues missed when the plan was a bare dict in THINK.

2. **Budget** (weight 0.3): `ResourceLedger.can_afford` checks the proposal's
   `budget_estimate` against the colony's per-hour LLM call cap, runtime cap,
   risk cap, security exposure cap, and merge risk cap.

3. **Trust** (weight 0.3): The proposing agent's `AgentTrustProfile.trust_score`
   must meet the minimum for its current role:

   | Role | Min trust to EXECUTE |
   |------|---------------------|
   | `SANDBOX` | 0.05 |
   | `REPAIR_ANT` | 0.20 |
   | `MEMORY_ANT` | 0.15 |
   | `DISPATCHER` | 0.25 |
   | `GUARD_ANT` | 0.30 |

**Composite gate score** = `(1 - falsification_severity) * 0.4 + budget_ok * 0.3 + trust_ratio * 0.3`

**Gate outcomes**:
- `GateDecision.EXECUTE`: proceed; ledger records the cost; DEPENDENCY
  pheromone deposited at the target
- `GateDecision.HOLD`: requeue; `required_evidence` list tells agent what to fix
- `GateDecision.REFUSE`: rejected; FAILURE pheromone deposited at the target;
  agent's trust decremented on subsequent `record_outcome` call

**MCP tool**:
```python
colony_propose_action(
    agent_id="engineer-claude-001",
    action_type="patch_file",
    target="codomyrmex.git_operations.core",
    rationale="Fix rebase conflict causing CI failure (see run #1042)",
    rollback_plan="git revert <sha>; restore from backup branch",
    evidence='{"ci_run": "1042", "error": "MergeConflictError"}'
)
```

A `HOLD` result should be treated as a feedback loop back to THINK: address
the `required_evidence` items, revise the plan, re-falsify, re-submit.

A `REFUSE` result is a hard stop. The EXECUTE phase must not proceed. Deposit
additional context for the next cycle via a new OBSERVE run.

---

### VERIFY → Consequence Memory

The VERIFY phase records what actually happened after EXECUTE. This is the
colony's trust feedback loop: every outcome updates the acting agent's
`AgentTrustProfile`, deposits a SUCCESS or FAILURE pheromone at the action
target, and feeds into future gate scoring through the role assignment rules.

**Subsystem**: `consequence_memory.ConsequenceMemory` + `role_adapter.RoleAdapter`

VERIFY is not optional. Every EXECUTE that receives `GateDecision.EXECUTE` must
be followed by a `colony_record_outcome` call. An agent that executes but never
records outcomes cannot accumulate trust and cannot earn a specialist role.

**Trust delta formula** (applied by `RoleAdapter._compute_trust_delta`):

```
delta = +0.05 if tests_passed else -0.05
delta += human_feedback * 0.03   # human_feedback in [-1.0, +1.0]
delta -= 0.04 if repair_needed else 0
delta = clamp(delta, -0.10, +0.10)
```

**Pheromone deposited at VERIFY**:
- `tests_passed=True` and `repair_needed=False` → SUCCESS signal (strength 2.0)
- Otherwise → FAILURE signal (strength 1.5)

**MCP tool**:
```python
colony_record_outcome(
    agent_id="engineer-claude-001",
    action_type="patch_file",
    target="codomyrmex.git_operations.core",
    actual_outcome="Rebase conflict resolved; CI passing on run #1043",
    tests_passed=True,
    human_feedback=0.8   # operator confirmed the fix was correct
)
```

After a successful VERIFY, call `colony_agent_profile` to observe the updated
trust score and confirm the agent's role has advanced (if applicable).

---

## Agent Role ↔ PAI Agent Type Mapping

Colony roles are earned through consequence history. PAI agent types are
capability specialisations. The mapping below describes how each PAI agent type
naturally earns — and operates within — the corresponding colony role.

| Colony role | PAI agent type | Trust threshold | How they earn the role |
|---|---|---|---|
| `SANDBOX` | any new agent | trust < 0.3 | Default for all agents at startup |
| `REPAIR_ANT` | Engineer | ≥ 0.8 + `test_fix` or `bug_repair` successes | Accumulate passing test runs and bug repairs |
| `MEMORY_ANT` | Scribe / Documenter | ≥ 0.8 + `doc_write` or `memory_index` successes | Document systems, index knowledge, archive modules |
| `DISPATCHER` | Architect | ≥ 20 proposals + 70% acceptance rate | Coordinate and delegate across modules at scale |
| `GUARD_ANT` | Security Reviewer | ≥ 0.85 + `security_scan` or `vulnerability_fix` successes | Run security scans, fix vulnerabilities |

**Role promotion is automatic**. `RoleAdapter.update_profile` re-derives the
role on every `ConsequenceRecord`. A PAI Engineer subagent that completes
enough `test_fix` and `bug_repair` actions with `tests_passed=True` will
be promoted from SANDBOX to REPAIR_ANT without any manual intervention.

**Gate permissions by role** are enforced automatically. A SANDBOX agent cannot
execute high-risk actions — its trust floor (0.05) will cause the gate's trust
component to score near zero, resulting in HOLD or REFUSE on any proposal
with a realistic budget.

**PAI Architect agents** are the natural DISPATCHER role. Because Architects
coordinate rather than execute directly, their action types are typically
`"delegate"`, `"coordinate"`, and `"route"`. These actions have low blast
radius and quickly accumulate a high acceptance rate (low falsification
severity), which earns the DISPATCHER role.

---

## Resource Ledger ↔ PAI Effort Tier Mapping

The `ResourceLedger` enforces multi-dimensional spending caps. PAI effort tiers
(E1–E5) correspond to different `ResourceBudget` profiles that the colony
enforces per run.

| PAI effort tier | Typical task scope | Suggested `ResourceBudget` profile |
|---|---|---|
| E1 Standard | Single file, fast path | `max_llm_calls_per_hour=10`, `max_risk_level=0.3`, `max_merge_risk=0.2` |
| E2 Extended | Multi-file, one pass | `max_llm_calls_per_hour=30`, `max_risk_level=0.5`, `max_merge_risk=0.4` |
| E3 Advanced | Feature or module-level | `max_llm_calls_per_hour=60`, `max_risk_level=0.6`, `max_merge_risk=0.6` |
| E4 Deep | Cross-module refactor | `max_llm_calls_per_hour=100`, `max_risk_level=0.7`, `max_merge_risk=0.7` |
| E5 Comprehensive | Whole-system migration | `max_llm_calls_per_hour=200`, `max_security_exposure=0.4` |

The default `ResourceBudget` (100 LLM calls/hour, risk cap 0.8, merge risk 0.7,
security exposure 0.5) corresponds to a permissive E4/E5 profile. For E1/E2
sessions, instantiate the `ColonyKernel` with a tighter `ResourceBudget` before
submitting proposals.

The `resource_ledger.ResourceLedger.agent_spend` method lets PAI hooks report
how much of the budget a specific subagent consumed — useful for the VERIFY
phase of a delegation tree.

**Budget dimensions and PAI meaning**:

| `ResourceCost` field | PAI meaning |
|---|---|
| `llm_calls` | Number of inference calls this agent has made |
| `runtime_seconds` | Wall-clock time consumed by the action |
| `risk_level` | Blast radius: 0.0 = read-only, 1.0 = irreversible destructive |
| `human_attention_minutes` | Estimated human review time needed |
| `merge_risk` | Probability the change will require conflict resolution |
| `doc_debt` | Documentation work deferred by this action |
| `security_exposure` | SAST/scan-detected risk fraction |

---

## MCP Tool Call Sequence by Phase

Complete sequence for a PAI Algorithm run that modifies a module:

```
OBSERVE
  colony_status()                              # snapshot: tick, top signals, agent count
  colony_pheromone_query(location, "failure")  # what's broken
  colony_pheromone_query(location, "need")     # what needs attention
  colony_pheromone_query(location, "dependency") # what's actively used
  colony_pruning_report()                      # stale modules to avoid touching

THINK
  colony_falsify_plan(plan_json)               # adversarial review of candidate plan
  # If severity_score ≥ 0.4: revise plan, re-call colony_falsify_plan
  # If severity_score < 0.4: proceed

EXECUTE
  colony_propose_action(...)                   # submit to actuation gate
  # If HOLD: address required_evidence, loop back to THINK
  # If REFUSE: abort; deposit new NEED signal; restart OBSERVE
  # If EXECUTE: carry out the action

VERIFY
  colony_record_outcome(...)                   # record what actually happened
  colony_agent_profile(agent_id)               # confirm updated trust score + role
  colony_tick()                                # advance evaporation; age signals
```

---

## End-to-End Example: ISA Criteria Feeding Colony Pressure Gradients

This example shows how a PAI Algorithm run producing ISA (Ideal State Artifact)
criteria flows into colony pheromone signals that shape the next run.

### Scenario

The PAI Algorithm runs at E3 on a task: "Improve reliability of
`codomyrmex.git_operations.core`". The Algorithm produces an ISA with these
criteria:

```
ISC-001: `git_operations.core.rebase_branch` raises no unhandled exceptions
ISC-002: CI pass rate for git_operations module ≥ 95% over 7 days
ISC-003: MergeConflictError cases have documented rollback paths
```

### Step 1 — OBSERVE reads colony state

```python
# OBSERVE: what does the pheromone field say about git_operations?
colony_pheromone_query("codomyrmex.git_operations.core", "failure")
# Returns: strength=3.2 (three recent failures)

colony_pheromone_query("codomyrmex.git_operations.core", "dependency")
# Returns: strength=8.7 (heavily used by CI pipeline)

colony_pruning_report()
# Returns: no candidates for git_operations (high dependency strength protects it)
```

The high FAILURE strength at a high-DEPENDENCY location maps directly to
ISC-001 and ISC-002: this module is broken and heavily used.

### Step 2 — THINK runs falsification

The Algorithm proposes: patch `rebase_branch` to catch `MergeConflictError`.

```python
colony_falsify_plan('{"action_type": "patch_file",
  "target": "codomyrmex.git_operations.core",
  "rationale": "rebase_branch raises unhandled MergeConflictError on dirty trees",
  "rollback_plan": "git revert the patch commit; CI monitors for regression",
  "evidence": {"ci_failures": ["run-1040", "run-1041"], "exception": "MergeConflictError"},
  "budget_estimate": {"llm_calls": 4, "runtime_seconds": 45.0, "risk_level": 0.3}}')

# Returns: severity_score=0.0, recommendation="execute"
# No findings: rollback present, budget funded, evidence present, risk low.
```

### Step 3 — EXECUTE passes the gate

```python
colony_propose_action(
    agent_id="engineer-claude-e3-001",
    action_type="patch_file",
    target="codomyrmex.git_operations.core",
    rationale="rebase_branch raises unhandled MergeConflictError on dirty trees",
    rollback_plan="git revert the patch commit; CI monitors for regression",
    evidence='{"ci_failures": ["run-1040", "run-1041"]}'
)
# Returns: decision="execute", gate_score=0.82
```

The gate deposits a DEPENDENCY signal at `codomyrmex.git_operations.core`
(marks it as actively being worked on) and records the `ResourceCost`
against the E3 budget.

### Step 4 — VERIFY closes the loop

After the patch is applied and CI confirms green:

```python
colony_record_outcome(
    agent_id="engineer-claude-e3-001",
    action_type="patch_file",
    target="codomyrmex.git_operations.core",
    actual_outcome="MergeConflictError now caught; CI passing on run-1043",
    tests_passed=True,
    human_feedback=0.9
)
```

The colony responds:
- SUCCESS signal (strength 2.0) deposited at `codomyrmex.git_operations.core`
- FAILURE signal at that location evaporates faster (it was FAST decay; SUCCESS
  reinforcement counters it)
- `engineer-claude-e3-001` trust delta: `+0.05 (tests) + 0.027 (feedback) = +0.077`
- If the agent has enough `patch_file`/`bug_repair` successes, role advances to
  REPAIR_ANT on next update

```python
colony_tick()
# Advances evaporation. The 3.2-strength FAILURE signal decays toward zero.
# After several ticks with no new failures, the pressure gradient at
# git_operations.core shifts from FAILURE-dominant to DEPENDENCY-dominant.
```

### How ISA criteria translate to pressure gradients

| ISA criterion | Colony signal produced by verification |
|---|---|
| ISC-001: no unhandled exceptions | SUCCESS at `git_operations.core` (replaces FAILURE signal over ticks) |
| ISC-002: CI pass rate ≥ 95% | FAILURE strength decreases each successful CI run; DEPENDENCY persists |
| ISC-003: rollback paths documented | MEMORY_ANT `doc_write` action → SUCCESS at `git_operations.core` docs |

The next Algorithm run at OBSERVE will see a changed pressure gradient:
FAILURE strength near zero, DEPENDENCY still high, SUCCESS recently deposited.
This correctly signals "this module was repaired and is healthy" — the colony
encodes verification results as environmental pressure, not as a flag in a
config file.

---

## Integration Notes

**Starting with a fresh colony**: `ColonyKernel.__init__` initialises an empty
pheromone field and an empty trust registry. On a PAI session that starts cold,
pre-populate the pheromone field by depositing HUMAN_PRIORITY signals at known
critical modules before the Algorithm begins its OBSERVE phase.

**Cross-session persistence**: The default `ColonyKernel` is an in-process
singleton (`mcp_tools._kernel`). Pheromone state and trust profiles are lost
between processes. For cross-session memory, wire the `ColonyKernel` to a
`ConsequenceMemory` backend that persists to disk or a database.

**Signal injection from PAI hooks**: PAI hooks (e.g. `ToolActivityTracker`,
`WorkCompletionLearning`) can deposit colony signals as side effects. On tool
failure, deposit a FAILURE signal. On work completion, deposit a SUCCESS signal.
This keeps the colony field in sync with PAI's observability data without any
manual bookkeeping.

**Pruning reports as ISA input**: `colony_pruning_report` is designed to feed
directly into the OBSERVE phase as ISA context. Stale modules with
`confidence ≥ 0.7` are strong candidates for an `archive_module` action at the
next EXECUTE phase — provided that action clears `FalsificationWorker` first.
