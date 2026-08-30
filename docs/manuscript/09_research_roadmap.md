# Research Roadmap: Evidence Gates and Dependency Order {#sec:research-roadmap}

{{CONFIG_PARAMETER_STATUS_NOTE}} This roadmap is a scoped research program, not a
catalogue of completed results. The current paper establishes the reproducible kernel
contract, a fixed-input paired replay artifact, and the local authenticated lifecycle
ledger. Subsequent milestones are conditional on their artifacts, metrics, falsifiers,
and exit criteria. A status label therefore describes evidence available in the current
repository, not a promise about delivery or scientific success.

## Research question and boundary

The central question is whether a proposal-governance control plane can improve the
safety--utility trade-off of agentic software work when its state is authenticated,
evaluated under hostile inputs, and calibrated against independently observed
consequences. The implementation currently supports a narrower statement: a
caller-reported failure changes same-target local pressure in a running kernel process,
and the deterministic gate responds according to its configured rule. The roadmap does
not promote that mechanism into a claim of harm reduction, optimality, collective
intelligence, or Active Inference.

The milestones are ordered by dependency. Replayable artifacts must precede external
comparisons; local lifecycle authentication must precede deployment-specific external
observation; externally attested outcomes must precede trust calibration; adversarial
and held-out evaluation must precede claims about utility; and persistence/concurrency
evidence must precede deployment-oriented interpretation. This ordering follows
reproducibility and accountability principles rather than a calendar commitment
[@peng2011reproducible; @raji2020accountability; @buhl2024safetycases].

The synthetic benchmark record retains `{{RESULT_BENCHMARK_PAIR_COUNT}}` paired
observations with sample unit `{{RESULT_BENCHMARK_SAMPLE_UNIT}}`, the case-manifest
digest `{{RESULT_BENCHMARK_CASE_MANIFEST_SHA256}}`, paired execution volumes of
`{{RESULT_BENCHMARK_EXECUTIONS_BASELINE}}` and
`{{RESULT_BENCHMARK_EXECUTIONS_MEDIATED}}`, and the difference direction
`{{RESULT_BENCHMARK_HARM_DIFFERENCE_DIRECTION}}`. Its interval uses
`{{RESULT_BENCHMARK_CI_METHOD}}` at a nominal `{{RESULT_BENCHMARK_CI_LEVEL}}%`
resampling reference level; `{{RESULT_BENCHMARK_INTERVAL_INTERPRETATION}}`.
The plotted mediator is `{{RESULT_BENCHMARK_MEDIATOR_PROVENANCE}}`, and production
gate parity is `{{RESULT_BENCHMARK_PRODUCTION_GATE_PARITY}}`. These metadata bind the
displayed fixture to its ordered task cases; they do not turn synthetic pairs into an
estimate of population risk or utility.

![{{FIGURE_CAPTION_RESEARCH_ROADMAP}}](figures/{{FIGURE_FILENAME_RESEARCH_ROADMAP}}){#{{FIGURE_LABEL_RESEARCH_ROADMAP}} width={{FIGURE_WIDTH_RESEARCH_ROADMAP}} alt="{{FIGURE_ALT_RESEARCH_ROADMAP}}" aria-describedby="{{FIGURE_LABEL_RESEARCH_ROADMAP}}-description"}
<div id="{{FIGURE_LABEL_RESEARCH_ROADMAP}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_RESEARCH_ROADMAP}}</div>

The first executable evidence fixtures are separated by what they can and
cannot establish. The attestation chain binds local lifecycle events, the
paired benchmark exposes the safety--utility analysis plumbing, and the
persistence fixture checks restart state. None is an external benchmark,
causal estimate, or production security guarantee.
The figures below are generated artifacts with declared boundaries, not evidence
that the later research milestones have been completed.

![{{FIGURE_CAPTION_ATTESTATION_EVENT_CHAIN}}](figures/{{FIGURE_FILENAME_ATTESTATION_EVENT_CHAIN}}){#{{FIGURE_LABEL_ATTESTATION_EVENT_CHAIN}} width={{FIGURE_WIDTH_ATTESTATION_EVENT_CHAIN}} alt="{{FIGURE_ALT_ATTESTATION_EVENT_CHAIN}}" aria-describedby="{{FIGURE_LABEL_ATTESTATION_EVENT_CHAIN}}-description"}
<div id="{{FIGURE_LABEL_ATTESTATION_EVENT_CHAIN}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_ATTESTATION_EVENT_CHAIN}}</div>

![{{FIGURE_CAPTION_SAFETY_UTILITY_FRONTIER}}](figures/{{FIGURE_FILENAME_SAFETY_UTILITY_FRONTIER}}){#{{FIGURE_LABEL_SAFETY_UTILITY_FRONTIER}} width={{FIGURE_WIDTH_SAFETY_UTILITY_FRONTIER}} alt="{{FIGURE_ALT_SAFETY_UTILITY_FRONTIER}}" aria-describedby="{{FIGURE_LABEL_SAFETY_UTILITY_FRONTIER}}-description"}
<div id="{{FIGURE_LABEL_SAFETY_UTILITY_FRONTIER}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_SAFETY_UTILITY_FRONTIER}}</div>

![{{FIGURE_CAPTION_CALIBRATION_RELIABILITY}}](figures/{{FIGURE_FILENAME_CALIBRATION_RELIABILITY}}){#{{FIGURE_LABEL_CALIBRATION_RELIABILITY}} width={{FIGURE_WIDTH_CALIBRATION_RELIABILITY}} alt="{{FIGURE_ALT_CALIBRATION_RELIABILITY}}" aria-describedby="{{FIGURE_LABEL_CALIBRATION_RELIABILITY}}-description"}
<div id="{{FIGURE_LABEL_CALIBRATION_RELIABILITY}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_CALIBRATION_RELIABILITY}}</div>

![{{FIGURE_CAPTION_PERSISTENCE_RECOVERY}}](figures/{{FIGURE_FILENAME_PERSISTENCE_RECOVERY}}){#{{FIGURE_LABEL_PERSISTENCE_RECOVERY}} width={{FIGURE_WIDTH_PERSISTENCE_RECOVERY}} alt="{{FIGURE_ALT_PERSISTENCE_RECOVERY}}" aria-describedby="{{FIGURE_LABEL_PERSISTENCE_RECOVERY}}-description"}
<div id="{{FIGURE_LABEL_PERSISTENCE_RECOVERY}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_PERSISTENCE_RECOVERY}}</div>

The roadmap in [@fig:research_roadmap] is a dependency map, not a delivery timeline. Its future
milestones are planning objects and must not be read as empirical evidence.

The first offline research fixtures are shown alongside the roadmap: the authenticated
event chain in [@fig:attestation_event_chain], the paired safety--utility plumbing in
[@fig:safety_utility_frontier], the explicit calibration hold in
[@fig:calibration_reliability], and the restart check in [@fig:persistence_recovery].

## Milestone contract

The complete configured program contains {{CONFIG_RESEARCH_ROADMAP_STAGE_COUNT}}
milestones. Each row states what would be built, measured, falsified, and accepted;
empty claims are not allowed to advance by narrative momentum.

Each configured row has two orthogonal state fields. `implementation_status` records
whether executable substrate exists; `evidence_status` records whether the decisive
study has produced admissible evidence. Thus an adapter can be implemented while its
external study remains `external_not_run`, and a prototype can exist while its held-out
comparison remains unperformed. The compact Status column below is only a display
label; the two machine-readable fields govern audit and promotion.

| ID | Milestone | Status | Hypothesis | Required artifact |
|:---|:---|:---|:---|:---|
{{RESULT_RESEARCH_ROADMAP_EVIDENCE_ROWS}}
: Evidence plan for the configured research milestones. {#tbl:research-roadmap-evidence}

| ID | Decisive metric | Falsifier | Exit criterion |
|:---|:---|:---|:---|
{{RESULT_RESEARCH_ROADMAP_DECISION_ROWS}}
: Decision contract for the configured research milestones. {#tbl:research-roadmap-decision}

The evidence plan in [@tbl:research-roadmap-evidence] and decision contract in
[@tbl:research-roadmap-decision] are generated from `docs/manuscript/config.yaml`;
they are not a second authority for parameters or results. The variable snapshot
records the exact roadmap configuration, while the figure registry records the rendered
planning visual and its hash. R0 additionally retains the replay's semantic and file
digests shown in [@tbl:reproducibility_identity]. The implemented R0 row is accepted
only when its configured `artifact_paths` resolve to checked-in source or evidence
surfaces. R1 is governed by the same artifact-path requirement for the implemented local
ledger. R2-R5 now have local adapters or harnesses, and R6 has a research prototype,
but those implementation artifacts do not satisfy their empirical exit criteria. R2
remains evidence-open until its adapter is exercised against deployment-specific,
independently sourced observations; R3-R6 remain evidence-open until their declared
external or held-out comparisons are retained. R7 is blocked until those dependencies
can be independently replayed.

## Execution protocol

`ResearchProgramOrchestrator` supplies the local dependency-control mechanism. It
validates a directed acyclic graph, executes ready tracks in deterministic topological
order, records exceptions as failures, and marks dependent tracks blocked. It does not
retry, hide, or promote a failed study, and a returned runner output is not itself a
scientific acceptance decision.

Every future study should retain the following minimum evidence bundle:

- the source commit, environment fingerprint, lockfile digest, configuration digest,
  random seed, and input checksums;
- raw append-only proposal, verdict, authorization, receipt, and outcome traces,
  including the external observation source and rejected or failed cases rather than
  only successful runs;
- the baseline policy, the mediated policy, and the exact paired assignment rule;
- analysis code that computes point estimates, uncertainty intervals, calibration
  diagnostics, and failure stratifications; and
- generated tables, figures, captions, and a machine-readable manifest linking each
  claim to its source artifact.

This entity--activity--agent separation is compatible with the W3C PROV data model,
which is used here as a provenance vocabulary rather than as evidence that a result is
correct [@w3c2013provo]. In particular, recording who or what generated an artifact and
which activity used it supports auditability; scientific acceptance still depends on
the milestone's independent observations, falsifier, and replay.

This bundle turns a research result into a replay target. It does not require a claim to
be positive: a well-specified null result or failed falsification attempt is publishable
evidence when its inputs and analysis remain inspectable. Model cards and safety cases
are useful reporting analogies, but their presence does not substitute for the linked
execution evidence [@mitchell2019modelcards; @buhl2024safetycases].

## Decision rules for promotion

Promotion from one milestone to the next requires all of the following:

1. the artifact is complete and independently replayable;
2. the decisive metric is computed on the declared comparison rather than on the gate
   labels it is intended to validate;
3. uncertainty, missingness, and adverse cases are reported;
4. the stated falsifier has been evaluated without silently changing the protocol; and
5. the result does not exceed the claim boundary of the implementation or the data.

If a milestone fails its falsifier, the next action is diagnosis, redesign, or a bounded
negative result—not relabeling the failure as a successful ecological effect. In
particular, training a predictor to reproduce EXECUTE/HOLD/REFUSE labels would validate
the existing rule's behavior, not its downstream usefulness. Utility must be measured
against independently observed repair cost, policy violation, task completion, or other
outcomes specified before analysis.

## Relation to the active-inference track

The final milestone depends on the distinctions in [@sec:active-inference]. A
probabilistic extension must declare observations, latent states, likelihoods, priors,
posteriors, policies, preferences, and an inference procedure. It must then be compared
with the current deterministic gate using posterior predictive checks, simulation-based
calibration, held-out log loss, utility, and compute cost. Naming a trust score a
posterior or a gate score expected free energy would not satisfy that contract.

The roadmap therefore treats Active Inference as a falsifiable modeling direction rather
than a retrospective interpretation. This is consistent with the current crosswalk's
claim boundary and with the broader positioning against tool-use security and runtime
assurance: cited external benchmarks motivate adapters and threat models, but none is
evidence for the Colony Kernel until the experiment is actually run
[@debenedetti2024agentdojo; @zhan2024injecagent; @ruan2023toolemu; @seto1998simplex].

## Scope of this release

The current release documents and validates R0's local contract, fixed-input replay, and
reproducibility route plus R1's authenticated local lifecycle ledger. It also provides
implementation substrate for R2-R6 and dependency-aware execution bookkeeping. It does
not claim that R2's external study or any later milestone's empirical evidence is complete,
that the provisional settings are calibrated, or that the control plane is a security
boundary. The appropriate scholarly contribution at this stage is a composable,
inspectable research substrate with explicit failure conditions and a machine-readable
path from configuration to prose, tables, figures, and artifacts.
