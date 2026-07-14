---
title: "Manuscript directory: codomyrmex"
type: "manuscript_guide"
version: "1.3.0"
---

# Manuscript (`docs/manuscript/`)

**Status**: Active. Generated metadata and token inventory are authoritative.

Repository-wide agent rules live in [`../AGENTS.md`](../AGENTS.md). This file covers **manuscript-specific** editing: file roles, `{{VARIABLE}}` token protocol, and the section modification workflow.

## Purpose

This directory contains the Codomyrmex manuscript source files, configuration, and token-injection pipeline. It is the authoritative source for the paper content rendered into PDF and HTML via the local Pandoc pipeline.

## Navigation

- **Directory README**: [README.md](README.md)
- **Syntax Reference**: [SYNTAX.md](SYNTAX.md)
- **Configuration**: [config.yaml](config.yaml)
- **Colony Kernel Specification**: [../modules/colony_kernel/SPEC.md](../modules/colony_kernel/SPEC.md)

## Key Files

- `config.yaml` — Paper metadata and gate/trust/decay parameters.
- `00_abstract.md` through `08_active_inference.md` — Main manuscript sections.
- `90_appendix_design_rationale.md` — Design-rationale appendix.
- `98_acknowledgements.md` — Configuration-injected, unnumbered acknowledgements.
- `99_references.md` — Minimal citeproc bibliography anchor; no citation syntax prose.
- `SYNTAX.md` — Pandoc syntax reference.
- `layer_contract.yaml` — Infrastructure import boundary declarations.

## Dependencies

- `scripts/compile_manuscript.py` — PDF/HTML rendering pipeline.
- `src/codomyrmex/manuscript/variables.py` — Token computation (`compute_variables()`).
- `scripts/z_generate_manuscript_variables.py` — Token injection orchestrator.
- `pandoc-crossref` — required filter for section, figure, table, and equation references; the renderer fails closed if it is missing.

## Development Guidelines

- Never hardcode numeric results; use `{{TOKEN}}` syntax for all computed values.
- Never hardcode rendered section, figure, table, or equation numbers in manuscript source; use `[@sec:*]`, `[@fig:*]`, `[@tbl:*]`, and `[@eq:*]`.
- Run `scripts/z_generate_manuscript_variables.py` after any parameter or result change.
- Keep `tests/unit/colony_kernel/test_manuscript_consistency.py` assertions in sync with reviewer-sensitive tokens and public claims.
- Follow the Section Modification Protocol below for all prose edits.

## Current State (ground truth)

Key facts agents must use when editing or cross-referencing this manuscript — **do not substitute stale numbers**:

| Fact | Value | Authoritative source |
|:-----|:-----|:---------------------|
| Colony kernel test status | **{{RESULT_TEST_PASSED}}/{{RESULT_TEST_COLLECTED}} passed** | `RESULT_TEST_*` tokens; `output/data/colony_kernel_test_status.json` |
| Local hazard input | **`max(RISK, FAILURE)`** | `ActuationGate.witness_state()`; paired kernel tests |
| Outcome integrity | **profile-dependent** | Advisory `caller_reported_unattested`; strict `attested_execution` requires one consumed capability and signed receipt |
| Default state lifetime | **one process; strict file-backed option** | `:memory:` is isolated-test mode; strict file paths persist authorization, receipt, signal, resource, and consequence state |
| Enforcement boundary | **declared action scope only** | Strict `action_scope` map; unregistered mutating paths fail closed and remain explicit bypasses |
| Gate weights | **generated tokens** | live expressions in `ActuationGate.evaluate` |
| Colony kernel subsystems | **generated count** | live `ColonyKernel` ownership graph |
| MCP tools exposed | **generated count** | live decorators in `src/codomyrmex/colony_kernel/mcp_tools.py` |
| Falsification attack vector (import-cycle) | **`CIRCULAR_ARCHITECTURE`** | `AttackVector` enum in `falsification_worker.py` — not `CIRCULAR_DEPS` |
| Transmission bookends | **enabled** | `config.yaml` → `publication.transmission_bookends.enabled: true` |
| Token injection pipeline | 3-step: compute → persist → render | `scripts/z_generate_manuscript_variables.py` → `output/data/manuscript_variables.json` → `output/manuscript/*.md` |
| Contents page | **generated after cover** | `scripts/compile_manuscript.py` writes `output/manuscript/00_01_contents.md` before render |
| Citation and reference pipeline | **pandoc-crossref then citeproc** | `scripts/compile_manuscript.py`; HTML math uses MathML |

## File Inventory

| File / Pattern | Role | `{{VARIABLE}}` Tokens | Figure References |
|---|---|---|---|
| `00_00_cover.md` | Cover page; renders cover art, automatic publication date, ORCID, DOI status, repository, and version metadata | `CONFIG_TITLE`, `CONFIG_SUBTITLE`, `CONFIG_FIRST_AUTHOR`, `CONFIG_PUBLICATION_DATE_DISPLAY`, `CONFIG_AUTHOR_ORCID`, `CONFIG_DOI`, `CONFIG_GITHUB_REPOSITORY`, `CONFIG_VERSION` | `cover.png` |
| `00_01_contents.md` | Generated output-only contents page inserted after the cover; do not edit by hand | None | None |
| `00_abstract.md` | Bounded thesis, paired contract, release gates, and limitations | `CONFIG_COLONY_KERNEL_SUBSYSTEMS`, `CONFIG_FIRST_AUTHOR`, `CONFIG_GATE_EXECUTE_THRESHOLD`, `CONFIG_KEYWORDS`, `CONFIG_MCP_TOOL_COUNT`, `RESULT_COVERAGE_PCT`, `RESULT_RUFF_ERRORS`, `RESULT_TEST_PASSED`, `RESULT_TY_ERRORS` | None |
| `01_introduction.md` | Problem framing, bounded thesis, architecture, evidence boundary | `CONFIG_TRIAL_COUNT` | None |
| `02_methodology.md` | Control-plane design, linear field, gate, trust, labels, pruning, falsification, and feedback sequence | `CONFIG_BASE_EVAPORATION_RATE`, `CONFIG_PHEROMONE_RETENTION_FAST_PCT`, `CONFIG_PHEROMONE_RETENTION_NORMAL_PCT`, `CONFIG_PHEROMONE_RETENTION_SLOW_PCT` | `fig:architecture`, `fig:falsification_vectors`, `fig:pressure_loop` |
| `02_theory.md` | Verified recurrence, local-pressure, gate, trust, and privacy bounds | None | `fig:pheromone_decay`, `fig:gate_score_3d` |
| `03_results.md` | Executed gates, paired locality, analytical score cases, trust fixture, decay, and MCP boundary | Generated row blocks plus scoped gate/result tokens | `fig:trust_trajectory`, `fig:gate_heatmap` |
| `04_conclusion.md` | Summary of contributions, ecological metaphor, future directions | None | None |
| `05_experimental_setup.md` | Proposed benchmark, live gate/field/budget configuration, software snapshot, and pipeline | `CONFIG_AGENT_COUNT`, `CONFIG_BUDGET_MAX_LLM_CALLS`, `CONFIG_BUDGET_MAX_RISK`, `CONFIG_BUDGET_MAX_RUNTIME`, `CONFIG_BUDGET_MAX_SECURITY`, `CONFIG_GATE_EXECUTE_THRESHOLD`, `CONFIG_GATE_HOLD_THRESHOLD`, `CONFIG_TRIAL_COUNT`, `CONFIG_VERSION`, `CONFIG_WARMUP_TICKS`, `CONFIG_WORKLOAD_TASK_COUNT`, `GENERATION_TIMESTAMP`, `PYTHON_VERSION` | None |
| `06_reproducibility.md` | Configuration provenance, artifact registry, quality-gate summary | `ARTIFACT_CONFIG_FILES`, `ARTIFACT_MCP_TOOLS`, `ARTIFACT_TEST_SUITES`, `CONFIG_FIRST_AUTHOR`, `CONFIG_HASH`, `CONFIG_KEYWORDS`, `CONFIG_VERSION`, `GENERATION_TIMESTAMP`, `PYTHON_VERSION`, `RESULT_COLONY_KERNEL_FILES`, `RESULT_COVERAGE_PCT`, `RESULT_MODULE_DOCS_COUNT`, `RESULT_RUFF_ERRORS`, `RESULT_TEST_PASSED`, `RESULT_TEST_COLLECTED`, `RESULT_TEST_SKIPPED`, `RESULT_TEST_FAILED`, `RESULT_TEST_ERRORS`, `RESULT_TY_ERRORS` | None |
| `07_scope_and_related_work.md` | Bounded comparison with agentic engineering, stigmergy, trust, security, assurance, and external evaluation | None | None |
| `08_active_inference.md` | Explicitly non-equivalent Active Inference crosswalk and implementation agenda | None | `fig:fep_correspondence` |
| `90_appendix_design_rationale.md` | Auditable design choices, rejected alternatives, and calibration boundaries | None | None |
| `98_acknowledgements.md` | Contributor credit | `CONFIG_ACKNOWLEDGEMENTS` | None |
| `99_references.md` | Citeproc bibliography anchor; bibliography rendered from `references.bib` | None | None |
| `config.yaml` | Paper metadata, gate parameters, trust thresholds, pheromone decay rates, budget caps, publication settings, steganography profile | — | — |
| `layer_contract.yaml` | Declares which `src/` files are permitted to import `infrastructure.*`; enforced at CI boundary | — | — |
| `manuscript.css` | HTML rendering style; mirrors the PDF red hyperlink contract | — | — |
| `preamble.md` | LaTeX injections shared by PDF output, including red hyperlinks | — | — |
| `references.bib` | BibTeX bibliography | — | — |
| `SYNTAX.md` | Citation, figure, and cross-reference syntax reference | — | — |
| `README.md` | Human quick-reference for this directory | — | — |
| `AGENTS.md` | This file — agent technical directives | — | — |

## `{{VARIABLE}}` Token Reference

`src/codomyrmex/manuscript/variables.py::compute_variables()` emits the complete generated
variable map. The auditable and complete inventory is
`output/data/manuscript_variables.json`; do not duplicate a static key count here.

The categories are:

- `CONFIG_*`: values read from `docs/manuscript/config.yaml`, counts derived from source/config files, and deterministic config-derived calculations.
- `RESULT_*`: live repository measurements and deterministic simulation outputs used by the paper.
- `ARTIFACT_*`: counts of versioned or generated artifacts that the reproducibility section reports.
- `PYTHON_VERSION`, `PLATFORM`, `GENERATION_TIMESTAMP`: environment values captured at generation time.

## `{{VARIABLE}}` Protocol

Numeric values that come from configuration or analysis outputs **must** use `{{VARIABLE_NAME}}` syntax. Hardcoding a value that will change when `config.yaml` is edited or the codebase evolves is the primary cause of manuscript drift.

**The 3-step injection pipeline:**

1. **Compute** — `scripts/z_generate_manuscript_variables.py` calls `src/codomyrmex/manuscript/variables.py::compute_variables()`. It reads manuscript metadata, runtime configuration, and live source/test facts; executes the scoped pytest/coverage, Ruff, and ty gates; and fails instead of reusing stale coverage when any gate fails.

2. **Persist** — The script writes the complete `{TOKEN: value}` mapping to `output/data/manuscript_variables.json`. This JSON file is the auditable record of every value injected into the rendered manuscript.

3. **Render** — The script writes resolved copies of each `docs/manuscript/*.md` template to `output/manuscript/*.md`, substituting every `{{TOKEN}}` with its resolved string value. `scripts/compile_manuscript.py --pdf` inserts generated contents after the cover and renders the **substituted** copies from `output/manuscript/`, never the source templates.

**Adding a new token:**

1. Add a key/value pair to the `variables` dict inside `src/codomyrmex/manuscript/variables.py::compute_variables()`.
2. Add or update an assertion in `tests/unit/colony_kernel/test_manuscript_consistency.py` when the token changes a reviewer-sensitive public claim.
3. Verify: `python -c "import json; d=json.load(open('output/data/manuscript_variables.json')); print(d['MY_TOKEN'])"`
4. Reference in a manuscript file as `{{MY_TOKEN}}`.

**Detecting unresolved tokens** (run before rendering):

```bash
grep -r "{{" output/manuscript/ --include="*.md" 2>/dev/null \
  && echo "UNRESOLVED TOKENS — re-run z_generate_manuscript_variables.py" \
  || echo "All tokens resolved"
```

`--include="*.md"` excludes `output/manuscript/references.bib`, where `{{...}}` is
standard BibTeX capitalization-protection syntax (e.g. `{{MRKL}}`, `{{ReAct}}`), not an
unresolved `{{TOKEN}}` — without it this check always reports a false positive.

## Section Modification Protocol

Follow these steps in order whenever prose, parameters, or measured results change:

1. **Update prose** in the relevant section file(s) under `docs/manuscript/`. For parameter changes, update `docs/manuscript/config.yaml` first; prose tokens will resolve automatically in step 3.
2. **Update tests** — add or extend assertions in `tests/unit/colony_kernel/test_manuscript_consistency.py` for any reviewer-sensitive token; update functional tests in `tests/unit/colony_kernel/` if behavior changed.
3. **Regenerate variables** — re-run the injection orchestrator to recompute all tokens and produce updated substituted copies:
   ```bash
   uv run python scripts/z_generate_manuscript_variables.py
   ```
4. **Verify all tokens resolved:**
   ```bash
   grep -r "{{" output/manuscript/ --include="*.md" || echo "All resolved"
   ```
5. **Render PDF** from the repository root:
   ```bash
   uv run python scripts/compile_manuscript.py --pdf
   ```

## RASP Conventions

1. Every `{{TOKEN}}` in the source manuscript files must have a corresponding key in `compute_variables()`. Reviewer-sensitive tokens and public claims must have corresponding assertions in `tests/unit/colony_kernel/test_manuscript_consistency.py`. A manuscript file that references an undefined token causes a non-zero exit before the PDF renderer runs.
2. `src/codomyrmex/manuscript/variables.py` is the only manuscript variable generator. Colony kernel modules remain independent of the parent template infrastructure.
3. Do not hardcode numeric results (test counts, coverage percentages, gate thresholds) directly into manuscript prose. Every claim that can drift must be backed by a token. Use the **Current State** table above when hand-editing prose that cannot use a token.
4. The falsification attack vector for import-cycle detection is `CIRCULAR_ARCHITECTURE`, not `CIRCULAR_DEPS`. The canonical enum lives in `src/codomyrmex/colony_kernel/falsification_worker.py`; do not invent aliases.
5. Avoid boilerplate closers ("In summary", "In conclusion") at the end of sections unless the section genuinely warrants them.
6. When cross-referencing sections, use Pandoc-crossref `[@sec:label]` syntax — never hardcoded section numbers.
7. When adding a table, figure, or display equation, add a stable `{#tbl:*}`, `{#fig:*}`, or `{#eq:*}` label and reference it in prose.
8. Keep citation syntax examples in `SYNTAX.md`; do not put raw `[@key]` examples or citation-key inventories in `99_references.md`.

## See also

- [`README.md`](README.md) — Quick orientation for this directory
- [`SYNTAX.md`](SYNTAX.md) — Pandoc syntax reference (citations, cross-references)
- [`config.yaml`](config.yaml) — Authoritative source for all configurable parameters
- [`layer_contract.yaml`](layer_contract.yaml) — Infrastructure import boundary declarations
- [`../modules/colony_kernel/SPEC.md`](../modules/colony_kernel/SPEC.md) — Colony Kernel formal specification
- [`../../src/codomyrmex/manuscript/variables.py`](../../src/codomyrmex/manuscript/variables.py) — Variable computation logic (`compute_variables()`)
- [`../../scripts/z_generate_manuscript_variables.py`](../../scripts/z_generate_manuscript_variables.py) — Thin orchestrator that runs the above and writes output files
