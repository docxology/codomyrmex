---
title: "Manuscript directory: codomyrmex"
type: "manuscript_guide"
version: "1.3.0"
---

# Manuscript (`docs/manuscript/`)

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

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
- `00_abstract.md` through `07_scope_and_related_work.md` — Manuscript sections.
- `99_references.md` — Minimal citeproc bibliography anchor; no citation syntax prose.
- `SYNTAX.md` — Pandoc syntax reference.
- `layer_contract.yaml` — Infrastructure import boundary declarations.

## Dependencies

- `scripts/compile_manuscript.py` — PDF/HTML rendering pipeline.
- `src/manuscript_variables.py` — Token computation (`compute_variables()`).
- `scripts/z_generate_manuscript_variables.py` — Token injection orchestrator.
- `pandoc-crossref` — required filter for section, figure, table, and equation references; the renderer fails closed if it is missing.

## Development Guidelines

- Never hardcode numeric results; use `{{TOKEN}}` syntax for all computed values.
- Never hardcode rendered section, figure, table, or equation numbers in manuscript source; use `[@sec:*]`, `[@fig:*]`, `[@tbl:*]`, and `[@eq:*]`.
- Run `scripts/z_generate_manuscript_variables.py` after any parameter or result change.
- Keep `src/codomyrmex/tests/unit/colony_kernel/test_manuscript_consistency.py` assertions in sync with all reviewer-sensitive tokens and public claims.
- Follow the Section Modification Protocol below for all prose edits.

## Current State (ground truth)

Key facts agents must use when editing or cross-referencing this manuscript — **do not substitute stale numbers**:

| Fact | Value | Authoritative source |
|:-----|:-----|:---------------------|
| Colony kernel test count | **{{RESULT_TEST_COUNT}}** | `RESULT_TEST_COUNT` token; `uv run pytest src/codomyrmex/tests/unit/colony_kernel/` |
| Gate weight: budget | **0.30** | `config.yaml` → `experiment.gate_score_weights.budget` |
| Gate weight: risk | **0.30** | `config.yaml` → `experiment.gate_score_weights.risk` |
| Gate weight: trust | **0.25** | `config.yaml` → `experiment.gate_score_weights.trust` |
| Gate weight: completeness | **0.15** | `config.yaml` → `experiment.gate_score_weights.completeness` |
| Colony kernel subsystems | **8** | `src/codomyrmex/colony_kernel/*` standalone modules plus `kernel.py` coordinator (PheromoneStore, ResourceLedger, ActuationGate, ConsequenceMemory, RoleAdapter, PruningDaemon, FalsificationWorker, ColonyKernel) |
| MCP tools exposed | **8** | `src/codomyrmex/colony_kernel/mcp_tools.py` |
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
| `00_abstract.md` | Abstract; states the Codomyrmex thesis, colony architecture summary, and build-quality snapshot | `CONFIG_VERSION`, `CONFIG_COLONY_KERNEL_SUBSYSTEMS`, `CONFIG_GATE_EXECUTE_THRESHOLD`, `CONFIG_TRUST_SANDBOX_SCORE`, `CONFIG_ROLE_COUNT`, `CONFIG_MCP_TOOL_COUNT`, `CONFIG_SIGNAL_TYPES_COUNT`, `CONFIG_MODULE_COUNT`, `RESULT_TEST_COUNT`, `RESULT_COVERAGE_PCT`, `RESULT_RUFF_ERRORS`, `RESULT_TY_ERRORS`, `CONFIG_KEYWORDS`, `CONFIG_FIRST_AUTHOR` | None |
| `01_introduction.md` | Motivation, problem framing, paper organisation | `CONFIG_FALSIFICATION_VECTORS`, `CONFIG_GATE_EXECUTE_THRESHOLD`, `CONFIG_GATE_HOLD_THRESHOLD`, `CONFIG_GATE_WEIGHT_BUDGET`, `CONFIG_TRUST_HARD_FLOOR` | None |
| `02_methodology.md` | Colony Control Plane design, pheromone model, actuation gate logic, trust dynamics, role lifecycle, falsification worker | `CONFIG_BASE_EVAPORATION_RATE`, `CONFIG_PHEROMONE_RETENTION_FAST_PCT`, `CONFIG_PHEROMONE_RETENTION_NORMAL_PCT`, `CONFIG_PHEROMONE_RETENTION_SLOW_PCT` | `fig:architecture`, `fig:pheromone_decay`, `fig:falsification_vectors`, `fig:pressure_loop` |
| `03_results.md` | Implementation outcomes: test suite, trust dynamics, gate distribution, documentation completeness | `ARTIFACT_TEST_SUITES`, `CONFIG_COLONY_KERNEL_SUBSYSTEMS`, `CONFIG_TRUST_DELTA_PASS`, `RESULT_COLONY_KERNEL_FILES`, `RESULT_COLONY_KERNEL_LOC`, `RESULT_COVERAGE_PCT`, `RESULT_PHEROMONE_FAST_LOSS_8_TICK_PCT`, `RESULT_PHEROMONE_SLOW_RETENTION_8_TICK_PCT`, `RESULT_TEST_COUNT`, `RESULT_TRUST_AT_0`, `RESULT_TRUST_AT_12`, `RESULT_TRUST_AT_3`, `RESULT_TRUST_AT_6`, `RESULT_TRUST_AT_9` | `fig:trust_trajectory`, `fig:gate_heatmap` |
| `04_conclusion.md` | Summary of contributions, ecological metaphor, future directions | None | None |
| `05_experimental_setup.md` | Gate thresholds, trust parameters, pheromone decay rates, budget caps, gate weights, software environment | `CONFIG_AGENT_COUNT`, `CONFIG_BUDGET_MAX_LLM_CALLS`, `CONFIG_BUDGET_MAX_RISK`, `CONFIG_BUDGET_MAX_RUNTIME`, `CONFIG_BUDGET_MAX_SECURITY`, `CONFIG_DECAY_RATE_NORMAL`, `CONFIG_FALSIFICATION_VECTORS`, `CONFIG_GATE_EXECUTE_THRESHOLD`, `CONFIG_GATE_HOLD_THRESHOLD`, `CONFIG_ROLE_COUNT`, `CONFIG_SIGNAL_TYPES_COUNT`, `CONFIG_TEST_COUNT`, `CONFIG_TRIAL_COUNT`, `CONFIG_TRIAL_COUNT_MINUS_1`, `CONFIG_VERSION`, `CONFIG_WARMUP_TICKS`, `CONFIG_WORKLOAD_TASK_COUNT`, `CONFIG_YAML_CONFIG_FILES`, `GENERATION_TIMESTAMP`, `PYTHON_VERSION` | None |
| `06_reproducibility.md` | Configuration provenance, artifact registry, quality-gate summary | `ARTIFACT_CONFIG_FILES`, `ARTIFACT_MCP_TOOLS`, `ARTIFACT_TEST_SUITES`, `CONFIG_FIRST_AUTHOR`, `CONFIG_HASH`, `CONFIG_KEYWORDS`, `CONFIG_VERSION`, `GENERATION_TIMESTAMP`, `PYTHON_VERSION`, `RESULT_COLONY_KERNEL_FILES`, `RESULT_COVERAGE_PCT`, `RESULT_MODULE_DOCS_COUNT`, `RESULT_RUFF_ERRORS`, `RESULT_TEST_COUNT`, `RESULT_TY_ERRORS` | None |
| `07_scope_and_related_work.md` | Scope limitations, related orchestration frameworks, capability security, AI risk-management positioning, threat-informed zero-trust/supply-chain positioning, agentic-security benchmark scholarship, assurance-case / external-benchmark positioning, runtime-assurance, provenance, privacy-action, cyber-capability, visibility, and harmful-agent evaluation scholarship | `CONFIG_TRUST_DELTA_FAIL`, `CONFIG_TRUST_DELTA_PASS` | None |
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

`src/manuscript_variables.py::compute_variables()` emits the complete generated
variable map. The v1.3.0 map currently contains 78 keys; the auditable snapshot
is `output/data/manuscript_variables.json`, and the full source/section table is
maintained in [SYNTAX.md](SYNTAX.md). Do not duplicate that full table here.

The categories are:

- `CONFIG_*`: values read from `docs/manuscript/config.yaml`, counts derived from source/config files, and deterministic config-derived calculations.
- `RESULT_*`: live repository measurements and deterministic simulation outputs used by the paper.
- `ARTIFACT_*`: counts of versioned or generated artifacts that the reproducibility section reports.
- `PYTHON_VERSION`, `PLATFORM`, `GENERATION_TIMESTAMP`: environment values captured at generation time.

## `{{VARIABLE}}` Protocol

Numeric values that come from configuration or analysis outputs **must** use `{{VARIABLE_NAME}}` syntax. Hardcoding a value that will change when `config.yaml` is edited or the codebase evolves is the primary cause of manuscript drift.

**The 3-step injection pipeline:**

1. **Compute** — `scripts/z_generate_manuscript_variables.py` calls `src/manuscript_variables.py::compute_variables()` to compute all token values. `compute_variables()` reads gate parameters, trust thresholds, decay rates, and budget caps from `docs/manuscript/config.yaml` (via `yaml.safe_load`); counts modules, files, and documentation artefacts directly from the repository filesystem; and captures the Python version, platform, and generation timestamp from the runtime environment.

2. **Persist** — The script writes the complete `{TOKEN: value}` mapping to `output/data/manuscript_variables.json`. This JSON file is the auditable record of every value injected into the rendered manuscript.

3. **Render** — The script writes resolved copies of each `docs/manuscript/*.md` template to `output/manuscript/*.md`, substituting every `{{TOKEN}}` with its resolved string value. `scripts/compile_manuscript.py --pdf` inserts generated contents after the cover and renders the **substituted** copies from `output/manuscript/`, never the source templates.

**Adding a new token:**

1. Add a key/value pair to the `variables` dict inside `src/manuscript_variables.py::compute_variables()`.
2. Add or update an assertion in `src/codomyrmex/tests/unit/colony_kernel/test_manuscript_consistency.py` when the token changes a reviewer-sensitive public claim.
3. Verify: `python -c "import json; d=json.load(open('output/data/manuscript_variables.json')); print(d['MY_TOKEN'])"`
4. Reference in a manuscript file as `{{MY_TOKEN}}`.

**Detecting unresolved tokens** (run before rendering):

```bash
grep -r "{{" output/manuscript/ 2>/dev/null \
  && echo "UNRESOLVED TOKENS — re-run z_generate_manuscript_variables.py" \
  || echo "All tokens resolved"
```

## Section Modification Protocol

Follow these steps in order whenever prose, parameters, or measured results change:

1. **Update prose** in the relevant section file(s) under `docs/manuscript/`. For parameter changes, update `docs/manuscript/config.yaml` first; prose tokens will resolve automatically in step 3.
2. **Update tests** — add or extend assertions in `src/codomyrmex/tests/unit/colony_kernel/test_manuscript_consistency.py` for any reviewer-sensitive token; update functional tests in `src/codomyrmex/tests/unit/colony_kernel/` if colony kernel behaviour changed.
3. **Regenerate variables** — re-run the injection orchestrator to recompute all tokens and produce updated substituted copies:
   ```bash
   uv run python scripts/z_generate_manuscript_variables.py
   ```
4. **Verify all tokens resolved:**
   ```bash
   grep -r "{{" output/manuscript/ || echo "All resolved"
   ```
5. **Render PDF** from the repository root:
   ```bash
   uv run python scripts/compile_manuscript.py --pdf
   ```

## RASP Conventions

1. Every `{{TOKEN}}` in the source manuscript files must have a corresponding key in `compute_variables()`. Reviewer-sensitive tokens and public claims must have corresponding assertions in `src/codomyrmex/tests/unit/colony_kernel/test_manuscript_consistency.py`. A manuscript file that references an undefined token causes a non-zero exit before the PDF renderer runs.
2. `src/manuscript_variables.py` is the only manuscript variable generator. Colony kernel modules must remain infrastructure-free.
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
- [`../../src/manuscript_variables.py`](../../src/manuscript_variables.py) — Variable computation logic (`compute_variables()`)
- [`../../scripts/z_generate_manuscript_variables.py`](../../scripts/z_generate_manuscript_variables.py) — Thin orchestrator that runs the above and writes output files
