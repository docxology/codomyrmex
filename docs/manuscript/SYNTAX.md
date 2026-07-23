# Manuscript Syntax Reference (codomyrmex)

Project-specific overlay for the **codomyrmex** manuscript. This file documents the equation label registry, table label registry, section labels, `{{TOKEN}}` table, and prose conventions used by the local rendering scripts.

## Citation Syntax (Pandoc)

```markdown
<!-- Single citation -->
[@dorigo2004ant]

<!-- Multiple citations -->
[@dorigo2004ant; @bonabeau1999swarm]

<!-- Citation with locator -->
[@dorigo2004ant, pp. 14-17]

<!-- Narrative citation -->
@grasse1959reconstruction described how ants coordinate...
```

All citation keys must exist in [`references.bib`](references.bib). `scripts/compile_manuscript.py` renders citations with Pandoc citeproc (`--citeproc`) and linked citation metadata; **never** write raw `\cite{}` in Markdown.

## Equation Environments

```markdown
<!-- Numbered equation with label (preferred Pandoc-crossref form) -->
$$
\text{gate\_score} = w_b \cdot b + w_r \cdot r + w_t \cdot t + w_c \cdot c
$$ {#eq:gate_score_detail}

<!-- Reference in text (parenthetical) -->
[@eq:gate_score_detail] gives the actuation-gate scoring model.

<!-- Reference in text (narrative) -->
@eq:gate_score_detail expands the weight assignments...
```

Reference equations with `[@eq:label]` (parenthetical) or `@eq:label` (narrative). **Never** use raw LaTeX `\ref` / `\eqref` macros in Markdown source — the Pandoc bracket form renders portably across PDF and HTML.

### Equation label registry

| Label | Equation | Source file |
|---|---|---|
| `{#eq:effective_strength}` | Signal strength scaled by source multiplier and agent trust factor | `02_methodology.md` |
| `{#eq:gate_score_detail}` | Generated weighted ordinary gate score | `02_methodology.md` |
| `{#eq:trust_penalty}` | Local trust-component penalty for recent failure streaks | `02_methodology.md` |
| `{#eq:proposal_completeness}` | Completeness score as a function of missing evidence fields | `02_methodology.md` |
| `{#eq:worked_example_execute}` | Worked EXECUTE score under clean budget/risk and medium trust | `02_methodology.md` |
| `{#eq:worked_example_failure_streak}` | Worked score after recent-failure trust penalty | `02_methodology.md` |
| `{#eq:worked_example_hold}` | Worked HOLD score after failure streak and medium risk pressure | `02_methodology.md` |
| `{#eq:trust_delta}` | $\Delta_\text{trust} = \Delta_\text{pass/fail} + \Delta_\text{repair} + h \cdot \Delta_\text{human}$ | `02_methodology.md` |
| `{#eq:field-state}` | Capped location-by-signal field state | `02_theory.md` |
| `{#eq:field-recurrence}` | Implemented capped subtractive recurrence | `02_theory.md` |
| `{#eq:passive-linear-decay}` | Closed form for passive linear decay | `02_theory.md` |
| `{#eq:finite-extinction}` | Finite extinction tick for passive traces | `02_theory.md` |
| `{#eq:effective-hazard}` | Maximum of local RISK and FAILURE pressure | `02_theory.md` |
| `{#eq:risk-clearance}` | Piecewise hazard-credit map | `02_theory.md` |
| `{#eq:paired-clear-score}` | Clear-target paired gate score | `02_theory.md` |
| `{#eq:paired-failure-score}` | Failed-target paired gate score | `02_theory.md` |
| `{#eq:theory-gate-score}` | General weighted ordinary gate score | `02_theory.md` |
| `{#eq:hold-value-condition}` | Conditional value criterion for HOLD | `02_theory.md` |
| `{#eq:trust-update}` | Clipped trust-state recurrence | `02_theory.md` |
| `{#eq:trust-delta}` | Outcome-dependent trust increment | `02_theory.md` |
| `{#eq:trust-drift}` | Expected drift under a stated outcome model | `02_theory.md` |
| `{#eq:trust-replacement-sensitivity}` | Replacement sensitivity of the deterministic trust summary | `02_theory.md` |
| `{#eq:paired-score-change}` | Exact paired same-target score change | `03_results.md` |
| `{#eq:lower-tier-score}` | Attainable lower-tier score family | `03_results.md` |
| `{#eq:variational-free-energy}` | Canonical identity used for comparison | `08_active_inference.md` |
| `{#eq:appendix-gate-score}` | Appendix ordinary gate score | `90_appendix_design_rationale.md` |
| `{#eq:appendix-linear-decay}` | Appendix linear-decay recurrence | `90_appendix_design_rationale.md` |

## Section Labels

Every H1 in this manuscript carries a `{#sec:<name>}` label so cross-section references (`[@sec:methodology]`) survive reordering. Abstract and references are explicitly unnumbered; numbered body sections start at the introduction.

| File | Section H1 | Label |
|---|---|---|
| `00_abstract.md` | Abstract | `{#sec:abstract .unnumbered}` |
| `01_introduction.md` | Introduction | `{#sec:introduction}` |
| `02_theory.md` | Operational Semantics and Verified Invariants | `{#sec:theory}` |
| `02_methodology.md` | Implementation Method and Control-Plane Semantics | `{#sec:methodology}` |
| `03_results.md` | Executed Contract Results and Evidence Boundary | `{#sec:results}` |
| `04_conclusion.md` | What the Release Establishes | `{#sec:conclusion}` |
| `05_experimental_setup.md` | Evaluation Protocol, Configuration, and Reproducibility Inputs | `{#sec:experimental_setup}` |
| `06_reproducibility.md` | Reproducibility Chain, Provenance, and Limits | `{#sec:reproducibility}` |
| `07_scope_and_related_work.md` | Scope, Related Work, and Claim Boundaries | `{#sec:scope}` |
| `08_active_inference.md` | Active Inference: Bounded Crosswalk and Upgrade Path | `{#sec:active-inference}` |
| `09_research_roadmap.md` | Research Roadmap: Evidence Gates and Dependency Order | `{#sec:research-roadmap}` |
| `10_formalism_code_crosswalk.md` | Formalism-to-Code Crosswalk: Translation, Evidence, and Limits | `{#sec:formalism-code-crosswalk}` |
| `90_appendix_design_rationale.md` | Appendix: Design Rationale, Assumptions, and Alternatives | `{#sec:design-rationale}` |
| `99_references.md` | References | `{#sec:references .unnumbered}` |

## Table References

```markdown
| Gate | Status | Detail |
|------|--------|--------|
| ruff | Pass   | 0 violations |

: Quality-gate outcomes for the Colony Kernel implementation {#tbl:quality_gates}

<!-- Reference in text -->
[@tbl:quality_gates] summarises all gate outcomes.
```

### Table label registry

| Label | Caption summary | Source file |
|---|---|---|
| `{#tbl:subsystem_overview}` | Colony Control Plane subsystem overview | `02_methodology.md` |
| `{#tbl:signal_types}` | Pheromone signal types and gate effects | `02_methodology.md` |
| `{#tbl:methodology_decay_rates}` | Subtractive unit-trace decay classes | `02_methodology.md` |
| `{#tbl:resource_dimensions}` | Resource budget dimensions enforced by `ResourceLedger` | `02_methodology.md` |
| `{#tbl:risk_pressure_mapping}` | Effective local-hazard mapping used by the gate | `02_methodology.md` |
| `{#tbl:trust_mapping}` | Trust-score mapping used by the gate | `02_methodology.md` |
| `{#tbl:gate_decision_thresholds}` | Actuation-gate decision thresholds | `02_methodology.md` |
| `{#tbl:role_ladder_methodology}` | Role labels and intended specializations | `02_methodology.md` |
| `{#tbl:pruning_confidence}` | Pruning-daemon candidate confidence tiers | `02_methodology.md` |
| `{#tbl:falsification_taxonomy}` | Falsification-worker attack vector taxonomy | `02_methodology.md` |
| `{#tbl:formal-claim-status}` | Verified properties and open hypotheses | `02_theory.md` |
| `{#tbl:quality_gates}` | Executed pytest/coverage/Ruff/ty snapshot | `03_results.md` |
| `{#tbl:paired-locality}` | Same-target inhibition, target isolation, and decay recovery | `03_results.md` |
| `{#tbl:representative-gates}` | Formula-checked gate cases | `03_results.md` |
| `{#tbl:trust_trajectory}` | Deterministic all-success trust fixture | `03_results.md` |
| `{#tbl:linear-decay-values}` | Exact passive unit-trace decay | `03_results.md` |
| `{#tbl:mcp-tools}` | Eight-tool MCP state-effect inventory | `03_results.md` |
| `{#tbl:evidence-status}` | Executed and proposed evidence status | `05_experimental_setup.md` |
| `{#tbl:dependent_variables}` | Required proposed-benchmark outcomes | `05_experimental_setup.md` |
| `{#tbl:experimental_gate_thresholds}` | Gate decision thresholds for experimental configuration | `05_experimental_setup.md` |
| `{#tbl:experimental_gate_weights}` | Gate score dimension weights for experimental configuration | `05_experimental_setup.md` |
| `{#tbl:experimental_decay_rates}` | Linear field dynamics for unit traces | `05_experimental_setup.md` |
| `{#tbl:resource_budget_caps}` | Resource budget caps from `kernel.yaml` | `05_experimental_setup.md` |
| `{#tbl:role_ladder}` | Inferred labels and current enforcement boundary | `05_experimental_setup.md` |
| `{#tbl:software_environment}` | Software environment for the manuscript snapshot | `05_experimental_setup.md` |
| `{#tbl:repro-scope}` | Scope of reproducibility evidence | `06_reproducibility.md` |
| `{#tbl:configuration_provenance}` | Configuration provenance for the rendered manuscript | `06_reproducibility.md` |
| `{#tbl:artifact_registry}` | Generated artifact registry for the manuscript pipeline | `06_reproducibility.md` |
| `{#tbl:quality_gate_summary}` | Quality gate summary used by the reproducibility certificate | `06_reproducibility.md` |
| `{#tbl:software_versions}` | Software versions used by the reproducibility certificate | `06_reproducibility.md` |
| `{#tbl:evaluation_snapshot}` | Evaluation snapshot inputs and generated artifacts | `06_reproducibility.md` |
| `{#tbl:external-evidence}` | Evidence required for an external comparison | `06_reproducibility.md` |
| `{#tbl:falsification-benchmarks}` | Conclusion claim boundary and falsification agenda | `04_conclusion.md` |
| `{#tbl:external-validation-agenda}` | Future external validation agenda | `07_scope_and_related_work.md` |
| `{#tbl:ai-correspondence-status}` | Active Inference analogies and non-equivalence | `08_active_inference.md` |
| `{#tbl:research-roadmap-evidence}` | Milestone evidence plan | `09_research_roadmap.md` |
| `{#tbl:research-roadmap-decision}` | Milestone decision contract | `09_research_roadmap.md` |
| `{#tbl:gate-formula-tradeoffs}` | Candidate score-policy tradeoffs | `90_appendix_design_rationale.md` |
| `{#tbl:appendix-figures}` | Generated figure evidence registry | `90_appendix_design_rationale.md` |

## Figure References

Figures are referenced using pandoc-crossref syntax:

```markdown
![Caption text.](figures/filename.png){#fig:label width=80%}

<!-- Reference in text -->
[@fig:label] shows the architecture.
```

Figure source PNG files live in `output/figures/` and are generated by `scripts/generate_manuscript_figures.py`. The generator reads `output/data/manuscript_variables.json`, `docs/manuscript/config.yaml`, and `config/colony_kernel/roles.yaml` before drawing the assets, then stamps each figure with the manuscript version, config hash, and generation date. Captions, labels, widths, filenames, and evidence classes are defined once under `config.yaml` and injected as `FIGURE_*` tokens. Re-run variable generation and the figure script together before rendering.

### Figure label registry

| Label | PNG filename | Generator function | Source file |
|---|---|---|---|
| `{#fig:architecture}` | `subsystem_architecture.png` | `fig_subsystem_architecture()` | `02_methodology.md` |
| `{#fig:pheromone_decay}` | `pheromone_decay.png` | `fig_pheromone_decay()` | `02_theory.md` |
| `{#fig:falsification_vectors}` | `falsification_vectors.png` | `fig_falsification_vectors()` | `02_methodology.md` |
| `{#fig:pressure_loop}` | `colony_pressure_loop.png` | `fig_colony_pressure_loop()` | `02_methodology.md` |
| `{#fig:trust_trajectory}` | `trust_trajectory.png` | `fig_trust_trajectory()` | `03_results.md` |
| `{#fig:gate_heatmap}` | `gate_score_heatmap.png` | `fig_gate_score_heatmap()` | `03_results.md` |
| `{#fig:gate_score_3d}` | `gate_score_3d.png` | `fig_gate_score_3d()` | `02_theory.md` |
| `{#fig:fep_correspondence}` | `fep_correspondence.png` | `fig_fep_correspondence()` | `08_active_inference.md` |
| `{#fig:research_roadmap}` | `research_roadmap.png` | `fig_research_roadmap()` | `09_research_roadmap.md` |
| `{#fig:formalism_code_crosswalk}` | `formalism_code_crosswalk.png` | `fig_formalism_code_crosswalk()` | `10_formalism_code_crosswalk.md` |
| `{#fig:replay_contract}` | `replay_contract.png` | `fig_replay_contract()` | `03_results.md` |
| `{#fig:attestation_event_chain}` | `attestation_event_chain.png` | `fig_attestation_event_chain()` | `09_research_roadmap.md` |
| `{#fig:safety_utility_frontier}` | `safety_utility_frontier.png` | `fig_safety_utility_frontier()` | `09_research_roadmap.md` |
| `{#fig:calibration_reliability}` | `calibration_reliability.png` | `fig_calibration_reliability()` | `09_research_roadmap.md` |
| `{#fig:persistence_recovery}` | `persistence_recovery.png` | `fig_persistence_recovery()` | `09_research_roadmap.md` |
| `{#fig:formalism_coverage}` | `formalism_coverage.png` | `fig_formalism_coverage()` | `10_formalism_code_crosswalk.md` |
| `{#fig:research_status_matrix}` | `research_status_matrix.png` | `fig_research_status_matrix()` | `10_formalism_code_crosswalk.md` |

The additional generated image is `cover.png`, referenced by the unnumbered cover page.
`output/figures/figure_registry.json` records the generated filenames, evidence classes,
byte sizes, and SHA-256 hashes.

## `{{VARIABLE}}` Token Table

All `{{TOKEN}}` placeholders are resolved at render time by `scripts/z_generate_manuscript_variables.py`, which writes `output/data/manuscript_variables.json` and substituted Markdown under `output/manuscript/`. An undefined or unresolved token causes a non-zero exit before the PDF renderer runs. The JSON snapshot and the key map in `variables.py` are authoritative; the compact table below is an authoring aid, not a second complete inventory.

| Token | Category | Section(s) |
|---|---|---|
| `{{ARTIFACT_CONFIG_FILES}}` | ARTIFACT | `06_reproducibility.md` |
| `{{ARTIFACT_MCP_TOOLS}}` | ARTIFACT | `06_reproducibility.md` |
| `{{ARTIFACT_REPLAY_PATH}}` | ARTIFACT | `06_reproducibility.md` |
| `{{ARTIFACT_TEST_SUITES}}` | ARTIFACT | `03_results.md`, `06_reproducibility.md` |
| `{{CONFIG_AGENT_COUNT}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_AUTHOR_ORCID}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_BASE_EVAPORATION_RATE}}` | CONFIG | `02_methodology.md` |
| `{{CONFIG_BUDGET_DIMENSIONS_COUNT}}` | CONFIG | generated map only |
| `{{CONFIG_BUDGET_MAX_LLM_CALLS}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_BUDGET_MAX_RISK}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_BUDGET_MAX_RUNTIME}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_BUDGET_MAX_SECURITY}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_COLONY_KERNEL_SUBSYSTEMS}}` | CONFIG | `00_abstract.md`, `03_results.md` |
| `{{CONFIG_DECAY_RATES_COUNT}}` | CONFIG | generated map only |
| `{{CONFIG_DECAY_RATE_FAST}}` | CONFIG | generated map only |
| `{{CONFIG_DECAY_RATE_NORMAL}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_DECAY_RATE_SLOW}}` | CONFIG | generated map only |
| `{{CONFIG_DOI}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_FALSIFICATION_VECTORS}}` | CONFIG | generated map only |
| `{{CONFIG_FIRST_AUTHOR}}` | CONFIG | `00_00_cover.md`, `00_abstract.md`, `06_reproducibility.md` |
| `{{CONFIG_GATE_EXECUTE_THRESHOLD}}` | CONFIG | `00_abstract.md`, `05_experimental_setup.md` |
| `{{CONFIG_GATE_HOLD_THRESHOLD}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_GATE_WEIGHT_BUDGET}}` | CONFIG | generated map only |
| `{{CONFIG_GATE_WEIGHT_COMPLETENESS}}` | CONFIG | generated map only |
| `{{CONFIG_GATE_WEIGHT_RISK}}` | CONFIG | generated map only |
| `{{CONFIG_GATE_WEIGHT_TRUST}}` | CONFIG | generated map only |
| `{{CONFIG_GITHUB_REPOSITORY}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_HASH}}` | CONFIG | `06_reproducibility.md` |
| `{{REPRO_GIT_COMMIT}}` | REPRO | `06_reproducibility.md` |
| `{{REPRO_INVENTORY_HASH}}` | REPRO | `06_reproducibility.md` |
| `{{REPRO_KERNEL_SOURCE_HASH}}` | REPRO | `06_reproducibility.md` |
| `{{CONFIG_KEYWORDS}}` | CONFIG | `00_abstract.md`, `06_reproducibility.md` |
| `{{CONFIG_MCP_TOOL_COUNT}}` | CONFIG | `00_abstract.md` |
| `{{CONFIG_MODULE_COUNT}}` | CONFIG | generated map only |
| `{{CONFIG_PDF_MARGIN}}` | CONFIG | `preamble.md`, `06_reproducibility.md` |
| `{{CONFIG_PARAMETER_STATUS_NOTE}}` | CONFIG | `01_introduction.md`, `02_methodology.md`, `02_theory.md`, `03_results.md`, `04_conclusion.md`, `05_experimental_setup.md`, `06_reproducibility.md`, `07_scope_and_related_work.md`, `08_active_inference.md`, `09_research_roadmap.md`, `90_appendix_design_rationale.md` |
| `{{CONFIG_RESEARCH_ROADMAP_STAGE_COUNT}}` | CONFIG | `09_research_roadmap.md`, generated roadmap caption |
| `{{RESULT_RESEARCH_ROADMAP_EVIDENCE_ROWS}}` | RESULT | `09_research_roadmap.md` |
| `{{RESULT_RESEARCH_ROADMAP_DECISION_ROWS}}` | RESULT | `09_research_roadmap.md` |
| `{{CONFIG_FORMALISM_CROSSWALK_COUNT}}` | CONFIG | `10_formalism_code_crosswalk.md`, generated crosswalk caption |
| `{{CONFIG_FORMALISM_CODE_CROSSWALK}}` | CONFIG | generated formalism/code crosswalk figure data |
| `{{RESULT_FORMALISM_CROSSWALK_ROWS}}` | RESULT | `10_formalism_code_crosswalk.md` |
| `{{RESULT_FORMALISM_CROSSWALK_EVIDENCE_ROWS}}` | RESULT | `10_formalism_code_crosswalk.md` |
| `{{CONFIG_PARAMETER_STATUS_SHORT}}` | CONFIG | generated figure captions |
| `{{CONFIG_PHEROMONE_RETENTION_FAST}}` | CONFIG | generated map only |
| `{{CONFIG_PHEROMONE_RETENTION_FAST_PCT}}` | CONFIG | `02_methodology.md` |
| `{{CONFIG_PHEROMONE_RETENTION_NORMAL}}` | CONFIG | generated map only |
| `{{CONFIG_PHEROMONE_RETENTION_NORMAL_PCT}}` | CONFIG | `02_methodology.md` |
| `{{CONFIG_PHEROMONE_RETENTION_SLOW}}` | CONFIG | generated map only |
| `{{CONFIG_PHEROMONE_RETENTION_SLOW_PCT}}` | CONFIG | `02_methodology.md` |
| `{{CONFIG_PUBLICATION_DATE}}` | CONFIG | generated map only |
| `{{CONFIG_PUBLICATION_DATE_DISPLAY}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_ROLE_COUNT}}` | CONFIG | generated map only |
| `{{CONFIG_SIGNAL_TYPES_COUNT}}` | CONFIG | generated map only |
| `{{CONFIG_SUBTITLE}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_TEST_COUNT}}` | CONFIG | generated map only |
| `{{CONFIG_TITLE}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_TRIAL_COUNT}}` | CONFIG | `01_introduction.md`, `05_experimental_setup.md` |
| `{{CONFIG_TRIAL_COUNT_MINUS_1}}` | CONFIG | generated map only |
| `{{CONFIG_TRUST_DELTA_FAIL}}` | CONFIG | generated map only |
| `{{CONFIG_TRUST_DELTA_PASS}}` | CONFIG | generated map only |
| `{{CONFIG_TRUST_HARD_FLOOR}}` | CONFIG | generated map only |
| `{{CONFIG_TRUST_PROMOTE_THRESHOLD}}` | CONFIG | generated map only |
| `{{CONFIG_TRUST_SANDBOX_SCORE}}` | CONFIG | generated map only |
| `{{CONFIG_VERSION}}` | CONFIG | `00_00_cover.md`, `05_experimental_setup.md`, `06_reproducibility.md` |
| `{{CONFIG_WARMUP_TICKS}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_WORKLOAD_TASK_COUNT}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_YAML_CONFIG_FILES}}` | CONFIG | generated map only |
| `{{GENERATION_TIMESTAMP}}` | ENVIRONMENT | `05_experimental_setup.md`, `06_reproducibility.md` |
| `{{PLATFORM}}` | ENVIRONMENT | generated map only |
| `{{PYTHON_VERSION}}` | ENVIRONMENT | `05_experimental_setup.md`, `06_reproducibility.md` |
| `{{RESULT_COLONY_KERNEL_FILES}}` | RESULT | `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_COLONY_KERNEL_LOC}}` | RESULT | `03_results.md` |
| `{{RESULT_COVERAGE_PCT}}` | RESULT | `00_abstract.md`, `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_GATE_SCORE_SANDBOX}}` | RESULT | generated map only |
| `{{RESULT_MODULE_DOCS_COUNT}}` | RESULT | `06_reproducibility.md` |
| `{{RESULT_PHEROMONE_FAST_LOSS_REPORT_TICK_PCT}}` | RESULT | `03_results.md`, `05_experimental_setup.md` |
| `{{RESULT_PHEROMONE_SLOW_RETENTION_REPORT_TICK_PCT}}` | RESULT | `03_results.md`, `05_experimental_setup.md` |
| `{{RESULT_PROPOSALS_TO_PROMOTION}}` | RESULT | generated map only |
| `{{RESULT_RUFF_ERRORS}}` | RESULT | `00_abstract.md`, `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_REPLAY_SEMANTIC_DIGEST}}` | RESULT | `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_REPLAY_RECORD_SHA256}}` | RESULT | `06_reproducibility.md` |
| `{{RESULT_REPLAY_FILE_SHA256}}` | RESULT | `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_REPLAY_REPEATABLE}}` | RESULT | `06_reproducibility.md` |
| `{{RESULT_REPLAY_SAME_TARGET_DECISION}}` | RESULT | `06_reproducibility.md` |
| `{{RESULT_REPLAY_UNRELATED_DECISION}}` | RESULT | `06_reproducibility.md` |
| `{{RESULT_REPLAY_RECOVERY_DECISION}}` | RESULT | `06_reproducibility.md` |
| `{{RESULT_TEST_COUNT}}` | RESULT | `00_abstract.md`, `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_TRUST_AFTER_PROMOTION}}` | RESULT | generated map only |
| `{{RESULT_TRUST_TRAJECTORY_ROWS}}` | RESULT | `03_results.md` |
| `{{RESULT_PAIRED_LOCALITY_ROWS}}` | RESULT | `03_results.md` |
| `{{RESULT_PAIRED_CLEAR_PRESSURE}}` | RESULT | generated replay figure caption |
| `{{RESULT_PAIRED_UNRELATED_PRESSURE}}` | RESULT | generated replay figure caption |
| `{{RESULT_DECAY_ROWS}}` | RESULT | `03_results.md` |
| `{{RESULT_REPRESENTATIVE_GATE_ROWS}}` | RESULT | `03_results.md` |
| `{{RESULT_TRUST_CONVERGENCE_STEPS}}` | RESULT | generated map only |
| `{{RESULT_TRUST_INITIAL}}` | RESULT | generated map only |
| `{{RESULT_TY_ERRORS}}` | RESULT | `00_abstract.md`, `03_results.md`, `06_reproducibility.md` |

## Preamble Injection

[`preamble.md`](preamble.md) contains the LaTeX packages that Pandoc consumes:

```markdown
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    allcolors=red
}
```

The HTML renderer also loads [`manuscript.css`](manuscript.css), which applies the same red hyperlink contract to browser output.

`scripts/compile_manuscript.py` fails closed when `pandoc-crossref` is missing. The filter runs before `--citeproc`; PDF output uses XeLaTeX and red links, while HTML output uses linked citations, linked cross-references, generated `nav#TOC`, and MathML for equations.

Do **not** duplicate package imports already loaded by this preamble.

## BibTeX Entry Format

```bibtex
@book{dorigo2004ant,
  author  = {Marco Dorigo and Thomas St\"{u}tzle},
  title   = {Ant Colony Optimization},
  publisher = {MIT Press},
  year    = {2004}
}

@book{bonabeau1999swarm,
  author    = {Eric Bonabeau and Marco Dorigo and Guy Theraulaz},
  title     = {Swarm Intelligence: From Natural to Artificial Systems},
  publisher = {Oxford University Press},
  year      = {1999}
}
```

- Keys must be lowercase alphanumeric with optional underscores
- Author names use `{Last, First}` or `{First Last}` format
- All entries must have at minimum: `author`, `title`, `year`
- Multi-word title words that must be capitalised wrap the word in braces: `{Colony}`

## Assembly order

The renderer assembles files using the executable `MANUSCRIPT_SECTION_ORDER` in
`scripts/compile_manuscript.py`. Filenames are stable identifiers, while section
numbers are renderer output and must not be hardcoded in prose or this guide. Use the
`sec`, `fig`, `tbl`, and `eq` labels above for all references. The generated contents
page is inserted after the cover, and the references anchor remains last.

## Prose Conventions

- No "In summary" or "In conclusion" at section ends (RASP standard)
- Use active voice for methodology and results descriptions: "The gate refuses" not "proposals are refused by the gate"
- Use explicit file paths when referencing code: `src/codomyrmex/colony_kernel/kernel.py`, not "the kernel module"
- Cite the config.yaml parameter path when stating a numeric threshold: "the `gate_execute_threshold` (0.75)" not "the threshold of 0.75"
- Every claim that could change between builds must be expressed as a `{{TOKEN}}` — never a bare literal
- Keep paragraphs focused — one idea per paragraph
- Avoid adjectives that assert quality without evidence ("robust", "powerful", "seamless")

## See Also

- [`README.md`](README.md) — Manuscript directory overview
- [`AGENTS.md`](AGENTS.md) — RASP protocol and AI agent constraints for this manuscript
- [`config.yaml`](config.yaml) — Authoritative source for all `CONFIG_*` token values
- [`preamble.md`](preamble.md) — Active LaTeX preamble
