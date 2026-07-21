# Appendix: Design Rationale and Visual Evidence {#sec:design-rationale}

This appendix records why the released Colony Kernel uses its present mechanisms and
what each choice gives up. The decisions are engineering choices, not proofs that the
selected policy is optimal. Where an alternative would require outcome data, the
release treats calibration as future evaluation rather than retroactively presenting a
hand-set constant as an empirical result.

{{CONFIG_PARAMETER_STATUS_NOTE}} The appendix consequently distinguishes runtime
defaults, presentation settings, and future-study inputs wherever their roles differ.

## DR-1: Weighted additive gate with hard overrides {#sec:dr-gate-formula}

After its early-return checks, `ActuationGate` computes the score in
[@eq:appendix-gate-score]:

$$
g={{CONFIG_GATE_WEIGHT_BUDGET}}b+{{CONFIG_GATE_WEIGHT_RISK}}h
 +{{CONFIG_GATE_WEIGHT_TRUST}}t+{{CONFIG_GATE_WEIGHT_COMPLETENESS}}c,
$$ {#eq:appendix-gate-score}

where $b$ is budget credit, $h$ is local hazard credit derived from the larger of
RISK and FAILURE pressure, $t$ is tiered trust credit, and $c$ is proposal
completeness. The score is a routing policy, not a probability of safety or harm.

[@tbl:gate-formula-tradeoffs] summarizes the relevant alternatives.

| Policy family | Useful property | Cost or missing prerequisite |
|---|---|---|
| Weighted additive | Direct component decomposition; partial credit supports HOLD | Compensation among components; hand-set weights require external calibration |
| Multiplicative | A zero component can dominate without a separate rule | Small components suppress the whole score; interpretation depends on scaling |
| Explicit rule set | Named conditions are easy to audit | Interactions and ordering grow with the rule set |
| Learned scorer | Can estimate interactions from labeled outcomes | Requires representative, independently attested training and calibration data |
: Tradeoffs among candidate ordinary-score policies. {#tbl:gate-formula-tradeoffs}

The implementation does not rely on the weighted sum for every condition. Missing
budget in the integrated path, SANDBOX status, trust below
{{CONFIG_TRUST_HARD_FLOOR}}, and CRITICAL findings
take explicit branches. This hybrid keeps the ordinary score inspectable while reserving
non-compensatory treatment for named conditions. It also means that analysis of the
formula alone is insufficient to predict every gate result.

## DR-2: Subtractive, tick-driven signal expiry {#sec:dr-decay}

Each trace stores an evaporation amount $\epsilon$ when deposited. A passive tick uses

$$
s_{n+1}=\max({{CONFIG_SCORE_MIN}},s_n-\epsilon),
$$ {#eq:appendix-linear-decay}

and removes a trace at zero. At the defaults, FAST, NORMAL, and SLOW subtract
{{CONFIG_EVAPORATION_FAST}}, {{CONFIG_EVAPORATION_NORMAL}}, and
{{CONFIG_EVAPORATION_SLOW}} per tick. [@eq:appendix-linear-decay] is exact for a trace with no new
deposit, reinforcement, or read-side effect.

The choice makes expiry finite and contract tests easy to replay. Its tradeoffs are
equally explicit: ticks are logical rather than wall-clock time, a larger effective
deposit lasts longer, and repeated deposits can dominate the nominal class. Source and
trust multipliers affect initial strength, while the field cap bounds accumulated
strength. Deployments that need real-time semantics must define the scheduler-to-tick
mapping rather than reinterpret a tick as an undocumented number of seconds.

## DR-3: Process-local state with optional file-backed consequences {#sec:dr-sqlite}

`ColonyKernelConfig` defaults `db_path` to `:memory:`. In that mode consequence rows and
profiles disappear when the process exits. `ConsequenceMemory` also supports a caller
supplied SQLite file path, while `db_path=None` selects its pure in-memory list mode.
The pheromone field remains in memory in all three cases.

This design minimizes setup and keeps real SQLite behavior available to tests. It does
not provide shared multi-process state, restart recovery for signal pressure, remote
replication, migration management, or conflict resolution. A deployment requiring
those properties needs an explicit state architecture; changing only the consequence
database path is not sufficient.

## DR-4: Clipped additive trust updates {#sec:dr-trust-deltas}

The integrated outcome path applies fixed deltas and clips trust to
$[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]$. A clean
reported outcome adds {{CONFIG_TRUST_DELTA_PASS}}; a failed one changes trust by
{{CONFIG_TRUST_DELTA_FAIL}}; repair and human-feedback terms
can change the net update. The rule is transparent and supports exact fixtures such as
[@tbl:trust_trajectory].

The cost of that simplicity is that trust is neither a calibrated posterior nor an
uncertainty interval. Equal scores can arise from different histories, and constant-step
updates do not imply convergence to a unique equilibrium. More importantly, current
outcomes are caller supplied: the MCP surface does not consume a durable prior EXECUTE
record. Before trust is used in an adversarial setting, proposal, execution, outcome,
and attestation must be linked.

## DR-5: Three routing outcomes {#sec:dr-three-state}

EXECUTE, HOLD, and REFUSE distinguish three operational states:

- EXECUTE returns an advisory approval verdict to the caller;
- HOLD requests revision, evidence, budget recovery, or later reevaluation; and
- REFUSE rejects the proposal and, in the integrated path, deposits FAILURE pressure.

HOLD is useful only when revision can change a relevant input at acceptable cost. The
release therefore does not claim that a three-way gate universally dominates a binary
one. A benchmark must measure revision cost, delay, eventual decision, throughput, and
outcome quality. The integrated and standalone budget paths also differ: an integrated
budget failure yields HOLD, while the standalone gate with its own ledger returns
REFUSE. Callers must choose the intended API rather than assume the labels are
interchangeable.

## DR-6: Deterministic falsification before scoring {#sec:dr-falsification}

The integrated proposal path runs deterministic checks before gate scoring. The checks
cover {{CONFIG_FALSIFICATION_VECTORS}} canonical `AttackVector` categories through
{{CONFIG_FALSIFICATION_CHECK_COUNT}} check functions. This order
makes findings available to the gate and makes the same input replayable without an LLM
call.

Deterministic heuristics have bounded, inspectable behavior, but they detect only the
patterns they implement. The current checks top out at HIGH severity; CRITICAL remains
an input class that would trigger the hard override. A clean report is not proof that a
proposal is safe, and returning REFUSE does not physically prevent a separate caller
from bypassing the kernel. Stronger deployments need an execution boundary that
requires a consumed gate authorization, plus external isolation and monitoring.

## DR-7: Role labels separated from action-type policy {#sec:dr-roles}

The trust-score path maps profiles onto {{CONFIG_ROLE_COUNT}} labels: SANDBOX, REPAIR_ANT, MEMORY_ANT,
DISPATCHER, and GUARD_ANT. The labels provide a readable lifecycle summary, and SANDBOX
is an actual early gate refusal. The other four labels do not currently enforce distinct
action-type matrices in `ActuationGate`.

This separation is important. A label taxonomy is inexpensive and auditable, but it is
not a complete access-control system. The default lifecycle also has a bootstrap gap:
new profiles begin in SANDBOX, the gate refuses their proposals, and trust rises only
through submitted outcomes. An external study must either supply a fixed supervised
calibration history or implement a narrowly constrained, attested SANDBOX path.

## DR-8: Shared location field rather than peer messaging {#sec:dr-stigmergy}

The pheromone field lets later proposals query pressure by location and signal type
without reconstructing every prior consequence record. It supports the paper's bounded
locality claim: a failure at one target can affect that target while an unrelated target
remains unchanged.

The current implementation is a central in-process store, not a distributed stigmergic
network. The release makes no asymptotic communication claim because actual cost depends
on index structure, query pattern, agent topology, and synchronization design. A shared
field reduces the API needed for the tested single-process case; it also creates a
single-process state boundary and supplies no cross-host consistency protocol.

## DR-9: Advisory pruning with a separate destructive API {#sec:dr-pruning}

`PruningDaemon.report()` and the MCP `colony_pruning_report` surface candidates; they do
not move files. `PruningDaemon.archive(candidate, dry_run=True)` is also non-mutating by
default. A direct caller can pass `dry_run=False`, in which case the implementation moves
an existing in-repository path under `docs/plans/archived/` after a containment check.

Keeping discovery separate from mutation makes review possible and prevents the MCP
report tool from silently archiving code. The tradeoff is procedural: safety depends on
which callers can invoke the lower-level archive method and on reviewing false-positive
candidates. Confidence scores are heuristic rankings, not calibrated probabilities,
and DEPENDENCY pressure is a veto signal only within the implemented scan rules.

## Generated figure inventory

The release route generates the {{ARTIFACT_FIGURE_COUNT}} assets in [@tbl:appendix-figures]. Captions in the
body state the fixed inputs and permitted inference; this inventory makes the distinction
between conceptual, formula-derived, and deterministic-fixture graphics explicit.

| Asset and evidence class | Intended reading and explicit limit |
|---|---|
| `cover.png` — conceptual cover | Visual identity and subsystem motif; no quantitative evidence. |
| `subsystem_architecture.png` — architecture | Kernel ownership of {{CONFIG_OPERATIONAL_SUBSYSTEM_COUNT}} operational components; no latency or distributed-topology claim. |
| `colony_pressure_loop.png` — dependency diagram | Proposal, decision, report, and later-state dependencies; not a literal call trace or autonomous execution. |
| `pheromone_decay.png` — formula-derived | Passive unit-trace paths; not empirical frequency or wall-clock half-life. |
| `gate_score_heatmap.png` — formula-derived | Policy bands over trust and effective hazard; not an observed distribution or calibrated risk. |
| `gate_score_3d.png` — formula-derived | Score envelope over trust and completeness; runtime inputs remain discrete. |
| `trust_trajectory.png` — deterministic fixture | Fixed clean-report updates and label thresholds; not autonomous learning or convergence. |
| `falsification_vectors.png` — code taxonomy | Implemented categories and representative severities; not prevalence, recall, or effectiveness. |
| `fep_correspondence.png` — conceptual analogy | Vocabulary crosswalk; not Bayesian inference, EFE optimization, or formal equivalence. |
: Generated figure registry and evidence class. {#tbl:appendix-figures}

Every generator reads the manuscript variable snapshot and stamps a version, compact
configuration digest, and generation date. As explained in [@sec:reproducibility], that
footer identifies the manuscript configuration used by the figure route; it does not
hash all source or authenticate the image. The generated `figure_registry.json` adds
an evidence-class label, byte size, and full SHA-256 for each PNG file;
it is an integrity inventory for the emitted files, not an external signature.

## Calibration and replacement criteria {#sec:dr-weight-calibration}

The gate weights and thresholds were selected as design constants. Replacing them with
new hand-set values would change policy, not add evidence. A defensible calibration
study should provide representative proposals, consumed execution records, independently
attested outcomes, costs of HOLD/revision, pre-registered metrics, held-out evaluation,
and calibration diagnostics. A learned policy should remain subordinate to named hard
conditions unless the study separately justifies changing those conditions.

The same replacement discipline applies to every decision in this appendix. A real-time
field should be judged against replayability and scheduler failures; a durable state
backend against migration and recovery tests; role-specific action policies against an
explicit matrix; and automated pruning against measured false-positive costs. The
present design is valuable because its boundaries are testable—not because it is the
final design for every deployment.

## Summary {#sec:dr-summary}

The released design favors small deterministic mechanisms with inspectable inputs and
explicit limitations. That choice enables the paired locality result and exact policy
figures reported in [@sec:results]. It does not establish external effectiveness,
adversarial integrity, restart continuity, or optimal calibration. Those claims require
the additional evidence package specified in [@tbl:external-evidence].
