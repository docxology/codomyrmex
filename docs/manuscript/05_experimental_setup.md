# Experimental Setup {#sec:experimental_setup}

This section is structured in two parts. [@sec:experimental-design] defines the experimental design proper:
independent variables, baseline conditions, dependent variables, trial structure, and analysis
procedure. The remaining subsections document configuration parameters in sufficient detail to reproduce
reported results; YAML parameter tables are consolidated there so that the experimental narrative
above remains uncluttered.

Three distinct evaluation contexts are defined and kept separate throughout:

- **Colony-kernel unit and integration test suite** — {{CONFIG_TEST_COUNT}} pytest tests gated by CI; these verify
  behavioral contracts, not performance claims.
- **Configured 20-trial benchmark protocol** — a reproducible synthetic workload design; each trial
  is specified as a self-contained colony run against the shared workload corpus (see [@sec:trial-structure] for
  trial definition). Raw trial traces are not shipped with this manuscript snapshot.
- **Analytical contract checks** — deterministic results derived from the gate formula, trust ladder,
  and checked-in fixtures; these support configuration consistency rather than production
  performance claims.

Readers should not conflate these contexts: the 20-trial count is a configured protocol size, not the
test-suite size, and analytic contract checks do not depend on benchmark trace availability.

All numeric values are drawn directly from the YAML configuration files versioned alongside the
codebase (config version {{CONFIG_VERSION}}).

---

## Experimental Design {#sec:experimental-design}

### Independent Variables {#sec:independent-variables}

The primary independent variable is the gating strategy applied to every proposed agent action.
Four conditions are evaluated:

1. **Codomyrmex** — the full composite gate (budget + risk + trust + completeness weights, live
   `AgentRole` enforcement, and `SignalType`-indexed pheromone coordination).
2. **Static-trust-only gate** — EXECUTE if agent trust ≥ {{CONFIG_GATE_EXECUTE_THRESHOLD}},
   REFUSE otherwise; budget, risk, and completeness dimensions are ignored.
3. **Budget-only gate** — EXECUTE if remaining LLM-call and runtime budgets are above 50 % of
   their caps; all other dimensions ignored.
4. **No-gate (always EXECUTE)** — every proposed action is dispatched unconditionally; serves as
   the unconstrained performance ceiling and safety floor.

Conditions 2–4 are implemented as drop-in replacements for the composite gate and share the
identical task workload and colony configuration.

### Dependent Variables {#sec:dependent-variables}

[@tbl:dependent_variables] defines the measured outcomes for the configured protocol.

| Dependent variable | Operationalisation |
|--------------------|--------------------|
| Gate decision distribution | Fraction of actions routed to EXECUTE / HOLD / REFUSE across a full trial |
| Error rate | Proportion of EXECUTE decisions that result in a logged failure event (kernel `SignalType.FAILURE` emission) |
| Budget efficiency | LLM calls consumed per successfully completed task subtree |
| Trust stability | Mean absolute deviation of agent trust scores across scheduler ticks |
| Throughput | Task subtrees closed (terminal `SignalType.SUCCESS`) per experiment run |
: Dependent variables for the configured benchmark protocol. {#tbl:dependent_variables}

### Baseline Conditions and Hypotheses {#sec:baseline-conditions}

Each baseline isolates a single gating dimension to attribute the performance of the full
Codomyrmex gate to its component contributions:

- **H1** (vs. static-trust-only): Codomyrmex achieves a lower error rate by rejecting high-trust
  agents whose actions exceed budget or risk caps — situations the static baseline cannot detect.
- **H2** (vs. budget-only): Codomyrmex achieves higher throughput by permitting low-budget-cost
  actions from high-trust agents that the budget-only gate would conservatively HOLD.
- **H3** (vs. no-gate): Codomyrmex reduces error rate and cumulative security exposure at the cost
  of a bounded throughput reduction, establishing that the gate's safety overhead is proportionate.

### Trial Structure and Replications {#sec:trial-structure}

The benchmark protocol consists of {{CONFIG_TRIAL_COUNT}} independent trials. Each trial is defined
as follows for reproducibility and future external execution:

- **Task workload** — a fixed sequence of {{CONFIG_WORKLOAD_TASK_COUNT}} task subtrees drawn from
  the shared workload corpus in identical order across conditions within each seed; this removes
  workload-ordering as a confound.
- **Agent mix** — {{CONFIG_AGENT_COUNT}} agents initialised at `AgentRole.SANDBOX` with
  `trust_score = 0.1` (the `AgentTrustProfile` default); no pre-warm is applied, so role
  promotion, if it occurs, is earned within the trial.
- **Colony warm-up** — the first {{CONFIG_WARMUP_TICKS}} scheduler ticks are designated warm-up.
  Pheromone deposits made during warm-up are included in subsequent routing decisions but
  warm-up-period outcomes are excluded from the dependent-variable computations. This ensures
  that trust distributions have non-trivial structure before performance measurement begins.
- **Termination** — a trial ends when either the workload corpus is exhausted or the
  wall-clock budget cap ({{CONFIG_BUDGET_MAX_RUNTIME}} seconds) is reached, whichever is first.
- **Trial indexing** — deterministic trial indices run from 0 to
  {{CONFIG_TRIAL_COUNT_MINUS_1}}. The colony-kernel code path does not invoke
  random-number generators, so no external seed registry is required for the
  reported benchmark snapshot.

Because raw benchmark traces are not included in this release artifact, the configured trial count
is not used to claim statistical power, confidence intervals, or production effect sizes. The
checked-in validation surface is the deterministic test suite plus generated consistency checks.

### Trust Initialization and Colony Warm-Up Procedure {#sec:trust-initialization}

All agents enter each trial at `AgentTrustProfile(trust_score=0.1, role=AgentRole.SANDBOX,
total_proposals=0)`. The starting score of 0.1 places agents below the REPAIR_ANT promotion
threshold (0.20 as defined by `_ROLE_REPAIR_MIN_TRUST` in `role_adapter.py`) so that no agent enters
the measurement phase with inherited authority.

The warm-up phase serves two purposes: (a) it allows pheromone trails to accumulate from the
first successful and failed actions, seeding the coordination layer with non-trivial signal
structure; (b) it allows at least some agents to accumulate the three proposals required by
`_ROLE_MIN_PROPOSALS_FOR_PROMOTION` before their roles are evaluated against trust thresholds.
The warm-up length of {{CONFIG_WARMUP_TICKS}} ticks was chosen to be long enough for role
differentiation to begin but short enough that the measurement window dominates trial duration.

Trust scores evolve via `compute_trust_delta()` (defined once in `models.py` and delegated to
from both `ConsequenceMemory` and `RoleAdapter`). The delta formula is:

```
delta = +0.04  if tests_passed  else  -0.08
delta += -0.05  if repair_needed
delta += human_feedback * 0.03   # human_feedback in [-1, +1]
```

Clamping is applied by `apply_delta`, not by `compute_trust_delta` itself. The asymmetry
(+0.04 gain vs. −0.08 loss) models conservative trust: agents must pass roughly two tasks cleanly
to recover from a single failure, creating a natural filter for agents that act carelessly.

### Analysis Procedure {#sec:analysis-procedure}

When benchmark traces are produced, gate decision distributions should be compared across conditions
using Fisher's exact test over EXECUTE / HOLD / REFUSE counts; error rates should be compared with
two-sample proportion tests with correction for planned pairwise comparisons. The current manuscript
does not ship those trace files or analysis outputs. Reported gate-refusal and trust-trajectory
values instead come from deterministic contract fixtures regenerated by
`scripts/z_generate_manuscript_variables.py`.

---

## Gate Configuration {#sec:gate-configuration}

The execution gate evaluates every proposed action against four dimensions and routes it to one of
three outcomes. [@tbl:experimental_gate_thresholds] lists the decision thresholds. These thresholds are defined in
`kernel.yaml` and enforced by `colony_kernel/kernel.py` (constants `_GATE_SCORE_EXECUTE = 0.75`
and `_GATE_SCORE_HOLD = 0.50`); they are the sole numeric authority — no threshold value is
duplicated elsewhere.

| Outcome | Condition | Interpretation |
|---------|-----------|----------------|
| EXECUTE | composite score ≥ {{CONFIG_GATE_EXECUTE_THRESHOLD}} | Action is approved and dispatched immediately |
| HOLD | {{CONFIG_GATE_HOLD_THRESHOLD}} ≤ score < {{CONFIG_GATE_EXECUTE_THRESHOLD}} | Action is queued pending additional context or human review |
| REFUSE | composite score < {{CONFIG_GATE_HOLD_THRESHOLD}} | Action is rejected; rationale is logged to the pheromone trail |
: Gate decision thresholds for experimental configuration. {#tbl:experimental_gate_thresholds}

On a REFUSE outcome the kernel deposits a `ColonySignal(SignalType.FAILURE,
strength=1.0 + falsification_severity * 3.0)` at `proposal.target`, amplifying the inhibitory
signal proportionally to how strongly the `FalsificationWorker` flagged the action.

The gate evaluation proceeds in this order within `propose_action()`:

1. `FalsificationWorker.analyze(proposal)` → findings (falsification severity 0.0–1.0)
2. `ResourceLedger.check_budget(proposal.budget_estimate)` → `budget_approved` (non-consuming
   check — the ledger is not debited at this stage)
3. Load or create the agent's `AgentTrustProfile` via `ConsequenceMemory.get_profile()`;
   increment `total_proposals`; save; call `RoleAdapter.update(profile)` to refresh role
4. `ActuationGate.evaluate(proposal, profile, findings, budget_approved)` → `GateResult`
5. On REFUSE: deposit the failure pheromone signal described above

Note: `propose_action()` is the primary submission entry point. There is no separate `submit()`
method on the public API; callers always go through `propose_action()`.

---

## Gate Score Weights {#sec:gate-score-weights}

The composite gate score is a weighted sum of four independently computed dimension scores.
[@tbl:experimental_gate_weights] gives the weight assigned to each dimension. Weights sum to 1.00.

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Budget | 0.30 | Fraction of remaining budget headroom relative to configured caps |
| Risk | 0.30 | Inverse of estimated action risk; higher risk reduces this component |
| Trust | 0.25 | Normalised agent trust score at the time of the gate evaluation |
| Completeness | 0.15 | Coverage of required fields and preconditions in the action specification |
: Gate score dimension weights for experimental configuration. {#tbl:experimental_gate_weights}

The budget and risk dimensions share equal weight (0.30 each, combined 0.60), reflecting the
design priority of keeping resource expenditure and operational risk as the primary regulators
of autonomous action. Trust receives less weight than budget or risk (0.25) because a high-trust
agent issuing a budget-exhausting action is still dangerous — the gate must be able to block such
actions even when trust is high. Completeness carries the smallest weight (0.15) because an
incomplete specification is more often a recoverable quality issue than a safety concern; HOLD
(not REFUSE) is the expected outcome for specification gaps alone.

The 0.30/0.30/0.25/0.15 vector is a design-prior weighting: budget and risk jointly dominate the
ordinary score, trust is secondary, and completeness is intentionally recoverable through HOLD.
Future benchmark traces may calibrate these weights, but the implementation and manuscript treat
the current vector as a fixed, auditable configuration contract.

---

## Pheromone Configuration {#sec:pheromone-configuration}

The stigmergic coordination layer maintains {{CONFIG_SIGNAL_TYPES_COUNT}} distinct signal types
drawn from the `SignalType` enum defined in `models.py`, each with its own decay rate. Decay is
modelled as exponential decay applied once per scheduler tick. The `DecayRate` enum provides
evaporation multipliers; the base evaporation rate from `StigmergyConfig` is multiplied by this
factor at each tick.

**`SignalType` enum values ({{CONFIG_SIGNAL_TYPES_COUNT}} total):**

1. `SignalType.FAILURE` — deposited on terminal task failure or REFUSE gate decision; inhibits
   reassignment to the same subtree
2. `SignalType.SUCCESS` — deposited when an agent successfully closes a task
3. `SignalType.RISK` — deposited when a budget dimension nears its cap or an action's risk score
   exceeds a warning threshold
4. `SignalType.NEED` — deposited when an agent requests additional resources or context before
   proceeding
5. `SignalType.DEPENDENCY` — deposited when a task subtree identifies an unresolved inter-agent
   dependency
6. `SignalType.HUMAN_PRIORITY` — deposited when a HOLD outcome is escalated to human review;
   persists until acknowledged

[@tbl:experimental_decay_rates] records the configured pheromone decay classes.

| Class | `DecayRate` value | Effective rate at default base | Characteristic half-life | `SignalType` variants |
|-------|-------------------|-------------------------------|--------------------------|----------------------|
| FAST | 3.0 | 0.3/tick | ~2 ticks (2.31) | `FAILURE`, `RISK` |
| NORMAL | 1.0 | 0.1/tick | ~7 ticks (6.93) | `NEED` |
| SLOW | 0.2 | 0.02/tick | ~35 ticks (34.66) | `SUCCESS`, `DEPENDENCY`, `HUMAN_PRIORITY` |
: Pheromone decay rate classes for experimental configuration. {#tbl:experimental_decay_rates}

`DecayRate` members are plain numeric floats on the enum (`FAST = 3.0`, `NORMAL = 1.0`,
`SLOW = 0.2`). They are evaporation multipliers, not lambda functions; the scheduler applies
`base_evaporation_per_tick * decay_rate_value` at each tick.

Fast-decay signals carry high-frequency tactical information whose relevance expires within one
scheduling cycle. `HUMAN_PRIORITY` is assigned the SLOW class because human review latency can
span many ticks; the signal must persist until it is explicitly acknowledged, ensuring that
no subsequent automated action proceeds on an escalated item before a human decision is recorded.

---

## Resource Budget Caps {#sec:resource-budget-caps}

All experimental and protocol runs are bounded by the hard caps defined in `config/colony_kernel/kernel.yaml`.
The kernel enforces these caps via `ResourceLedger`; any action whose projected cost would breach
a cap bypasses ordinary gate scoring with `gate_score = 0.0`. Standalone gate evaluation returns
`REFUSE` for that condition, while the integrated `ColonyKernel` path returns `HOLD` so the action
can be requeued after the budget period resets.

[@tbl:resource_budget_caps] lists the hard caps enforced by `ResourceLedger`.

| Budget Dimension | Cap | Unit |
|-----------------|-----|------|
| LLM calls | {{CONFIG_BUDGET_MAX_LLM_CALLS}} | calls per experiment run |
| Wall-clock runtime | {{CONFIG_BUDGET_MAX_RUNTIME}} | seconds |
| Cumulative risk | {{CONFIG_BUDGET_MAX_RISK}} | normalised risk units (0–1) |
| Security exposure | {{CONFIG_BUDGET_MAX_SECURITY}} | normalised exposure score (0–1) |
: Resource budget caps from `kernel.yaml`. {#tbl:resource_budget_caps}

The `llm_calls` cap of {{CONFIG_BUDGET_MAX_LLM_CALLS}} was chosen to allow complex multi-agent
workflows while remaining within single-run cost budgets during protocol execution. The `runtime` cap of
{{CONFIG_BUDGET_MAX_RUNTIME}} seconds (5 minutes) provides a wall-clock backstop independent of
call-count accounting; it is intentionally tight to surface runaway-agent behaviour before it
accumulates significant cost.

---

## Role Configuration {#sec:role-configuration}

Agent roles are defined by the `AgentRole` enum in `models.py`. The colony operates
{{CONFIG_ROLE_COUNT}} roles, each corresponding to an `AgentRole` variant:

```
SANDBOX     = "sandbox"
REPAIR_ANT  = "repair_ant"
MEMORY_ANT  = "memory_ant"
DISPATCHER  = "dispatcher"
GUARD_ANT   = "guard_ant"
```

Roles are inferred — never hard-assigned at startup. The `AgentRole` docstring states this
explicitly: *"Roles are inferred by RoleAdapter — never hard-assigned at startup. Each role
carries implicit permission constraints enforced by the gate."*

[@tbl:role_ladder] records the experimental role ladder.

| `AgentRole` variant | Promotion trust threshold | Minimum proposals | Permitted action types |
|---------------------|--------------------------|-------------------|------------------------|
| `SANDBOX` | — (entry role; all new agents begin here) | — | read-only, observe |
| `REPAIR_ANT` | trust ≥ 0.20 | ≥ 3 total proposals | read, write (scoped), patch, test-fix, doc-update |
| `MEMORY_ANT` | trust ≥ 0.35 | ≥ 3 total proposals | read, write, archive, index, summarise |
| `DISPATCHER` | trust ≥ 0.50 | ≥ 3 total proposals | full task dispatch; may delegate, coordinate, route |
| `GUARD_ANT` | trust ≥ 0.70 | ≥ 3 total proposals | gate other agents; security review, gate audit, archive authority |
: `AgentRole` variants, promotion thresholds, and permitted actions. {#tbl:role_ladder}

The `role_adapter.py` `RoleAdapter` exposes two APIs that must not be conflated. The kernel-facing
`infer_role(profile)` / `update(profile)` path uses the 0.20/0.35/0.50/0.70 threshold ladder shown
above (constants `_ROLE_REPAIR_MIN_TRUST`, `_ROLE_MEMORY_MIN_TRUST`,
`_ROLE_DISPATCHER_MIN_TRUST`, `_ROLE_GUARD_MIN_TRUST`). An agent with fewer than
`_ROLE_MIN_PROPOSALS_FOR_PROMOTION = 3` total proposals stays SANDBOX regardless of trust score.
The standalone `assign_role(agent_id)` specialization path additionally considers action history:
REPAIR_ANT and MEMORY_ANT require trust >= 0.80 with matching successful action types,
GUARD_ANT requires trust >= 0.85 with security action history, and DISPATCHER requires at least
20 proposals with at least 70% acceptance. The manuscript's trust-ladder claims use the
kernel-facing `infer_role` path.

Demotion is automatic: a trust score drop below the entry threshold of the current role triggers
an immediate reassignment to the highest role whose threshold the new score still clears.

---

## Falsification Vectors {#sec:falsification-vectors}

The experimental design incorporates {{CONFIG_FALSIFICATION_VECTORS}} adversarial falsification
vectors to probe the gate and trust subsystems. Each vector targets a distinct failure mode.

1. **Budget exhaustion race** — two agents simultaneously consume budget toward the same cap to
   test that the kernel serialises cap checks correctly and does not double-issue an EXECUTE that
   breaches the limit.
2. **Trust threshold bypass** — inject an action with a high composite gate score while the
   issuing agent's trust score sits below 0.20 (`_ROLE_REPAIR_MIN_TRUST`), verifying that the
   agent remains in SANDBOX and that the gate applies SANDBOX permission constraints correctly;
   the expected outcome depends on the action type (write-path actions should REFUSE; read-only
   actions may EXECUTE).
3. **Pheromone replay** — re-deposit a stale `SignalType.SUCCESS` signal after it has fully
   decayed to confirm that the scheduler does not re-credit already-processed signals.
4. **Role promotion race** — promote an agent from `AgentRole.SANDBOX` to `AgentRole.REPAIR_ANT`
   while a concurrent gate evaluation is in flight, testing that the gate snapshot is consistent
   with the role at decision time and that the mid-flight snapshot is not retroactively updated.
5. **Decay rate mismatch** — configure a `SignalType.RISK` signal with a SLOW rate (multiplier
   0.2, overriding the default FAST multiplier 3.0) and observe it over FAST-duration ticks to
   verify that the decay class is read from `decay_rates.yaml` at deposit time, not inferred
   from the `SignalType` variant name.
6. **Weight normalisation drift** — temporarily mutate one gate weight without re-normalising
   the others, confirming that the gate detects weight-sum deviation and rejects the malformed
   configuration before evaluating any action.
7. **HOLD-to-EXECUTE coercion** — submit a follow-up action identical to a HOLD-queued one to
   verify that the queue does not silently upgrade the pending item to EXECUTE on the second
   arrival; the expected outcome is a second HOLD or a REFUSE if the queue depth exceeds the cap.
8. **Security exposure creep** — issue a sequence of low-risk actions that individually pass the
   `security_exposure` cap but cumulatively exceed {{CONFIG_BUDGET_MAX_SECURITY}}, testing that
   cumulative tracking persists across scheduler ticks and that a `SignalType.RISK` deposit is
   emitted at the crossing point.
9. **Completeness field spoofing** — submit an action specification with all required fields
   present but semantically empty (empty strings, zero values) to test that the completeness
   scorer validates content depth, not mere field presence.
10. **Concurrent trust update collision** — issue two trust-modifying events for the same agent
    within a single scheduler tick to verify that the trust ledger serialises writes and does not
    silently drop one update; the post-tick trust score must equal the algebraically correct
    composition of both events.

The 10-vector worker is exercised in
`src/codomyrmex/tests/unit/colony_kernel/test_falsification_worker.py`, and manuscript/doc drift is
covered by `src/codomyrmex/tests/unit/colony_kernel/test_manuscript_consistency.py`. A vector is
considered passing when the system produces the expected finding or gate influence with no
side-effects on unrelated state.

---

## YAML Configuration Files {#sec:yaml-configuration-files}

The colony kernel reads {{CONFIG_YAML_CONFIG_FILES}} YAML files from `config/colony_kernel/` at
startup. No configuration is hardcoded in Python source; all numeric parameters exposed in this
section trace to one of these files.

**`kernel.yaml`**
Defines the top-level budget caps ([@tbl:resource_budget_caps]), the gate decision thresholds
([@tbl:experimental_gate_thresholds]), the pheromone signal type registry, and the overall gate
score weight vector ([@tbl:experimental_gate_weights]).

**Important:** the kernel-facing trust promotion thresholds (0.20, 0.35, 0.50, 0.70) and the
minimum-proposals gate (`_ROLE_MIN_PROPOSALS_FOR_PROMOTION = 3`) are defined as module-level
private constants in `role_adapter.py`; they are not read from YAML and are not configurable at
runtime.

**`roles.yaml`**
Defines the {{CONFIG_ROLE_COUNT}} `AgentRole` variants (`SANDBOX`, `REPAIR_ANT`, `MEMORY_ANT`,
`DISPATCHER`, `GUARD_ANT`) and documentation-facing role labels/defaults. Kernel-facing promotion
and demotion thresholds are code-defined in `role_adapter.py` and are not overridable via this file.

**`decay_rates.yaml`**
Provides per-`SignalType` decay rate overrides ([@tbl:experimental_decay_rates]). `SignalType` variants not listed in this
file inherit the NORMAL decay rate (multiplier {{CONFIG_DECAY_RATE_NORMAL}}). The file is the
single authoritative source for decay parameters; the kernel reads it at startup and caches values
for the lifetime of the colony process. The `SignalType` variant name is used as the YAML key —
any unrecognised key causes startup to abort with a configuration error rather than silently
defaulting, ensuring that renamed variants are caught immediately.

---

## Software Environment {#sec:software-environment-setup}

All experiments were conducted with the following software stack.

[@tbl:software_environment] lists the software stack used for the manuscript snapshot.

| Component | Value |
|-----------|-------|
| Python version | {{PYTHON_VERSION}} |
| Package manager | uv |
| Linter | ruff (zero-error policy enforced in CI) |
| Type checker | ty (zero-diagnostic policy enforced in CI) |
| Test runner | pytest with coverage |
| Config version | {{CONFIG_VERSION}} |
| Generated | {{GENERATION_TIMESTAMP}} |
: Software environment for the manuscript snapshot. {#tbl:software_environment}

The zero-error and zero-diagnostic policies mean that CI blocks any merge that introduces a ruff
finding or a ty type error, providing a continuous correctness baseline across the codebase.

The data models (`ActionProposal`, `GateResult`, `AgentTrustProfile`, `AgentRole`, `SignalType`,
`DecayRate`) are defined in `models.py` using Python standard-library `@dataclass` and `enum.Enum`
— there is no Pydantic dependency. This choice was deliberate: the models are used inside a
performance-sensitive scheduling loop where Pydantic's validation overhead is undesirable, and
all validation is performed at the gate boundary before proposals enter the loop.

---

## Pipeline Ordering {#sec:pipeline-ordering}

Manuscript variables are produced by a three-stage pipeline that must be executed in order.
Running stages out of order produces stale or missing variable substitutions.

**Stage 1 — `z_generate_manuscript_variables.py`**
Runs the colony-kernel scoped pytest coverage gate, reads the YAML
configuration and source-code constants, and writes
`output/data/manuscript_variables.json` plus
`output/data/colony_kernel_coverage.json`. This file pair is the auditable
snapshot for all manuscript token substitutions used across the manuscript
sections.

**Stage 2 — `generate_manuscript_figures.py`**
Reads the generated variable snapshot, `docs/manuscript/config.yaml`, and
`config/colony_kernel/roles.yaml`, then renders the seven figure assets under
`output/figures/` for embedding into the tracked HTML and PDF artifacts. Each
figure carries a small provenance note containing the manuscript version,
configuration hash, and generation date so visual claims remain tied to the same
source snapshot as the prose tokens.

**Stage 3 — `compile_manuscript.py`**
Reads every manuscript Markdown section, substitutes token values from
`output/data/manuscript_variables.json`, writes `output/paper.html`, and
optionally produces the final PDF. Unresolved tokens cause the render to abort
with an error listing the missing variables.

---

*Section generated {{GENERATION_TIMESTAMP}} from config version {{CONFIG_VERSION}}.*
