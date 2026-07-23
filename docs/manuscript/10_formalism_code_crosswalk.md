# Formalism-to-Code Crosswalk and Translation Methods {#sec:formalism-code-crosswalk}

The repository uses several kinds of formal description: typed operational contracts,
discrete recurrences, piecewise decision rules, executable invariants, AST-preservation
rules, optional SMT obligations, and probabilistic inference components. These formalisms
are complementary, but they are not interchangeable. A formula in a document is not a
property of the software until the variables, state transition, implementation mapping,
and verification boundary are made explicit.

{{CONFIG_PARAMETER_STATUS_NOTE}} This section makes that translation chain inspectable.
It does not claim that every formalism has been connected to the Colony Kernel, and it
does not treat a shared word such as *trust*, *state*, or *policy* as evidence of
semantic equivalence.

## A five-link translation chain {#sec:crosswalk-method}

The crosswalk uses five links for every formal claim:

1. **Formal object.** State the mathematical or logical object, its variables, domains,
   and assumptions. If a probability model is intended, declare the sample space,
   likelihood, prior, posterior, and policy variables rather than naming a scalar as a
   posterior by analogy.
2. **Code representation.** Identify the typed value objects, enums, state holders, or
   functions that represent the object. The representation may be partial; that fact is
   recorded rather than inferred away.
3. **Translation mechanism.** State how the formal object is computed from or imposed on
   code: a constructor guard, state-transition function, recurrence, AST comparison,
   schema adapter, or sound symbolic encoding.
4. **Executable evidence.** Name the tests, replay artifacts, solver obligations, or
   generated outputs that exercise the translation. A test of a wrapper is not silently
   promoted to a proof of the wrapped system.
5. **Claim boundary.** State what the evidence supports and the strongest nearby claim it
   does not support. This final link prevents a local invariant from becoming a claim of
   safety, utility, biological equivalence, or production reliability.

This discipline follows design-by-contract and formal-methods practice
[@apt2003principles], while the retained configuration, source anchors, and generated
artifacts follow the broader requirements of reproducible and accountable computation
[@peng2011reproducible; @raji2020accountability; @buhl2024safetycases].

![{{FIGURE_CAPTION_FORMALISM_CODE_CROSSWALK}}](figures/{{FIGURE_FILENAME_FORMALISM_CODE_CROSSWALK}}){#{{FIGURE_LABEL_FORMALISM_CODE_CROSSWALK}} width={{FIGURE_WIDTH_FORMALISM_CODE_CROSSWALK}}}

![{{FIGURE_CAPTION_FORMALISM_COVERAGE}}](figures/{{FIGURE_FILENAME_FORMALISM_COVERAGE}}){#{{FIGURE_LABEL_FORMALISM_COVERAGE}} width={{FIGURE_WIDTH_FORMALISM_COVERAGE}}}

![{{FIGURE_CAPTION_RESEARCH_STATUS_MATRIX}}](figures/{{FIGURE_FILENAME_RESEARCH_STATUS_MATRIX}}){#{{FIGURE_LABEL_RESEARCH_STATUS_MATRIX}} width={{FIGURE_WIDTH_RESEARCH_STATUS_MATRIX}}}

The visual in [@fig:formalism_code_crosswalk] shows correspondence as a chain with
missing links, not as a proof graph. Green denotes a mapping whose implementation and
focused evidence are present; blue denotes a partial bridge; amber and pink denote
future work or a research component.

The inventory summary in [@fig:formalism_coverage] counts these documented statuses,
while [@fig:research_status_matrix] places the formalism rows beside the roadmap
milestones. Neither visualization measures theorem coverage; both are navigation and
claim-boundary aids.

## Current correspondence inventory {#sec:crosswalk-inventory}

The configured inventory contains {{CONFIG_FORMALISM_CROSSWALK_COUNT}} mappings:
{{RESULT_FORMAL_CROSSWALK_IMPLEMENTED}} implemented,
{{RESULT_FORMAL_CROSSWALK_PARTIAL}} partial, and
{{RESULT_FORMAL_CROSSWALK_RESEARCH}} research. The first table records the formal
layer and its current status; the second records the translation and evidence boundary.
Both tables are generated from
`docs/manuscript/config.yaml` and validated against the current repository paths before
rendering.

| ID | Mapping | Formal layer | Formal object | Status |
|:---|:---|:---|:---|:---|
{{RESULT_FORMALISM_CROSSWALK_ROWS}}
: Formalism inventory and implementation status. {#tbl:formalism-code-inventory}

| ID | Code anchor | Translation mechanism | Executable evidence | Claim boundary |
|:---|:---|:---|:---|:---|
{{RESULT_FORMALISM_CROSSWALK_EVIDENCE_ROWS}}
: Translation, evidence, and claim boundaries for the formalism inventory. {#tbl:formalism-code-evidence}

[@tbl:formalism-code-inventory] is the status view; [@tbl:formalism-code-evidence] is
the evidence and limitation view. Keeping both views explicit prevents a green
implementation row from being read as a universal proof.

The inventory distinguishes *representation* from *verification*. For example,
`ActiveInferenceAgent` and `InferenceEngine` provide probabilistic components, but their
presence does not connect them to the Colony Kernel's deterministic gate. Conversely, the
gate recurrence and the AST-preservation rules have executable bridges but do not imply
that the resulting policy is safe or optimal.

## How the formalisms compose {#sec:crosswalk-composition}

The useful relationship among the layers is a sequence of constrained translations:

**Operational semantics → recurrence.** Typed `ColonySignal`, `ActionProposal`, and
`GateResult` objects define the state vocabulary. `PheromoneStore` then supplies a
discrete transition for one part of that state. The recurrence is a projection of the
operational state, not a complete semantics for the kernel.

**Recurrence → decision rule.** The gate observes the projected local field and applies a
piecewise risk function plus hard overrides. Monotonicity of the recurrence or risk
function can be proved arithmetically while the composition, ordering, and side effects
still require integration tests.

**Decision rule → invariant predicate.** Bounds, threshold ordering, and weight
conservation can be stated as executable predicates. These predicates should import the
same runtime constants as the decision rule; copied constants create a second model that
can pass while the implementation changes.

**Invariant predicate → symbolic obligation.** An SMT bridge can prove a supplied
obligation such as $C\land\neg I$ being unsatisfiable. It proves the encoded obligation,
not the Python implementation, unless a sound state-to-symbol translation and a
correspondence theorem are supplied. The repository now includes a kernel-specific,
bounded encoding and a structured `unavailable` result when optional Z3 is absent; the
encoding remains evidence about the stated obligations, not a whole-program proof.

**Deterministic state → probabilistic model.** A probabilistic or Active-Inference model
must introduce random variables, likelihoods, priors, transition dynamics, preferences,
and an observation protocol. Deterministic pressure, trust, or gate scores may be
observations or interface projections, but they are not posteriors or expected free
energy without those definitions.

These relations are directional. A code path can instantiate a formal recurrence, while
an equation cannot by itself establish that a caller, scheduler, or persistence layer
actually follows the equation. The crosswalk therefore treats implementation evidence as
necessary for a code claim and formal definitions as necessary for a mathematical claim;
neither substitutes for the other.

## Integration research agenda {#sec:crosswalk-agenda}

The next work is deliberately staged so that each stronger connection depends on a
weaker one being replayable:

1. **State and trace schema.** The versioned ledger and replay schema now link proposal
   digest, gate verdict, execution authorization, execution receipt, outcome evidence,
   and actor. Focused tests cover replay, omission, duplication, nonce reuse, and
   unauthorized relinking; outcomes are not promoted to inference data automatically.
2. **Kernel-specific invariant encoding.** A solver-neutral contract and optional Z3
   backend now return proved, refuted, unknown, timeout, or unavailable states. The
   remaining research task is a broader correspondence audit across generated states.
3. **Refinement tests.** The independent reference interpreter and differential tests
   cover the current gate projection. More transition families should be added before
   claiming complete refinement.
4. **Probabilistic adapter.** The explicit adapter declares an observation model over
   attested traces, a latent
   state space, priors, transition and observation models, preferences, and policy
   horizon. Keep the deterministic gate as a baseline and report calibration, held-out
   log loss, utility, refusal cost, and compute cost.
5. **Cross-formalism evidence bundle.** Publish the source commit, configuration and
   environment digests, seeds, inputs, raw traces, solver versions, generated tables and
   figures, and all negative or inconclusive results. Promotion requires the evidence
   bundle and the stated falsifier, not a plausible narrative.

The [@sec:research-roadmap] milestones are the release-level plan; this section is the
translation method that makes a milestone's formal and executable parts composable. A
future positive result may justify a stronger claim only after the relevant bridge is
implemented, independently replayed, and shown not to collapse into a test of the same
labels it is intended to validate.

## Scope and non-equivalence {#sec:crosswalk-limitations}

The current release establishes several local correspondences and exposes their gaps. It
does not provide a formal semantics for all modules, a proof-carrying build, a complete
refinement proof from Python to SMT, a causal model of outcomes, or an integrated Active
Inference controller. The appropriate scholarly claim is therefore methodological:
Codomyrmex provides a substrate in which formal objects, code anchors, tests, and claim
boundaries can be recorded together. Whether those connections produce better safety,
utility, calibration, or generalization remains an empirical question.
