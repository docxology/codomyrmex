# 5. Experimental Setup {#sec:experimental_setup}

This section is structured in two parts. Section 5.0 defines the experimental design proper:
independent variables, baseline conditions, dependent variables, trial structure, and analysis
procedure. Sections 5.1–5.9 document configuration parameters in sufficient detail to reproduce
reported results; YAML parameter tables are consolidated there so that the experimental narrative
above remains uncluttered.

Three distinct evaluation contexts are reported and kept separate throughout:

- **Unit and integration test suite** — {{CONFIG_TEST_COUNT}} pytest tests gated by CI; these verify
  behavioral contracts, not performance claims.
- **20-trial benchmark suite** — the primary empirical surface; each trial is a self-contained
  colony run against the shared workload corpus (see §5.0.4 for trial definition).
- **Analytical derivations** — closed-form results (e.g., gate refusal rate as a function of the
  scoring formula and the empirical trust distribution) that are computed from first principles and
  verified against the benchmark observations.

Readers should not conflate these contexts: the 20-trial count is the benchmark sample, not the
test-suite size, and analytic results do not depend on the trial sample.

All numeric values are drawn directly from the YAML configuration files versioned alongside the
codebase (config version {{CONFIG_VERSION}}).

---

## 5.0 Experimental Design

### 5.0.1 Independent Variables

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

### 5.0.2 Dependent Variables

| Dependent variable | Operationalisation |
|--------------------|--------------------|
| Gate decision distribution | Fraction of actions routed to EXECUTE / HOLD / REFUSE across a full trial |
| Error rate | Proportion of EXECUTE decisions that result in a logged failure event (kernel `SignalType.FAILURE` emission) |
| Budget efficiency | LLM calls consumed per successfully completed task subtree |
| Trust stability | Mean absolute deviation of agent trust scores across scheduler ticks |
| Throughput | Task subtrees closed (terminal `SignalType.SUCCESS`) per experiment run |

### 5.0.3 Baseline Conditions and Hypotheses

Each baseline isolates a single gating dimension to attribute the performance of the full
Codomyrmex gate to its component contributions:

- **H1** (vs. static-trust-only): Codomyrmex achieves a lower error rate by rejecting high-trust
  agents whose actions exceed budget or risk caps — situations the static baseline cannot detect.
- **H2** (vs. budget-only): Codomyrmex achieves higher throughput by permitting low-budget-cost
  actions from high-trust agents that the budget-only gate would conservatively HOLD.
- **H3** (vs. no-gate): Codomyrmex reduces error rate and cumulative security exposure at the cost
  of a bounded throughput reduction, establishing that the gate's safety overhead is proportionate.

### 5.0.4 Trial Structure and Replications

The benchmark suite consists of {{CONFIG_TRIAL_COUNT}} independent trials. Each trial is defined
as follows:

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
- **Seed registration** — each run uses a fixed random seed drawn from a pre-registered seed
  table (seeds 0–{{CONFIG_TRIAL_COUNT_MINUS_1}}, registered at `tests/integration/seeds.txt`
  prior to data collection).

With {{CONFIG_TRIAL_COUNT}} trials, power is sufficient to detect medium effect sizes
(Cohen's $h \approx 0.5$ for proportion comparisons, Cohen's $d \approx 0.8$ for continuous
outcomes) at $\alpha = 0.05$ with $\beta \leq 0.20$. Confidence intervals are reported for all
primary outcomes; readers should treat point estimates as indicative given the modest sample.

### 5.0.5 Trust Initialization and Colony Warm-Up Procedure

All agents enter each trial at `AgentTrustProfile(trust_score=0.1, role=AgentRole.SANDBOX,
total_proposals=0)`. The starting score of 0.1 places agents below the REPAIR_ANT promotion
threshold (0.20 as defined by `_ROLE_REPAIR_MIN_TRUST` in `kernel.py`) so that no agent enters
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

### 5.0.6 Analysis Procedure

Gate decision distributions are compared across conditions using Fisher's exact test (four cells:
EXECUTE / HOLD / REFUSE / total per condition pair). Error rates are compared with a two-sample
proportion z-test with Bonferroni correction for three pairwise comparisons ($\alpha = 0.05 / 3$).
Effect sizes are reported as Cramér's $V$ for categorical distributions and Cohen's $h$ for
proportions. Throughput and budget efficiency are compared with Mann–Whitney U tests (non-parametric
because run-level distributions are right-skewed). Confidence intervals for proportions use the
Wilson score method (preferred over the normal approximation at small $n$).

All analysis code is in `scripts/analysis/compare_conditions.py`; outputs are written to
`output/analysis/`. Analytical derivations of the gate refusal rate are in
`scripts/analysis/analytical_gate_rate.py`, which numerically integrates the scoring formula
over the empirical trust score distribution from the benchmark runs.

---

## 5.1 Gate Configuration

The execution gate evaluates every proposed action against four dimensions and routes it to one of
three outcomes. Table 1 lists the decision thresholds. These thresholds are defined in
`kernel.yaml` and enforced by `colony_kernel/kernel.py` (constants `_GATE_SCORE_EXECUTE = 0.75`
and `_GATE_SCORE_HOLD = 0.50`); they are the sole numeric authority — no threshold value is
duplicated elsewhere.

**Table 1 — Gate Decision Thresholds**

| Outcome | Condition | Interpretation |
|---------|-----------|----------------|
| EXECUTE | composite score ≥ {{CONFIG_GATE_EXECUTE_THRESHOLD}} | Action is approved and dispatched immediately |
| HOLD | {{CONFIG_GATE_HOLD_THRESHOLD}} ≤ score < {{CONFIG_GATE_EXECUTE_THRESHOLD}} | Action is queued pending additional context or human review |
| REFUSE | composite score < {{CONFIG_GATE_HOLD_THRESHOLD}} | Action is rejected; rationale is logged to the pheromone trail |

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

## 5.2 Gate Score Weights

The composite gate score is a weighted sum of four independently computed dimension scores.
Table 2 gives the weight assigned to each dimension. Weights sum to 1.00.

**Table 2 — Gate Score Dimension Weights**

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Budget | 0.30 | Fraction of remaining budget headroom relative to configured caps |
| Risk | 0.30 | Inverse of estimated action risk; higher risk reduces this component |
| Trust | 0.25 | Normalised agent trust score at the time of the gate evaluation |
| Completeness | 0.15 | Coverage of required fields and preconditions in the action specification |

The budget and risk dimensions share equal weight (0.30 each, combined 0.60), reflecting the
design priority of keeping resource expenditure and operational risk as the primary regulators
of autonomous action. Trust receives less weight than budget or risk (0.25) because a high-trust
agent issuing a budget-exhausting action is still dangerous — the gate must be able to block such
actions even when trust is high. Completeness carries the smallest weight (0.15) because an
incomplete specification is more often a recoverable quality issue than a safety concern; HOLD
(not REFUSE) is the expected outcome for specification gaps alone.

The 0.30/0.30/0.25/0.15 vector was derived iteratively from simulation runs over the workload
corpus, holding the decision thresholds fixed, and selecting the weight vector that minimised
a joint cost function penalising both error rate and throughput loss. The final vector was
then validated on held-out workload seeds before the benchmark suite was run.

---

## 5.3 Pheromone Configuration

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

**Table 3 — Pheromone Decay Rate Classes**

| Class | `DecayRate` value | Effective rate at default base | Characteristic half-life | `SignalType` variants |
|-------|-------------------|-------------------------------|--------------------------|----------------------|
| FAST | 3.0 | 0.3/tick | ~2 ticks (2.31) | `FAILURE`, `RISK` |
| NORMAL | 1.0 | 0.1/tick | ~7 ticks (6.93) | `NEED` |
| SLOW | 0.2 | 0.02/tick | ~35 ticks (34.66) | `SUCCESS`, `DEPENDENCY`, `HUMAN_PRIORITY` |

`DecayRate` members are plain numeric floats on the enum (`FAST = 3.0`, `NORMAL = 1.0`,
`SLOW = 0.2`). They are evaporation multipliers, not lambda functions; the scheduler applies
`base_evaporation_per_tick * decay_rate_value` at each tick.

Fast-decay signals carry high-frequency tactical information whose relevance expires within one
scheduling cycle. `HUMAN_PRIORITY` is assigned the SLOW class because human review latency can
span many ticks; the signal must persist until it is explicitly acknowledged, ensuring that
no subsequent automated action proceeds on an escalated item before a human decision is recorded.

---

## 5.4 Resource Budget Caps

All experiments are bounded by the hard caps defined in `config/colony_kernel/kernel.yaml`.
The kernel enforces these caps via `ResourceLedger`; any action whose projected cost would breach
a cap receives an automatic REFUSE decision regardless of gate score.

**Table 4 — Resource Budget Caps (`kernel.yaml`)**

| Budget Dimension | Cap | Unit |
|-----------------|-----|------|
| LLM calls | {{CONFIG_BUDGET_MAX_LLM_CALLS}} | calls per experiment run |
| Wall-clock runtime | {{CONFIG_BUDGET_MAX_RUNTIME}} | seconds |
| Cumulative risk | {{CONFIG_BUDGET_MAX_RISK}} | normalised risk units (0–1) |
| Security exposure | {{CONFIG_BUDGET_MAX_SECURITY}} | normalised exposure score (0–1) |

The `llm_calls` cap of {{CONFIG_BUDGET_MAX_LLM_CALLS}} was chosen to allow complex multi-agent
workflows while remaining within single-run cost budgets during evaluation. The `runtime` cap of
{{CONFIG_BUDGET_MAX_RUNTIME}} seconds (5 minutes) provides a wall-clock backstop independent of
call-count accounting; it is intentionally tight to surface runaway-agent behaviour before it
accumulates significant cost.

---

## 5.5 Role Configuration

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

**Table 5 — `AgentRole` Variants, Promotion Thresholds, and Permitted Actions**

| `AgentRole` variant | Promotion trust threshold | Minimum proposals | Permitted action types |
|---------------------|--------------------------|-------------------|------------------------|
| `SANDBOX` | — (entry role; all new agents begin here) | — | read-only, observe |
| `REPAIR_ANT` | trust ≥ 0.20 | ≥ 3 total proposals | read, write (scoped), patch, test-fix, doc-update |
| `MEMORY_ANT` | trust ≥ 0.35 | ≥ 3 total proposals | read, write, archive, index, summarise |
| `DISPATCHER` | trust ≥ 0.50 | ≥ 3 total proposals | full task dispatch; may delegate, coordinate, route |
| `GUARD_ANT` | trust ≥ 0.70 | ≥ 3 total proposals | gate other agents; security review, gate audit, archive authority |

**Two distinct role-inference algorithms exist in the codebase and must not be conflated:**

1. **`kernel.py` inlined `RoleAdapter`** — uses the 0.20/0.35/0.50/0.70 threshold ladder shown
   above (constants `_ROLE_REPAIR_MIN_TRUST`, `_ROLE_MEMORY_MIN_TRUST`,
   `_ROLE_DISPATCHER_MIN_TRUST`, `_ROLE_GUARD_MIN_TRUST`). An agent with fewer than
   `_ROLE_MIN_PROPOSALS_FOR_PROMOTION = 3` total proposals stays SANDBOX regardless of trust
   score. Promotion is determined by the highest threshold the agent's current trust clears.

2. **`role_adapter.py` `RoleAdapter`** — uses an action-type-based algorithm with different
   thresholds (REPAIR_ANT: trust ≥ 0.80 and successful types intersect `{test_fix, bug_repair}`;
   MEMORY_ANT: trust ≥ 0.80 and successful types intersect `{doc_write, memory_index}`;
   GUARD_ANT: trust ≥ 0.85 and successful types intersect `{security_scan, vulnerability_fix}`;
   DISPATCHER: ≥ 20 proposals with ≥ 70% acceptance rate; forced SANDBOX if trust < 0.30 or
   consecutive failures ≥ 3). The thresholds 0.20/0.35/0.50/0.70 do **not** appear in
   `role_adapter.py`.

The kernel instantiates the `role_adapter.py` `RoleAdapter` as a subsystem
(`self.role_adapter = RoleAdapter()`); the inlined `kernel.py` `RoleAdapter` is a local class
used for the trust-ladder computation within the kernel's own role-evaluation logic.

Demotion is automatic: a trust score drop below the entry threshold of the current role triggers
an immediate reassignment to the highest role whose threshold the new score still clears.

---

## 5.6 Falsification Vectors

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

Each vector is implemented as a pytest parametrised test case in
`tests/integration/test_falsification.py`. A vector is considered passing when the system
produces the expected rejection or alarm outcome with no side-effects on unrelated state.

---

## 5.7 YAML Configuration Files

The colony kernel reads {{CONFIG_YAML_CONFIG_FILES}} YAML files from `config/colony_kernel/` at
startup. No configuration is hardcoded in Python source; all numeric parameters exposed in this
section trace to one of these files.

**`kernel.yaml`**
Defines the top-level budget caps (Table 4), the gate decision thresholds (Table 1), the pheromone
signal type registry, and the overall gate score weight vector (Table 2).

**Important:** the trust promotion thresholds (0.20, 0.35, 0.50, 0.70) and the minimum-proposals
gate (`_ROLE_MIN_PROPOSALS_FOR_PROMOTION = 3`) are defined as module-level private constants in
`kernel.py` — they are not read from any YAML file and are not configurable at runtime.

**`roles.yaml`**
Defines the {{CONFIG_ROLE_COUNT}} `AgentRole` variants (`SANDBOX`, `REPAIR_ANT`, `MEMORY_ANT`,
`DISPATCHER`, `GUARD_ANT`), including the action types permitted at each role and the demotion
rules applied when trust falls below a role's entry threshold. Promotion trust thresholds are
code-defined in `kernel.py` and are not overridable via this file.

**`decay_rates.yaml`**
Provides per-`SignalType` decay rate overrides (Table 3). `SignalType` variants not listed in this
file inherit the NORMAL decay rate (multiplier {{CONFIG_DECAY_RATE_NORMAL}}). The file is the
single authoritative source for decay parameters; the kernel reads it at startup and caches values
for the lifetime of the colony process. The `SignalType` variant name is used as the YAML key —
any unrecognised key causes startup to abort with a configuration error rather than silently
defaulting, ensuring that renamed variants are caught immediately.

---

## 5.8 Software Environment

All experiments were conducted with the following software stack.

**Table 6 — Software Environment**

| Component | Value |
|-----------|-------|
| Python version | {{PYTHON_VERSION}} |
| Package manager | uv |
| Linter | ruff (zero-error policy enforced in CI) |
| Type checker | ty (zero-diagnostic policy enforced in CI) |
| Test runner | pytest with coverage |
| Config version | {{CONFIG_VERSION}} |
| Generated | {{GENERATION_TIMESTAMP}} |

The zero-error and zero-diagnostic policies mean that CI blocks any merge that introduces a ruff
finding or a ty type error, providing a continuous correctness baseline across the codebase.

The data models (`ActionProposal`, `GateResult`, `AgentTrustProfile`, `AgentRole`, `SignalType`,
`DecayRate`) are defined in `models.py` using Python standard-library `@dataclass` and `enum.Enum`
— there is no Pydantic dependency. This choice was deliberate: the models are used inside a
performance-sensitive scheduling loop where Pydantic's validation overhead is undesirable, and
all validation is performed at the gate boundary before proposals enter the loop.

---

## 5.9 Pipeline Ordering

Manuscript variables are produced by a three-stage pipeline that must be executed in order.
Running stages out of order produces stale or missing variable substitutions.

**Stage 1 — `colony_analysis.py`**
Runs the full colony simulation or replays a recorded experiment trace. Produces
`experiment_results.json` containing raw gate decisions, trust trajectories, pheromone snapshots,
and budget consumption traces.

**Stage 2 — `z_generate_manuscript_variables.py`**
Reads `experiment_results.json` and the three YAML config files, computes all derived statistics,
and writes `manuscript_variables.yaml`. This file is the single source for all `{{TOKEN}}`
substitutions used across the manuscript sections.

**Stage 3 — `03_render_pdf.py`**
Reads every manuscript Markdown section, substitutes `{{TOKEN}}` values from
`manuscript_variables.yaml`, passes the result through the LaTeX pipeline, and produces the final
PDF. Unresolved tokens cause the render to abort with an error listing the missing variables.

---

*Section generated {{GENERATION_TIMESTAMP}} from config version {{CONFIG_VERSION}}.*
