# Manuscript Syntax Reference (codomyrmex)

Project-specific overlay for the **codomyrmex** manuscript. This file documents the equation label registry, table label registry, section labels, `{{TOKEN}}` table, and prose conventions used by the local rendering scripts.

## Citation Syntax (Pandoc)

```markdown
<!-- Single citation -->
[@dorigo2004ants]

<!-- Multiple citations -->
[@dorigo2004ants; @bonabeau1999swarm]

<!-- Citation with locator -->
[@dorigo2004ants, pp. 14-17]

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
| `{#eq:gate_score_detail}` | $g = 0.30 \cdot \text{budget\_ok} + 0.30 \cdot \text{risk\_ok} + 0.25 \cdot \text{trust\_ok} + 0.15 \cdot \text{completeness}$ | `02_methodology.md` |
| `{#eq:trust_penalty}` | Local trust-component penalty for recent failure streaks | `02_methodology.md` |
| `{#eq:proposal_completeness}` | Completeness score as a function of missing evidence fields | `02_methodology.md` |
| `{#eq:worked_example_execute}` | Worked EXECUTE score under clean budget/risk and medium trust | `02_methodology.md` |
| `{#eq:worked_example_failure_streak}` | Worked score after recent-failure trust penalty | `02_methodology.md` |
| `{#eq:worked_example_hold}` | Worked HOLD score after failure streak and medium risk pressure | `02_methodology.md` |
| `{#eq:trust_delta}` | $\Delta_\text{trust} = \Delta_\text{pass/fail} + \Delta_\text{repair} + h \cdot \Delta_\text{human}$ | `02_methodology.md` |

## Section Labels

Every H1 in this manuscript carries a `{#sec:<name>}` label so cross-section references (`[@sec:methodology]`) survive reordering. Abstract and references are explicitly unnumbered; numbered body sections start at the introduction.

| File | Section H1 | Label |
|---|---|---|
| `00_abstract.md` | Abstract | `{#sec:abstract .unnumbered}` |
| `01_introduction.md` | Introduction | `{#sec:introduction}` |
| `02_methodology.md` | Methodology | `{#sec:methodology}` |
| `03_results.md` | Colony Kernel Implementation Results | `{#sec:results}` |
| `04_conclusion.md` | Conclusion | `{#sec:conclusion}` |
| `05_experimental_setup.md` | Experimental Setup | `{#sec:experimental_setup}` |
| `06_reproducibility.md` | Reproducibility Certification | `{#sec:reproducibility}` |
| `07_scope_and_related_work.md` | Scope, Related Work, and Positioning | `{#sec:scope}` |
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
| `{#tbl:methodology_decay_rates}` | Pheromone decay classes and retention constants | `02_methodology.md` |
| `{#tbl:resource_dimensions}` | Resource budget dimensions enforced by `ResourceLedger` | `02_methodology.md` |
| `{#tbl:risk_pressure_mapping}` | RISK pheromone pressure mapping used by the gate | `02_methodology.md` |
| `{#tbl:trust_mapping}` | Trust-score mapping used by the gate | `02_methodology.md` |
| `{#tbl:gate_decision_thresholds}` | Actuation-gate decision thresholds | `02_methodology.md` |
| `{#tbl:role_ladder_methodology}` | Kernel role ladder and action permissions | `02_methodology.md` |
| `{#tbl:pruning_confidence}` | Pruning-daemon candidate confidence tiers | `02_methodology.md` |
| `{#tbl:falsification_taxonomy}` | Falsification-worker attack vector taxonomy | `02_methodology.md` |
| `{#tbl:quality_gates}` | ruff / ty / pytest / coverage gate outcomes for the Colony Kernel | `03_results.md` |
| `{#tbl:trust_trajectory}` | Trust score and role at representative outcome checkpoints for a new agent | `03_results.md` |
| `{#tbl:gate_outcomes}` | Gate-score outcomes under varied agent and proposal conditions | `03_results.md` |
| `{#tbl:mcp_tools}` | Colony Kernel MCP tool inventory — 8 tools with name and purpose | `03_results.md` |
| `{#tbl:dependent_variables}` | Dependent variables for the configured benchmark protocol | `05_experimental_setup.md` |
| `{#tbl:experimental_gate_thresholds}` | Gate decision thresholds for experimental configuration | `05_experimental_setup.md` |
| `{#tbl:experimental_gate_weights}` | Gate score dimension weights for experimental configuration | `05_experimental_setup.md` |
| `{#tbl:experimental_decay_rates}` | Pheromone decay rate classes for experimental configuration | `05_experimental_setup.md` |
| `{#tbl:resource_budget_caps}` | Resource budget caps from `kernel.yaml` | `05_experimental_setup.md` |
| `{#tbl:role_ladder}` | `AgentRole` variants, promotion thresholds, and permitted actions | `05_experimental_setup.md` |
| `{#tbl:software_environment}` | Software environment for the manuscript snapshot | `05_experimental_setup.md` |
| `{#tbl:configuration_provenance}` | Configuration provenance for the rendered manuscript | `06_reproducibility.md` |
| `{#tbl:artifact_registry}` | Generated artifact registry for the manuscript pipeline | `06_reproducibility.md` |
| `{#tbl:quality_gate_summary}` | Quality gate summary used by the reproducibility certificate | `06_reproducibility.md` |
| `{#tbl:software_versions}` | Software versions used by the reproducibility certificate | `06_reproducibility.md` |
| `{#tbl:evaluation_snapshot}` | Evaluation snapshot inputs and generated artifacts | `06_reproducibility.md` |

## Figure References

Figures are referenced using pandoc-crossref syntax:

```markdown
![Caption text.](figures/filename.png){#fig:label width=80%}

<!-- Reference in text -->
[@fig:label] shows the architecture.
```

Figure source PNG files live in `output/figures/` and are generated by `scripts/generate_manuscript_figures.py`. The generator reads `output/data/manuscript_variables.json`, `docs/manuscript/config.yaml`, and `config/colony_kernel/roles.yaml` before drawing the assets, then stamps each figure with the manuscript version, config hash, and generation date. Re-run the script to regenerate all figures before rendering.

### Figure label registry

| Label | PNG filename | Generator function | Source file |
|---|---|---|---|
| `{#fig:architecture}` | `subsystem_architecture.png` | `fig_subsystem_architecture()` | `02_methodology.md` |
| `{#fig:pheromone_decay}` | `pheromone_decay.png` | `fig_pheromone_decay()` | `02_methodology.md` |
| `{#fig:falsification_vectors}` | `falsification_vectors.png` | `fig_falsification_vectors()` | `02_methodology.md` |
| `{#fig:pressure_loop}` | `colony_pressure_loop.png` | `fig_colony_pressure_loop()` | `02_methodology.md` |
| `{#fig:trust_trajectory}` | `trust_trajectory.png` | `fig_trust_trajectory()` | `03_results.md` |
| `{#fig:gate_heatmap}` | `gate_score_heatmap.png` | `fig_gate_score_heatmap()` | `03_results.md` |

## `{{VARIABLE}}` Token Table

All `{{TOKEN}}` placeholders are resolved at render time by `scripts/z_generate_manuscript_variables.py`, which writes `output/data/manuscript_variables.json` and substituted Markdown under `output/manuscript/`. An unresolved token causes a non-zero exit before the PDF renderer runs. The table below is the complete v1.3.0 generated variable inventory; tokens marked "generated map only" are emitted for reproducibility or downstream templates but are not currently referenced by the numbered manuscript sections.

| Token | Category | Section(s) |
|---|---|---|
| `{{ARTIFACT_CONFIG_FILES}}` | ARTIFACT | `06_reproducibility.md` |
| `{{ARTIFACT_MCP_TOOLS}}` | ARTIFACT | `06_reproducibility.md` |
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
| `{{CONFIG_FALSIFICATION_VECTORS}}` | CONFIG | `01_introduction.md`, `05_experimental_setup.md` |
| `{{CONFIG_FIRST_AUTHOR}}` | CONFIG | `00_00_cover.md`, `00_abstract.md`, `06_reproducibility.md` |
| `{{CONFIG_GATE_EXECUTE_THRESHOLD}}` | CONFIG | `00_abstract.md`, `01_introduction.md`, `05_experimental_setup.md` |
| `{{CONFIG_GATE_HOLD_THRESHOLD}}` | CONFIG | `01_introduction.md`, `05_experimental_setup.md` |
| `{{CONFIG_GATE_WEIGHT_BUDGET}}` | CONFIG | `01_introduction.md` |
| `{{CONFIG_GATE_WEIGHT_COMPLETENESS}}` | CONFIG | generated map only |
| `{{CONFIG_GATE_WEIGHT_RISK}}` | CONFIG | generated map only |
| `{{CONFIG_GATE_WEIGHT_TRUST}}` | CONFIG | generated map only |
| `{{CONFIG_GITHUB_REPOSITORY}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_HASH}}` | CONFIG | `06_reproducibility.md` |
| `{{CONFIG_KEYWORDS}}` | CONFIG | `00_abstract.md`, `06_reproducibility.md` |
| `{{CONFIG_MCP_TOOL_COUNT}}` | CONFIG | `00_abstract.md` |
| `{{CONFIG_MODULE_COUNT}}` | CONFIG | `00_abstract.md` |
| `{{CONFIG_PHEROMONE_RETENTION_FAST}}` | CONFIG | generated map only |
| `{{CONFIG_PHEROMONE_RETENTION_FAST_PCT}}` | CONFIG | `02_methodology.md` |
| `{{CONFIG_PHEROMONE_RETENTION_NORMAL}}` | CONFIG | generated map only |
| `{{CONFIG_PHEROMONE_RETENTION_NORMAL_PCT}}` | CONFIG | `02_methodology.md` |
| `{{CONFIG_PHEROMONE_RETENTION_SLOW}}` | CONFIG | generated map only |
| `{{CONFIG_PHEROMONE_RETENTION_SLOW_PCT}}` | CONFIG | `02_methodology.md` |
| `{{CONFIG_PUBLICATION_DATE}}` | CONFIG | generated map only |
| `{{CONFIG_PUBLICATION_DATE_DISPLAY}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_ROLE_COUNT}}` | CONFIG | `00_abstract.md`, `05_experimental_setup.md` |
| `{{CONFIG_SIGNAL_TYPES_COUNT}}` | CONFIG | `00_abstract.md`, `05_experimental_setup.md` |
| `{{CONFIG_SUBTITLE}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_TEST_COUNT}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_TITLE}}` | CONFIG | `00_00_cover.md` |
| `{{CONFIG_TRIAL_COUNT}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_TRIAL_COUNT_MINUS_1}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_TRUST_DELTA_FAIL}}` | CONFIG | `07_scope_and_related_work.md` |
| `{{CONFIG_TRUST_DELTA_PASS}}` | CONFIG | `03_results.md`, `07_scope_and_related_work.md` |
| `{{CONFIG_TRUST_HARD_FLOOR}}` | CONFIG | `01_introduction.md` |
| `{{CONFIG_TRUST_PROMOTE_THRESHOLD}}` | CONFIG | generated map only |
| `{{CONFIG_TRUST_SANDBOX_SCORE}}` | CONFIG | `00_abstract.md` |
| `{{CONFIG_VERSION}}` | CONFIG | `00_abstract.md`, `05_experimental_setup.md`, `06_reproducibility.md` |
| `{{CONFIG_WARMUP_TICKS}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_WORKLOAD_TASK_COUNT}}` | CONFIG | `05_experimental_setup.md` |
| `{{CONFIG_YAML_CONFIG_FILES}}` | CONFIG | `05_experimental_setup.md` |
| `{{GENERATION_TIMESTAMP}}` | ENVIRONMENT | `05_experimental_setup.md`, `06_reproducibility.md` |
| `{{PLATFORM}}` | ENVIRONMENT | generated map only |
| `{{PYTHON_VERSION}}` | ENVIRONMENT | `05_experimental_setup.md`, `06_reproducibility.md` |
| `{{RESULT_COLONY_KERNEL_FILES}}` | RESULT | `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_COLONY_KERNEL_LOC}}` | RESULT | `03_results.md` |
| `{{RESULT_COVERAGE_PCT}}` | RESULT | `00_abstract.md`, `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_GATE_REFUSAL_RATE}}` | RESULT | `00_abstract.md` |
| `{{RESULT_GATE_SCORE_PROMOTED}}` | RESULT | generated map only |
| `{{RESULT_GATE_SCORE_SANDBOX}}` | RESULT | generated map only |
| `{{RESULT_MODULE_DOCS_COUNT}}` | RESULT | `06_reproducibility.md` |
| `{{RESULT_PHEROMONE_FAST_LOSS_8_TICK_PCT}}` | RESULT | `03_results.md` |
| `{{RESULT_PHEROMONE_SLOW_RETENTION_8_TICK_PCT}}` | RESULT | `03_results.md` |
| `{{RESULT_PROPOSALS_TO_PROMOTION}}` | RESULT | generated map only |
| `{{RESULT_RUFF_ERRORS}}` | RESULT | `00_abstract.md`, `06_reproducibility.md` |
| `{{RESULT_TEST_COUNT}}` | RESULT | `00_abstract.md`, `03_results.md`, `06_reproducibility.md` |
| `{{RESULT_TRUST_AFTER_PROMOTION}}` | RESULT | generated map only |
| `{{RESULT_TRUST_AT_0}}` | RESULT | `03_results.md` |
| `{{RESULT_TRUST_AT_12}}` | RESULT | `03_results.md` |
| `{{RESULT_TRUST_AT_3}}` | RESULT | `03_results.md` |
| `{{RESULT_TRUST_AT_6}}` | RESULT | `03_results.md` |
| `{{RESULT_TRUST_AT_9}}` | RESULT | `03_results.md` |
| `{{RESULT_TRUST_CONVERGENCE_STEPS}}` | RESULT | `00_abstract.md` |
| `{{RESULT_TRUST_INITIAL}}` | RESULT | generated map only |
| `{{RESULT_TY_ERRORS}}` | RESULT | `00_abstract.md`, `06_reproducibility.md` |

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
@article{dorigo2004ants,
  author  = {Marco Dorigo and Thomas St\"{u}tzle},
  title   = {Ant Colony Optimization},
  journal = {MIT Press},
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

## Section Numbering

```text
00_00_cover.md             → Cover (unnumbered)
00_01_contents.md          → Contents (generated under output/manuscript/)
00_abstract.md              → Abstract (unnumbered in PDF)
01_introduction.md          → Section 1
02_methodology.md           → Section 2
03_results.md               → Section 3
04_conclusion.md            → Section 4
05_experimental_setup.md    → Section 5
06_reproducibility.md       → Section 6
07_scope_and_related_work.md → Section 7
99_references.md            → References (Pandoc citeproc bibliography)
```

Files are assembled by `scripts/compile_manuscript.py` using lexicographic manuscript section order with generated contents inserted after `00_00_cover.md` and before `00_abstract.md`. The explicit cover file renders first, and `99_` ensures the references anchor comes last.

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
