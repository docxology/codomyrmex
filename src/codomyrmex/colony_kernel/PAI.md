# Colony Kernel — PAI Algorithm Integration

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: June 2026

## Overview

The Colony Kernel is Codomyrmex's emergent proposal-evaluation control plane:
it returns advisory gate verdicts, tracks caller-reported outcomes and resource
use, derives trust and role labels, and maintains process-local pheromone
pressure. Downstream callers remain responsible for enforcing verdicts and for
the accuracy of submitted outcome reports.

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
- Where have failures been reported? (`SignalType.FAILURE` at high strength)
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
| `FAILURE` | A caller or subsystem reported failure here recently | FAST (0.30/tick) |
| `NEED` | Explicit attention request deposited | NORMAL (0.10/tick) |
| `RISK` | Caution marker, clear quickly | FAST |
| `DEPENDENCY` | Actively imported/called | SLOW (0.02/tick) |
| `HUMAN_PRIORITY` | Operator-injected, highest trust weight | SLOW |
| `SUCCESS` | Previous action worked here | SLOW (0.02/tick) |

Trust source weighting during OBSERVE: `HUMAN` signals carry a 2x weight in
gate scoring. When reading pheromone pressure, give operator-deposited signals
(`SignalSource.HUMAN`) priority over `SignalSource.AGENT`.

---

### THINK → FalsificationWorker

The THINK phase produces a plan. Before committing to any approach, the
colony applies adversarial review via `FalsificationWorker`. This maps
exactly to PAI's THINK phase goal: generate a plan and then attack it.

**Subsystem**: `falsification_worker.FalsificationWorker`

`FalsificationWorker.evaluate_plan` applies ten attack vectors to any plan
dict. A plan that clears all ten attack vectors with a `severity_score < 0.4`
receives `recommendation: "execute"` — it passes the THINK-phase gate.

**The ten attack vectors**:

| Attack vector | What it tests | Severity if triggered |
|---|---|---|
| `NO_ROLLBACK` | No concrete rollback strategy | HIGH |
| `NO_TEST_VALUE` | No automated test value | HIGH |
| `SCOPE_CREEP` | Scope exceeds target or rationale | MEDIUM/HIGH |
| `FALSE_METRIC` | Expected outcome is absent or non-falsifiable | LOW/MEDIUM |
| `CIRCULAR_ARCHITECTURE` | Import or architecture cycle risk | MEDIUM/HIGH |
| `DEPENDENCY_RISK` | Too many unvetted dependencies | MEDIUM |
| `SECURITY_RISK` | Security-sensitive change without review evidence | HIGH |
| `OVER_BROAD_MODULE` | Module responsibility is too broad | MEDIUM |
| `HIDDEN_MAINTENANCE_COST` | Long-term upkeep burden is ignored | MEDIUM |
| `PREMATURE_ABSTRACTION` | Generic abstraction without demonstrated need | LOW |

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
actuation gate. The gate is the decision point in this recommended workflow,
but it is not a non-bypassable execution boundary: it returns a verdict and
does not itself run a tool or prevent another caller from acting.

**Subsystem**: `kernel.ColonyKernel.propose_action` (the actuation gate)

**Gate score formula** (`ActuationGate.evaluate`):

```
gate_score = (
    budget_ok    * 0.30
  + risk_ok      * 0.30
  + trust_ok     * 0.25
  + completeness * 0.15
)
gate_score = clamp(gate_score, 0.0, 1.0)
```

**Routing thresholds**:

| Condition | Decision |
|-----------|----------|
| `budget_approved == False` supplied by kernel | HOLD |
| standalone ledger budget check fails | REFUSE |
| `profile.role == SANDBOX` | REFUSE (unconditional) |
| `profile.trust_score < 0.30` | REFUSE (unconditional) |
| CRITICAL falsification finding present | REFUSE |
| `gate_score ≥ 0.75` | EXECUTE |
| `0.50 ≤ gate_score < 0.75` | HOLD |
| `gate_score < 0.50` | REFUSE |

**Gate outcomes**:
- `GateDecision.EXECUTE`: the proposal cleared the current policy; no budget is
  consumed and no DEPENDENCY signal is deposited until a separate
  `record_outcome` call
- `GateDecision.HOLD`: the returned `required_evidence` list tells the caller
  what to address before optional resubmission
- `GateDecision.REFUSE`: the kernel deposits a FAILURE signal at the proposal
  target; it does not automatically change trust or enforce a downstream stop

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

A `REFUSE` result is a hard stop for this recommended workflow. The kernel does
not technically prevent an external caller from bypassing the result. Deposit
additional context for the next cycle via a new OBSERVE run.

---

### VERIFY → Consequence Memory

The VERIFY phase submits a caller's report of what happened after an action.
This is the colony's trust feedback loop: each accepted report updates the
agent profile, resource ledger, and pheromone field. The current MCP surface
does not attest the report or link it to a consumed prior EXECUTE authorization.

**Subsystem**: `consequence_memory.ConsequenceMemory` + `role_adapter.RoleAdapter`

The recommended workflow pairs every acted-upon EXECUTE verdict with one
`colony_record_outcome` call. This pairing is a caller responsibility, not a
kernel invariant. Without submitted reports, the kernel cannot account for
costs, update trust, or derive later role labels from those actions.

**Trust delta formula** (applied by `ConsequenceMemory._compute_delta`):

```
delta  = +0.04  if tests_passed  else  -0.08
delta += -0.05  if repair_needed
delta +=  human_feedback × 0.03   # human_feedback ∈ [-1.0, +1.0]
```

Result: `trust_score = clamp(trust_score + delta, 0.0, 1.0)`

**Pheromone updates from `record_outcome`**:
- `tests_passed=False` → FAILURE with nominal strength 2.0 and TEST source;
  the 1.5 source multiplier deposits effective strength 3.0
- `tests_passed=True` → reinforce an existing SUCCESS trace by 0.15 (a no-op
  when none exists)
- `tests_passed=True` and `repair_needed=False` → additionally deposit SUCCESS
  with nominal strength 1.5 and TEST source, for effective strength 2.25
- every report → DEPENDENCY with strength 0.5 and RUNTIME source

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

Colony roles are inferred from recorded trust and proposal counts. PAI agent
types are capability specialisations, while the colony roles are labels. The
mapping below describes an intended semantic affinity; it does not grant or
restrict action types.

| Colony role | PAI agent type | Trust threshold | How they earn the role |
|---|---|---|---|
| `SANDBOX` | any new agent | entry role; `trust_score = 0.10` | Default for all agents at startup |
| `REPAIR_ANT` | Engineer | ≥ 0.20 and ≥ 3 proposals | Accumulate passing test runs and bug repairs |
| `MEMORY_ANT` | Scribe / Documenter | ≥ 0.35 and ≥ 3 proposals | Document systems, index knowledge, archive modules |
| `DISPATCHER` | Architect | ≥ 0.50 and ≥ 3 proposals | Coordinate and delegate across modules at scale |
| `GUARD_ANT` | Security Reviewer | ≥ 0.70 and ≥ 3 proposals | Run security scans, fix vulnerabilities |

**Role promotion is automatic**. The kernel-facing `RoleAdapter.update(profile)`
path re-derives the role from the profile's trust score and proposal count.
The standalone `assign_role(agent_id)` path is stricter and also considers
successful action types (`test_fix`, `bug_repair`, `doc_write`, `memory_index`,
`security_scan`, and `vulnerability_fix`); do not use its specialization
thresholds as the kernel promotion ladder.

**Gate behavior by role** is deliberately narrow. A SANDBOX agent cannot pass the
gate: new agents start at trust 0.10, and both SANDBOX status and trust below 0.30
hard-refuse before ordinary scoring. Higher roles are inferred labels; the current gate
does not implement inheritance or an action-class permission matrix.

**PAI Architect agents** have a natural semantic affinity with the DISPATCHER
label because their action types are often `"delegate"`, `"coordinate"`, and
`"route"`. Action type and falsification severity do not enter the kernel role
ladder; DISPATCHER is inferred only after at least three proposals and trust of
at least 0.50.

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
  colony_record_outcome(...)                   # submit the caller's outcome report
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

The gate returns only the decision. If the caller acts on EXECUTE, the later
`colony_record_outcome` call records a cost (using a valid supplied cost or the
proposal estimate) and deposits a DEPENDENCY signal.

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
- SUCCESS is deposited at effective strength 2.25 at
  `codomyrmex.git_operations.core` (nominal 1.5 × TEST source multiplier 1.5)
- FAILURE and SUCCESS remain separate channels; the existing FAILURE trace
  changes only when that channel is explicitly ticked, reinforced, or receives
  another deposit
- `engineer-claude-e3-001` trust delta: `+0.04 (tests) + 0.027 (feedback) = +0.067`
- If the profile has at least three counted proposals and the reported outcomes
  raise trust to at least 0.20, the role label becomes REPAIR_ANT on update

```python
colony_tick()
# Advances evaporation. The 3.2-strength FAILURE signal decays toward zero.
# After several ticks with no new failures, the pressure gradient at
# git_operations.core shifts from FAILURE-dominant to DEPENDENCY-dominant.
```

### How ISA criteria translate to pressure gradients

| ISA criterion | Colony signal produced by verification |
|---|---|
| ISC-001: no unhandled exceptions | Reported clean outcome deposits SUCCESS at `git_operations.core`; FAILURE remains independently inspectable |
| ISC-002: CI pass rate ≥ 95% | Explicit ticks decrease FAILURE; submitted outcome reports deposit DEPENDENCY |
| ISC-003: rollback paths documented | MEMORY_ANT `doc_write` action → SUCCESS at `git_operations.core` docs |

After enough explicit ticks, the next Algorithm run may see lower FAILURE,
persisting DEPENDENCY, and a recent SUCCESS trace. This represents the submitted
report history; without independent attestation it does not establish that the
module was repaired or is healthy.

---

## Integration Notes

**Starting with a fresh colony**: `ColonyKernel.__init__` initialises an empty
pheromone field and an empty trust registry. On a PAI session that starts cold,
pre-populate the pheromone field by depositing HUMAN_PRIORITY signals at known
critical modules before the Algorithm begins its OBSERVE phase.

**Cross-session persistence**: The default `ColonyKernel` is an in-process
singleton (`mcp_tools._kernel`). Its in-memory pheromone state and default
`ConsequenceMemory` are lost between processes. A file-backed SQLite path can persist
reported consequences and trust profiles, but the pheromone field, budget accumulator,
and complete kernel state still require a separate persistence design.

**Signal injection from PAI hooks**: PAI hooks (e.g. `ToolActivityTracker`,
`WorkCompletionLearning`) can deposit colony signals as side effects. On tool
failure, deposit a FAILURE signal. On work completion, deposit a SUCCESS signal.
This keeps the colony field in sync with PAI's observability data without any
manual bookkeeping.

**Pruning reports as ISA input**: `colony_pruning_report` is designed to feed
directly into the OBSERVE phase as ISA context. Stale modules with
`confidence ≥ 0.7` are strong candidates for an `archive_module` action at the
next EXECUTE phase — provided that action clears `FalsificationWorker` first.
