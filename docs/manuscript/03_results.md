# Verified Implementation Results {#sec:results}

This section reports only evidence reproducible from the checked-in Colony Kernel. It
distinguishes:

- **executed quality gates**: scoped tests, branch coverage, lint, and static typing;
- **deterministic contract cases**: exact inputs evaluated by real subsystem instances;
- **analytical consequences**: arithmetic derived from the implemented score; and
- **unexecuted evaluation plans**: the comparative benchmark specified in
  [@sec:experimental-design].

No raw multi-condition benchmark trace ships with this snapshot. Accordingly, this
section reports no production effect size, confidence interval, ecological optimum, or
population-level safety rate.

## Executed quality gates {#sec:results-quality}

The fail-closed manuscript generator reruns the Colony Kernel tests and refuses to emit
release variables if pytest, Ruff, or ty returns non-zero. [@tbl:quality_gates] is
therefore a snapshot of executed release gates, not a manually entered scorecard.

| Gate | Snapshot result | Interpretation |
|---|---:|---|
| pytest | {{RESULT_TEST_PASSED}} passing of {{RESULT_TEST_COLLECTED}} collected tests | Real tests under `tests/unit/colony_kernel/`; skipped={{RESULT_TEST_SKIPPED}}, failed={{RESULT_TEST_FAILED}}, errors={{RESULT_TEST_ERRORS}} |
| branch coverage | {{RESULT_COVERAGE_PCT}}% | Scoped to `src/codomyrmex/colony_kernel` |
| Ruff | {{RESULT_RUFF_ERRORS}} findings | Zero required for variable generation |
| ty | {{RESULT_TY_ERRORS}} diagnostics | Zero required for variable generation |
: Executed Colony Kernel quality gates for the rendered snapshot. {#tbl:quality_gates}

The suite spans {{ARTIFACT_TEST_SUITES}} test modules and exercises the
{{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} named subsystems, their integration class, and the
{{CONFIG_MCP_TOOL_COUNT}}-tool MCP adapter. Coverage and passing tests establish exercised behavior under
the suite; they do not establish that untested faults, adversarial outcome reports, or
deployment failures are absent.

The source snapshot contains {{RESULT_COLONY_KERNEL_LOC}} nonblank, noncomment lines
across {{RESULT_COLONY_KERNEL_FILES}} top-level Colony Kernel Python files. These counts
describe scope, not quality. The exact commands and evidence limitations are recorded in
[@sec:reproducibility].

## Paired locality contract {#sec:results-locality}

The central implemented claim is evaluated as a paired deterministic case using a real
`ColonyKernel`, `PheromoneStore`, `ActuationGate`, and in-memory
`ConsequenceMemory`—without mocks.

The fixture uses an authorized agent with trust {{RESULT_PAIRED_AGENT_TRUST}}, no recent failures, a fully
specified proposal, an available budget, and an initially clear target. It then records a
failed outcome at that target from another agent and reevaluates both the same target and
an unrelated target. [@tbl:paired-locality] gives the exact results.

| Evaluation | Local RISK | Local FAILURE | Effective hazard | Score | Decision |
|---|---:|---:|---:|---:|---|
{{RESULT_PAIRED_LOCALITY_ROWS}}
: Paired same-target inhibition, cross-target isolation, and decay recovery. {#tbl:paired-locality}

The failed outcome deposits nominal FAILURE strength {{CONFIG_CANONICAL_FAILURE_STRENGTH}}
from source TEST. The {{CONFIG_SOURCE_MULTIPLIER_TEST}} source multiplier yields pressure
{{RESULT_PAIRED_FAILURE_PRESSURE}}, changing the hazard credit from full to medium. The
resulting score change is

$$
\Delta g={{CONFIG_GATE_WEIGHT_RISK}}({{CONFIG_RISK_CREDIT_MEDIUM}}-1)
={{RESULT_PAIRED_SCORE_CHANGE}} .
$$ {#eq:paired-score-change}

The test also establishes locality: the unrelated target is unchanged. A second test
establishes reversibility after passive decay. These facts support a bounded statement:
the recorded failure increases friction for later same-location action in the running
process. They do not show that the original outcome report was truthful, that the effect
persists across restarts, or that the gate reduces real-world harm.

## Gate landscape and attainable scores {#sec:results-gate}

The ordinary gate score has {{CONFIG_GATE_COMPONENT_COUNT}} non-negative weighted components. Because trust credit,
hazard credit, and completeness are discrete, not every real number in $[0,1]$ is
attainable.

For a lower-tier authorized agent with clear budget and hazard, the score is

$$
g(c)=w_b+w_r+w_t\,t_{\mathrm{lower}}+w_c c,
$$ {#eq:lower-tier-score}

Each coefficient and the lower trust credit are injected from the live gate. Runtime
completeness has a finite attainable set because each missing field incurs the generated
penalty. Thus the threshold is exact while the discrete input mapping can create gaps;
the generated cases below expose those gaps without a second arithmetic source in prose.

[@tbl:representative-gates] records representative, formula-checked cases.

| Condition | Budget credit | Hazard credit | Trust credit | Completeness | Score | Decision |
|---|---:|---:|---:|---:|---:|---|
{{RESULT_REPRESENTATIVE_GATE_ROWS}}
: Representative hard-override and ordinary gate cases. {#tbl:representative-gates}

[@fig:gate_heatmap] visualizes the controlled slice with budget and completeness fixed at
1.0 and no recent-failure penalty. The vertical discontinuities come from the trust hard
floor and trust-credit tier; the horizontal discontinuities come from effective hazard
thresholds at {{CONFIG_HAZARD_MEDIUM_THRESHOLD}} and {{CONFIG_HAZARD_HIGH_THRESHOLD}}. The pressure axis should be read as
$\max(\mathrm{RISK},\mathrm{FAILURE})$, not RISK alone.

![Formula-derived gate decision landscape over trust and effective local hazard pressure, where hazard is the maximum of RISK and FAILURE. Budget approval and completeness are fixed at 1.0; no recent-failure trust penalty or falsification override is applied. Colours encode configured decision bands, while the black strip is the trust hard override. This is an analytical policy map, not an observed proposal distribution.](figures/gate_score_heatmap.png){#fig:gate_heatmap width=90%}

## Trust accounting path {#sec:results-trust}

A new profile begins at trust {{CONFIG_TRUST_SANDBOX_SCORE}} and role SANDBOX. Along the artificial all-success
path, each recorded clean outcome adds {{CONFIG_TRUST_DELTA_PASS}}. [@tbl:trust_trajectory] reports exact
checkpoints.

| Recorded outcomes | Trust | Inferred role | Gate implication |
|---:|---:|---|---|
{{RESULT_TRUST_TRAJECTORY_ROWS}}
: Deterministic all-success trust path from the default profile. {#tbl:trust_trajectory}

The role ladder's first threshold ({{CONFIG_ROLE_REPAIR_THRESHOLD}}) is below the gate's
independent trust hard floor ({{CONFIG_TRUST_HARD_FLOOR}}). Exiting SANDBOX therefore
does not itself authorize a proposal.

[@fig:trust_trajectory] plots this deterministic path. It is not a convergence plot:
alternating or stochastic outcomes need not converge, and the current constant-step
clipped update has no restoring term.

![Deterministic trust trajectory under consecutive caller-reported clean outcomes. Shaded bands show inferred role labels; the independent generated gate floor means the first role promotion does not yet make ordinary gate scoring reachable. Points are analytical applications of the fixed update, not population measurements or evidence of stochastic convergence.](figures/trust_trajectory.png){#fig:trust_trajectory width=90%}

The fixture is also not an attested credential protocol. The current MCP outcome tool
does not require a matching prior EXECUTE record, so an operator or client can submit
the reports that drive this path. This is a deployment blocker for adversarial trust.

## Subtractive signal dynamics {#sec:results-decay}

The field subtracts {{CONFIG_EVAPORATION_FAST}}, {{CONFIG_EVAPORATION_NORMAL}}, or
{{CONFIG_EVAPORATION_SLOW}} per tick for FAST, NORMAL, or SLOW traces,
respectively, then removes traces at zero. [@tbl:linear-decay-values] gives the exact
integer-tick path for a unit deposit with no reinforcement.

| Tick | FAST | NORMAL | SLOW |
|---:|---:|---:|---:|
{{RESULT_DECAY_ROWS}}
: Exact passive decay of a unit trace under each class. {#tbl:linear-decay-values}

Accordingly, a FAST unit trace has lost
{{RESULT_PHEROMONE_FAST_LOSS_REPORT_TICK_PCT}}% after
{{CONFIG_DECAY_REPORT_TICK}} ticks, while a SLOW unit trace retains
{{RESULT_PHEROMONE_SLOW_RETENTION_REPORT_TICK_PCT}}%. [@fig:pheromone_decay] plots
the same recurrence continuously for legibility and states the integer-tick runtime
interpretation in its caption.

## MCP state and interface boundary {#sec:results-mcp}

The package exposes the {{CONFIG_MCP_TOOL_COUNT}} MCP tools summarized in [@tbl:mcp-tools].

| Tool | State effect |
|---|---|
| `colony_propose_action` | Runs falsification and gate evaluation; may deposit traces |
| `colony_record_outcome` | Accepts a reported outcome; updates memory, budget, trust, role, and traces |
| `colony_execute_authorized` | Strict-only capability consumption and signed executor receipt |
| `colony_record_attested_outcome` | Strict-only receipt-linked consequence update |
| `colony_action_scope` | Reads declared scope and bypass behavior |
| `colony_agent_profile` | Reads one profile |
| `colony_status` | Reads the kernel snapshot |
| `colony_pheromone_query` | Reads typed pressure |
| `colony_falsify_plan` | Runs deterministic heuristic review; may deposit traces |
| `colony_pruning_report` | Reads pruning candidates |
| `colony_tick` | Advances decay and period-reset checks |
: Colony Kernel MCP interface and state effects. {#tbl:mcp-tools}

Requests and responses are self-contained JSON-shaped documents, but calls are not
stateless. A module-level `ColonyKernel` singleton shares state across calls within one
server process. Advisory mode retains the process-local default. A strict file-backed
profile persists consequence, authorization, receipt, pheromone, and resource state with
SQLite WAL; `:memory:` remains isolated-test mode.

The strict path closes the proposal–outcome linkage gap for declared actions:
`colony_propose_action` can return a durable signed capability, the executor consumes it
once, and `colony_record_attested_outcome` requires the resulting receipt. The advisory
outcome tool remains intentionally report-dependent; in strict mode it quarantines
unknown, refused, mismatched, duplicate, and unlinked reports without changing trust or
failure evidence. Actions outside the declared scope remain a documented bypass.

## What has not been measured {#sec:results-not-measured}

The current release has not executed the proposed {{CONFIG_TRIAL_COUNT}}-trial,
{{CONFIG_BENCHMARK_CONDITION_COUNT}}-condition benchmark.
Consequently:

- the configured trial count is a protocol parameter, not a sample size already observed;
- no refusal percentage is reported as an empirical result;
- no baseline comparison or hypothesis test has been run;
- no throughput, error-rate, budget-efficiency, or trust-stability effect size is
  claimed; and
- the figures in this paper are code-taxonomy, formula-derived, or deterministic-fixture
  visualizations—not plots of an external agent population.

This boundary is a result in its own right: it identifies exactly what the internal
contract suite establishes and what the next empirical study must supply.
