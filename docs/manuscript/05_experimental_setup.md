# Evaluation Protocol, Configuration, and Reproducibility Inputs {#sec:experimental_setup}

This section separates a **proposed external benchmark** from the configuration and
contract checks that were actually executed for this release. The comparative benchmark
has not been run, its baselines are not implemented as released adapters, and no raw
trial traces are included. Its purpose here is to make the next empirical test explicit
without presenting planned work as evidence.

**Parameter status.** {{CONFIG_PARAMETER_STATUS_NOTE}} The protocol values reserved in
this section are therefore starting points for a preregistered study, not observations
or claims about the correct operating point. A study should report every changed value,
its authority (runtime policy, configuration, or presentation), and the regenerated
artifact hashes.

[@tbl:parameter-classes] makes the distinction explicit before the proposed trial
design and the live runtime configuration are described.

| Parameter class | Examples in this release | Interpretation and authority |
|---|---|---|
| Runtime policy | Gate weights, thresholds, trust deltas, decay constants | Current code-defined behavior; tune by changing the runtime policy and rerun the contract suite. |
| Presentation | Plot horizon, grid density, trust slices, checkpoint selection | Reproducible display choices; tune without changing kernel semantics, but regenerate figures and captions. |
| Proposed protocol | Agent count, workload size, warm-up, trial count, seed, baseline conditions | Initial study-design values; they are not completed experiments or observed sample sizes. |
: Parameter classes, authorities, and evidence interpretation for the current snapshot. {#tbl:parameter-classes}

## Evidence-status map {#sec:experimental-design}

[@tbl:evidence-status] is the release's claim-status ledger.

| Evidence surface | Release status | Permitted inference |
|---|---|---|
| Colony Kernel unit/integration suite | Executed during variable generation | Checked deterministic behavior under test inputs |
| Ruff and ty checks | Executed; fail closed | No scoped lint/type diagnostics in this snapshot |
| Formula-derived figures and tables | Regenerated from configuration and constants | Arithmetic consequences of the policy |
| Local authenticated lifecycle ledger | Executed deterministic fixture | Hash/signature/linkage integrity, not external actuation truth |
| {{CONFIG_BENCHMARK_CONDITION_COUNT}}-condition benchmark | Proposed, not executed | No comparative conclusion |
| Production deployment study | Absent | No production safety or performance conclusion |
: Evidence status for the release and proposed study. {#tbl:evidence-status}

### Proposed independent variable {#sec:independent-variables}

The proposed study varies the gate policy while holding the ordered workload and reported
outcomes constant:

1. **Composite gate** — the released budget, local hazard, trust, completeness, role,
   and falsification policy.
2. **Static-trust baseline** — a future adapter using only an explicitly specified
   trust threshold.
3. **Budget-only baseline** — a future adapter using only resource approval.
4. **Always-execute baseline** — a future unsafe control that dispatches every proposal.

Conditions 2–4 are design specifications, not checked-in drop-in implementations.
Implementing and testing them is a prerequisite to executing the benchmark.

### Proposed dependent variables {#sec:dependent-variables}

[@tbl:dependent_variables] defines the outcomes that a future benchmark must actually
record rather than infer from gate decisions alone.

| Variable | Required operational definition |
|---|---|
| Decision distribution | EXECUTE/HOLD/REFUSE counts per condition and paired workload item |
| Externally attested failure rate | Failed, independently observed outcomes divided by consumed EXECUTE authorizations |
| Budget efficiency | Consumed resource units per externally attested successful task |
| Trust path | Per-agent trust before and after every consumed outcome record |
| Throughput | Externally attested completed workload items per run |
| Recovery latency | Proposals/ticks from first HOLD until EXECUTE, REFUSE, or expiry |
: Outcomes required for the proposed benchmark. {#tbl:dependent_variables}

### Falsifiable hypotheses {#sec:baseline-conditions}

The study should test, rather than assume:

- **H1:** the composite gate lowers externally attested failure rate relative to always-execute;
- **H2:** same-target failure has a larger subsequent gate effect than failure at an
  unrelated target;
- **H3:** HOLD provides positive value after accounting for revision cost and delay; and
- **H4:** safety changes are not explained solely by reduced execution volume.

A lower raw error count is insufficient if a policy simply executes less. Results must
report denominators, throughput, and paired workload effects.

### Proposed trial structure {#sec:trial-structure}

The checked-in configuration reserves {{CONFIG_TRIAL_COUNT}} run indices,
{{CONFIG_AGENT_COUNT}} agents, {{CONFIG_WORKLOAD_TASK_COUNT}} workload items, and
{{CONFIG_WARMUP_TICKS}} warm-up ticks. These are planning parameters only. Before use,
the study must provide:

- a versioned workload with stable item identifiers;
- deterministic seeds or a declaration that the run is fully deterministic;
- implemented baseline adapters;
- an authorization ledger linking proposal ID, decision, execution, and one consumed
  outcome;
- an independent outcome oracle or attestation rule;
- raw append-only traces with configuration and commit hashes; and
- an analysis script that regenerates every reported table and confidence interval.

“Independent trial” should be used only when randomness or independently sampled
workloads justify independence. Replaying an identical deterministic trace produces
replications for reproducibility, not independent statistical samples.

### Trust initialization and bootstrap {#sec:trust-initialization}

The default profile begins at trust {{CONFIG_TRUST_SANDBOX_SCORE}} and SANDBOX. The current gate refuses all
SANDBOX proposals, including read-only actions, while trust increases only through
reported outcomes. Consequently, a trial cannot bootstrap autonomously from this state.
A credible benchmark must choose and document one of two approaches:

1. provide a fixed, supervised calibration history before measurement; or
2. implement a restricted SANDBOX action path with local lifecycle authentication and
   deployment-specific external observation.

The present all-success trajectory is a deterministic contract fixture using submitted
outcomes. It must not be described as naturally earned autonomous authority.

### Proposed analysis {#sec:analysis-procedure}

For paired workload items, report condition-by-item decisions and outcomes before
aggregate statistics. Binary externally attested failure outcomes can be analyzed with paired
methods or a mixed-effects model that accounts for workload and agent. Ternary gate
decisions require a multinomial or ordinal model appropriate to the design. Pre-register
exclusions, multiplicity correction, missing-outcome treatment, and stopping rules.
Effect sizes with uncertainty intervals are primary; significance tests are secondary.

## Runtime gate configuration {#sec:gate-configuration}

The integrated kernel runs falsification, checks the budget, loads the agent profile,
updates its role label, and evaluates the gate. [@tbl:experimental_gate_thresholds] gives
the configured routing bands.

| Outcome | Condition on ordinary score | Runtime meaning |
|---|---|---|
| EXECUTE | score ≥ {{CONFIG_GATE_EXECUTE_THRESHOLD}} | Caller may actuate |
| HOLD | {{CONFIG_GATE_HOLD_THRESHOLD}} ≤ score < {{CONFIG_GATE_EXECUTE_THRESHOLD}} | Return revision/recovery requirements |
| REFUSE | score < {{CONFIG_GATE_HOLD_THRESHOLD}} | Reject and deposit FAILURE |
: Ordinary gate routing thresholds. {#tbl:experimental_gate_thresholds}

Budget failure, SANDBOX, trust below {{CONFIG_TRUST_HARD_FLOOR}}, and CRITICAL falsification are evaluated as
early returns. Integrated budget failure yields HOLD; standalone gate use yields REFUSE.
The score is a policy value, not a calibrated probability.

### Gate weights {#sec:gate-score-weights}

[@tbl:experimental_gate_weights] identifies each ordinary score component and its live
runtime input.

| Component | Weight | Runtime input |
|---|---:|---|
| Budget | {{CONFIG_GATE_WEIGHT_BUDGET}} | Binary result of the resource pre-check |
| Local hazard | {{CONFIG_GATE_WEIGHT_RISK}} | Piecewise credit from max(RISK, FAILURE) |
| Trust | {{CONFIG_GATE_WEIGHT_TRUST}} | Tiered trust credit with optional recent-failure penalty |
| Completeness | {{CONFIG_GATE_WEIGHT_COMPLETENESS}} | Presence of rollback, evidence, and expected outcome |
: Ordinary gate score components. {#tbl:experimental_gate_weights}

Weights and thresholds are code-defined policy constants with documentation mirrors in
YAML. The current release has not calibrated them against external outcomes.

## Signal-field configuration {#sec:pheromone-configuration}

{{CONFIG_SIGNAL_TYPES_COUNT}} `SignalType` values share a capped field. Each trace stores its own subtractive
evaporation amount at deposit time; [@tbl:experimental_decay_rates] reports the
{{CONFIG_DECAY_RATES_COUNT}}
configured classes.

| Class | Subtraction per tick | Unit trace at report tick | Typical channels |
|---|---:|---:|---|
| FAST | {{CONFIG_EVAPORATION_FAST}} | {{RESULT_PHEROMONE_FAST_LOSS_REPORT_TICK_PCT}}% lost | FAILURE, RISK |
| NORMAL | {{CONFIG_EVAPORATION_NORMAL}} | generated in [@tbl:linear-decay-values] | NEED/default |
| SLOW | {{CONFIG_EVAPORATION_SLOW}} | {{RESULT_PHEROMONE_SLOW_RETENTION_REPORT_TICK_PCT}}% retained | SUCCESS, DEPENDENCY, HUMAN_PRIORITY |
: Linear field dynamics for a unit trace without reinforcement. {#tbl:experimental_decay_rates}

The runtime caps field strength at {{CONFIG_FIELD_MAX_STRENGTH}} and floors at zero. Deposits can have source and
trust multipliers, so lifetime scales with effective initial strength. The model does
not use exponential half-lives.

## Resource caps {#sec:resource-budget-caps}

Values in [@tbl:resource_budget_caps] are loaded from
`config/colony_kernel/kernel.yaml` by the manuscript generator.

| Dimension | Cap |
|---|---:|
| LLM calls | {{CONFIG_BUDGET_MAX_LLM_CALLS}} |
| Runtime seconds | {{CONFIG_BUDGET_MAX_RUNTIME}} |
| Cumulative risk level | {{CONFIG_BUDGET_MAX_RISK}} |
| Security exposure | {{CONFIG_BUDGET_MAX_SECURITY}} |
: Selected period-scoped resource budget caps. {#tbl:resource_budget_caps}

The ledger has {{CONFIG_BUDGET_DIMENSIONS_COUNT}} dimensions in total. The pre-check does not consume resources;
`record_outcome` consumes a caller-supplied cost when valid or falls back to the
proposal estimate.

## Role labels {#sec:role-configuration}

[@tbl:role_ladder] distinguishes inferred labels from the authorization behavior that is
actually enforced.

| Role | Trust threshold after ≥{{CONFIG_ROLE_MIN_PROPOSALS}} records | Live authorization behavior |
|---|---:|---|
| SANDBOX | entry/default | Every proposal hard-refused |
| REPAIR_ANT | {{CONFIG_ROLE_REPAIR_THRESHOLD}} | No role-specific action matrix beyond leaving SANDBOX |
| MEMORY_ANT | {{CONFIG_ROLE_MEMORY_THRESHOLD}} | No role-specific action matrix |
| DISPATCHER | {{CONFIG_ROLE_DISPATCHER_THRESHOLD}} | No role-specific action matrix |
| GUARD_ANT | {{CONFIG_ROLE_GUARD_THRESHOLD}} | No role-specific action matrix |
: Inferred role labels and current enforcement boundary. {#tbl:role_ladder}

The labels encode a deterministic ladder and intended specializations. They should not be
reported as enforced capabilities until the gate validates action type against role.

## Falsification categories {#sec:falsification-vectors}

The worker runs {{CONFIG_FALSIFICATION_CHECK_COUNT}} checks grouped into these
{{CONFIG_FALSIFICATION_VECTORS}} enum categories:

1. `SECURITY_RISK`
2. `NO_ROLLBACK`
3. `NO_TEST_VALUE`
4. `SCOPE_CREEP`
5. `CIRCULAR_ARCHITECTURE`
6. `FALSE_METRIC`
7. `HIDDEN_MAINTENANCE_COST`
8. `DEPENDENCY_RISK`
9. `OVER_BROAD_MODULE`
10. `PREMATURE_ABSTRACTION`

HIGH or CRITICAL findings deposit FAILURE; MEDIUM findings deposit RISK. Only CRITICAL
findings are gate hard overrides. The worker's PASS/CONDITIONAL/FAIL report is not itself
the gate decision.

## Configuration provenance {#sec:yaml-configuration-files}

{{CONFIG_YAML_CONFIG_FILES}} YAML files under `config/colony_kernel/` document/load kernel budget policy, role
metadata, and decay metadata. Runtime authority is mixed:

- `kernel.yaml` is loaded for budget defaults and carries documentation mirrors for
  some gate constants;
- promotion thresholds are private constants in `role_adapter.py`;
- gate weights, hazard thresholds, completeness penalty, and hard floor are constants
  in `actuation_gate.py`; and
- per-trace evaporation is derived from `DecayRate` and the base store constant.

The manuscript therefore identifies each value's runtime authority instead of claiming
that every parameter is dynamically configurable. {{CONFIG_PARAMETER_STATUS_NOTE}}

## Software snapshot {#sec:software-environment-setup}

[@tbl:software_environment] records the build-facing tools and generated snapshot facts.

| Component | Snapshot |
|---|---|
| Python | {{PYTHON_VERSION}} |
| Package manager | uv |
| Test runner | pytest + pytest-cov |
| Linter | Ruff |
| Type checker | ty |
| Config version | {{CONFIG_VERSION}} |
| Generated | {{GENERATION_TIMESTAMP}} |
: Software used to generate the release evidence. {#tbl:software_environment}

“Generated” is an artifact timestamp. Exact dependency resolution comes from `uv.lock`,
not from version ranges in prose.

## Manuscript pipeline {#sec:pipeline-ordering}

The authoritative route runs from the repository root. Its locked dependency group and
explicit paths avoid relying on a template project or an untracked wrapper:

```bash
uv sync --locked --group docs
uv run --locked python scripts/z_generate_manuscript_variables.py
uv run --locked python scripts/generate_manuscript_figures.py
uv run --locked --group docs python scripts/compile_manuscript.py \
  --manuscript-dir output/manuscript --output-dir output --check --skip-generate
uv run --locked --group docs python scripts/compile_manuscript.py \
  --manuscript-dir output/manuscript --output-dir output \
  --pdf --bookends --pdf-engine lualatex --pdf-standard ua-2 --skip-generate
uv run --locked python scripts/validate_manuscript_integrity.py \
  --require-rendered --online-bibliography
```

Variable generation reruns the scoped tests, branch coverage, Ruff, and ty checks and
fails on a non-zero gate. Figure generation reads that snapshot and produces the
{{ARTIFACT_FIGURE_COUNT}} registered images. Compilation hydrates Markdown, resolves
cross-references and citations, renders semantic HTML, hashes an unbookended content
PDF, then produces the final distribution PDF with visible first/last bookends in one
Pandoc/LaTeX pass. The final PDF hash belongs only in the detached publication manifest,
which avoids circular self-hashing.

This route binds internal evidence to `{{ARTIFACT_COMBINED_PDF_PATH}}`,
`output/paper-content.pdf`, and `output/paper.html`. It does not prove that the proposed
external benchmark has been executed or that the requested PDF standard conforms until
an external validator reports success.
