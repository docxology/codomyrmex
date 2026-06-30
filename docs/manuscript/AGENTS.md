---
title: "Manuscript directory: codomyrmex"
type: "manuscript_guide"
version: "1.2.7"
---

# Manuscript (`projects/codomyrmex/docs/manuscript/`)

Repository-wide agent rules live in [`../AGENTS.md`](../AGENTS.md). This file covers **manuscript-specific** editing: file roles, `{{VARIABLE}}` token protocol, and the section modification workflow.

## Current State (ground truth)

Key facts agents must use when editing or cross-referencing this manuscript — **do not substitute stale numbers**:

| Fact | Value | Authoritative source |
|:---|:---|:---|
| Colony kernel test count | **433** | `RESULT_TEST_COUNT` token; `uv run pytest src/codomyrmex/colony_kernel/tests/` |
| Gate weight: budget | **0.30** | `config.yaml` → `experiment.gate_score_weights.budget` |
| Gate weight: risk | **0.30** | `config.yaml` → `experiment.gate_score_weights.risk` |
| Gate weight: trust | **0.25** | `config.yaml` → `experiment.gate_score_weights.trust` |
| Gate weight: completeness | **0.15** | `config.yaml` → `experiment.gate_score_weights.completeness` |
| Colony kernel subsystems | **8** | `src/codomyrmex/colony_kernel/kernel.py` (PheromoneStore, ResourceLedger, ActuationGate, ConsequenceMemory, RoleAdapter, PruningDaemon, FalsificationWorker, ColonyKernel coordinator) |
| MCP tools exposed | **8** | `src/codomyrmex/colony_kernel/mcp_tools.py` |
| Falsification attack vector (import-cycle) | **`CIRCULAR_ARCHITECTURE`** | `AttackVector` enum in `falsification_worker.py` — not `CIRCULAR_DEPS` |
| Transmission bookends | **enabled** | `config.yaml` → `publication.transmission_bookends.enabled: true` |
| Token injection pipeline | 3-step: compute → persist → render | `scripts/z_generate_manuscript_variables.py` → `output/data/manuscript_variables.json` → `output/manuscript/*.md` |

## File Inventory

| File / Pattern | Role | `{{VARIABLE}}` Tokens | Figure References |
|---|---|---|---|
| `00_abstract.md` | Abstract; states the Codomyrmex thesis, colony architecture summary, and build-quality snapshot | `CONFIG_VERSION`, `CONFIG_COLONY_KERNEL_SUBSYSTEMS`, `CONFIG_GATE_EXECUTE_THRESHOLD`, `CONFIG_TRUST_SANDBOX_SCORE`, `CONFIG_ROLE_COUNT`, `CONFIG_MCP_TOOL_COUNT`, `CONFIG_SIGNAL_TYPES_COUNT`, `CONFIG_MODULE_COUNT`, `RESULT_TEST_COUNT`, `RESULT_COVERAGE_PCT`, `RESULT_RUFF_ERRORS`, `RESULT_TY_ERRORS`, `CONFIG_KEYWORDS`, `CONFIG_FIRST_AUTHOR` | None |
| `01_introduction.md` | Motivation, problem framing, paper organisation | None | None |
| `02_methodology.md` | Colony Control Plane design, pheromone model, actuation gate logic, trust dynamics, role lifecycle, falsification worker | `CONFIG_COLONY_KERNEL_SUBSYSTEMS`, `CONFIG_ROLE_COUNT`, `CONFIG_SIGNAL_TYPES_COUNT`, `CONFIG_DECAY_RATES_COUNT`, `CONFIG_DECAY_RATE_FAST`, `CONFIG_DECAY_RATE_NORMAL`, `CONFIG_DECAY_RATE_SLOW`, `CONFIG_GATE_WEIGHT_BUDGET`, `CONFIG_GATE_WEIGHT_RISK`, `CONFIG_GATE_WEIGHT_TRUST`, `CONFIG_GATE_WEIGHT_COMPLETENESS`, `CONFIG_BUDGET_DIMENSIONS_COUNT`, `CONFIG_BUDGET_MAX_LLM_CALLS`, `CONFIG_BUDGET_MAX_RUNTIME`, `CONFIG_BUDGET_MAX_RISK`, `CONFIG_BUDGET_MAX_SECURITY`, `CONFIG_FALSIFICATION_VECTORS` | None |
| `03_results.md` | Empirical outcomes: test suite, trust dynamics, gate distribution, documentation completeness | `RESULT_TEST_COUNT`, `RESULT_COVERAGE_PCT`, `RESULT_RUFF_ERRORS`, `RESULT_TY_ERRORS`, `RESULT_TRUST_INITIAL`, `RESULT_TRUST_AFTER_PROMOTION`, `RESULT_GATE_SCORE_SANDBOX`, `RESULT_GATE_SCORE_PROMOTED`, `RESULT_PROPOSALS_TO_PROMOTION`, `RESULT_COLONY_KERNEL_LOC`, `RESULT_COLONY_KERNEL_FILES`, `RESULT_MODULE_DOCS_COUNT` | None |
| `04_conclusion.md` | Summary of contributions, ecological metaphor, future directions | None | None |
| `05_experimental_setup.md` | Gate thresholds, trust parameters, pheromone decay rates, budget caps, gate weights, software environment | `CONFIG_VERSION`, `CONFIG_GATE_EXECUTE_THRESHOLD`, `CONFIG_GATE_HOLD_THRESHOLD`, `CONFIG_TRUST_SANDBOX_SCORE`, `CONFIG_TRUST_HARD_FLOOR`, `CONFIG_TRUST_PROMOTE_THRESHOLD`, `CONFIG_SIGNAL_TYPES_COUNT`, `CONFIG_DECAY_RATES_COUNT`, `CONFIG_DECAY_RATE_FAST`, `CONFIG_DECAY_RATE_NORMAL`, `CONFIG_DECAY_RATE_SLOW`, `CONFIG_GATE_WEIGHT_BUDGET`, `CONFIG_GATE_WEIGHT_RISK`, `CONFIG_GATE_WEIGHT_TRUST`, `CONFIG_GATE_WEIGHT_COMPLETENESS`, `CONFIG_BUDGET_DIMENSIONS_COUNT`, `CONFIG_BUDGET_MAX_LLM_CALLS`, `CONFIG_BUDGET_MAX_RUNTIME`, `CONFIG_BUDGET_MAX_RISK`, `CONFIG_BUDGET_MAX_SECURITY`, `CONFIG_YAML_CONFIG_FILES`, `PYTHON_VERSION`, `PLATFORM`, `GENERATION_TIMESTAMP` | None |
| `06_reproducibility.md` | Configuration provenance, artifact registry, quality-gate summary | `CONFIG_HASH`, `CONFIG_VERSION`, `CONFIG_FIRST_AUTHOR`, `CONFIG_KEYWORDS`, `ARTIFACT_TEST_SUITES`, `ARTIFACT_CONFIG_FILES`, `ARTIFACT_MCP_TOOLS`, `RESULT_MODULE_DOCS_COUNT`, `RESULT_COLONY_KERNEL_FILES`, `RESULT_TEST_COUNT`, `RESULT_COVERAGE_PCT`, `RESULT_RUFF_ERRORS`, `RESULT_TY_ERRORS` | None |
| `07_scope_and_related_work.md` | Scope limitations, comparisons with related orchestration frameworks | None | None |
| `99_references.md` | Narrative references section; bibliography rendered from `references.bib` | None | None |
| `config.yaml` | Paper metadata, gate parameters, trust thresholds, pheromone decay rates, budget caps, publication settings, steganography profile | — | — |
| `layer_contract.yaml` | Declares which `src/` files are permitted to import `infrastructure.*`; enforced at CI boundary | — | — |
| `preamble.md` | LaTeX injections shared by PDF output | — | — |
| `references.bib` | BibTeX bibliography | — | — |
| `SYNTAX.md` | Citation, figure, and cross-reference syntax reference | — | — |
| `README.md` | Human quick-reference for this directory | — | — |
| `AGENTS.md` | This file — agent technical directives | — | — |

## `{{VARIABLE}}` Token Reference

All 52 tokens used across the manuscript sections, organised by category:

### Configuration tokens — drawn from `config.yaml` at render time

| Token | Description |
|---|---|
| `CONFIG_VERSION` | Paper version string from `config.yaml` (`paper.version`) |
| `CONFIG_MODULE_COUNT` | Number of top-level Codomyrmex submodules (counted from `src/codomyrmex/`) |
| `CONFIG_COLONY_KERNEL_SUBSYSTEMS` | Count of Colony Control Plane subsystems (8) |
| `CONFIG_MCP_TOOL_COUNT` | Number of MCP tools registered in the public surface |
| `CONFIG_GATE_EXECUTE_THRESHOLD` | Composite score threshold for EXECUTE decision |
| `CONFIG_GATE_HOLD_THRESHOLD` | Composite score threshold for HOLD decision (below EXECUTE) |
| `CONFIG_TRUST_SANDBOX_SCORE` | Maximum trust score while agent is in sandbox mode |
| `CONFIG_TRUST_HARD_FLOOR` | Trust floor below which agent is locked in sandbox regardless of gate score |
| `CONFIG_TRUST_PROMOTE_THRESHOLD` | Minimum trust score required before role promotion is considered |
| `CONFIG_SIGNAL_TYPES_COUNT` | Number of distinct typed inter-agent signal channels |
| `CONFIG_DECAY_RATES_COUNT` | Number of distinct pheromone decay rate tiers |
| `CONFIG_DECAY_RATE_FAST` | Fast-decay rate (ephemeral signals) |
| `CONFIG_DECAY_RATE_NORMAL` | Normal-decay rate (standard coordination signals) |
| `CONFIG_DECAY_RATE_SLOW` | Slow-decay rate (persistent consequence signals) |
| `CONFIG_GATE_WEIGHT_BUDGET` | Gate score weight assigned to the budget dimension |
| `CONFIG_GATE_WEIGHT_RISK` | Gate score weight assigned to the risk dimension |
| `CONFIG_GATE_WEIGHT_TRUST` | Gate score weight assigned to the trust dimension |
| `CONFIG_GATE_WEIGHT_COMPLETENESS` | Gate score weight assigned to the completeness dimension |
| `CONFIG_BUDGET_DIMENSIONS_COUNT` | Number of independently tracked budget dimensions |
| `CONFIG_BUDGET_MAX_LLM_CALLS` | Maximum LLM calls permitted per agent per task |
| `CONFIG_BUDGET_MAX_RUNTIME` | Maximum wall-time (seconds) per agent dispatch |
| `CONFIG_BUDGET_MAX_RISK` | Maximum cumulative risk score permitted before HOLD override |
| `CONFIG_BUDGET_MAX_SECURITY` | Maximum security-violation budget before hard refusal |
| `CONFIG_YAML_CONFIG_FILES` | Count of YAML configuration files versioned in `docs/manuscript/` |
| `CONFIG_FALSIFICATION_VECTORS` | Number of adversarial falsification vectors the falsification worker tests |
| `CONFIG_ROLE_COUNT` | Count of canonical agent roles (Scout, Builder, Auditor, Pruner, Reproducer) |
| `CONFIG_FIRST_AUTHOR` | First author name string from `config.yaml` |
| `CONFIG_KEYWORDS` | Comma-joined keyword string from `config.yaml` |
| `CONFIG_HASH` | SHA-256 digest (truncated) of `docs/manuscript/config.yaml` at render time |

### Result tokens — computed from live introspection of the repository

| Token | Description |
|---|---|
| `RESULT_TEST_COUNT` | Total passing tests in the project test suite |
| `RESULT_COVERAGE_PCT` | Branch + statement coverage percentage |
| `RESULT_RUFF_ERRORS` | Count of ruff lint violations (target: 0) |
| `RESULT_TY_ERRORS` | Count of ty static-type diagnostics (target: 0) |
| `RESULT_TRUST_INITIAL` | Baseline trust score assigned to a newly spawned agent |
| `RESULT_TRUST_AFTER_PROMOTION` | Trust score recorded after a successful first promotion |
| `RESULT_GATE_SCORE_SANDBOX` | Typical composite gate score for a sandboxed agent |
| `RESULT_GATE_SCORE_PROMOTED` | Typical composite gate score for a promoted agent |
| `RESULT_PROPOSALS_TO_PROMOTION` | Median number of accepted proposals before first role promotion |
| `RESULT_COLONY_KERNEL_LOC` | Lines of Python source in `src/codomyrmex/colony_kernel/` |
| `RESULT_COLONY_KERNEL_FILES` | Count of `.py` files in `src/codomyrmex/colony_kernel/` |
| `RESULT_MODULE_DOCS_COUNT` | Count of `.md` documentation files for the colony kernel |

### Artifact tokens — counts of generated or versioned artifacts

| Token | Description |
|---|---|
| `ARTIFACT_TEST_SUITES` | Count of `test_*.py` files in the project test directory |
| `ARTIFACT_CONFIG_FILES` | Count of YAML configuration files in `docs/manuscript/` |
| `ARTIFACT_MCP_TOOLS` | Count of MCP tool definition files registered in the public surface |

### Environment tokens — captured from the runtime environment at generation time

| Token | Description |
|---|---|
| `PYTHON_VERSION` | Python interpreter version string (e.g. `3.12.3`) |
| `PLATFORM` | Operating system and architecture string |
| `GENERATION_TIMESTAMP` | ISO-8601 UTC timestamp at which variables were generated |

## `{{VARIABLE}}` Protocol

Numeric values that come from configuration or analysis outputs **must** use `{{VARIABLE_NAME}}` syntax. Hardcoding a value that will change when `config.yaml` is edited or the codebase evolves is the primary cause of manuscript drift.

**The 3-step injection pipeline:**

1. **Compute** — `scripts/z_generate_manuscript_variables.py` calls `src/manuscript_variables.py::compute_variables()` to compute all token values. `compute_variables()` reads gate parameters, trust thresholds, decay rates, and budget caps from `docs/manuscript/config.yaml` (via `yaml.safe_load`); counts modules, files, and documentation artefacts directly from the repository filesystem; and captures the Python version, platform, and generation timestamp from the runtime environment.

2. **Persist** — The script writes the complete `{TOKEN: value}` mapping to `output/data/manuscript_variables.json`. This JSON file is the auditable record of every value injected into the rendered manuscript.

3. **Render** — The script also calls `infrastructure.rendering.manuscript_injection.write_resolved_manuscript_tree()`, which copies each `docs/manuscript/*.md` template to `output/manuscript/*.md`, substituting every `{{TOKEN}}` with its resolved string value. `scripts/03_render_pdf.py` renders the **substituted** copies from `output/manuscript/`, never the source templates.

**Adding a new token:**

1. Add a key/value pair to the `variables` dict inside `src/manuscript_variables.py::compute_variables()`.
2. Add a corresponding assertion in `tests/test_manuscript_variables.py` (the `test_all_manuscript_tokens_are_generated` cross-reference test will fail automatically if a manuscript token is missing from the computed dict).
3. Verify: `python -c "import json; d=json.load(open('projects/codomyrmex/output/data/manuscript_variables.json')); print(d['MY_TOKEN'])"`
4. Reference in a manuscript file as `{{MY_TOKEN}}`.

**Detecting unresolved tokens** (run before rendering):

```bash
grep -r "{{" projects/codomyrmex/output/manuscript/ 2>/dev/null \
  && echo "UNRESOLVED TOKENS — re-run z_generate_manuscript_variables.py" \
  || echo "All tokens resolved"
```

## Section Modification Protocol

Follow these steps in order whenever prose, parameters, or measured results change:

1. **Update prose** in the relevant section file(s) under `docs/manuscript/`. For parameter changes, update `docs/manuscript/config.yaml` first; prose tokens will resolve automatically in step 3.
2. **Update tests** — add or extend assertions in `tests/test_manuscript_variables.py` for any new token; update functional tests in `tests/` if colony kernel behaviour changed.
3. **Regenerate variables** — re-run the injection orchestrator to recompute all tokens and produce updated substituted copies:
   ```bash
   uv run python projects/codomyrmex/scripts/z_generate_manuscript_variables.py
   ```
4. **Verify all tokens resolved:**
   ```bash
   grep -r "{{" projects/codomyrmex/output/manuscript/ || echo "All resolved"
   ```
5. **Render PDF** from the repository root:
   ```bash
   uv run python scripts/03_render_pdf.py --project codomyrmex
   ```

## RASP Conventions

1. Every `{{TOKEN}}` in the source manuscript files must have a corresponding key in `compute_variables()` and a corresponding assertion in `tests/test_manuscript_variables.py`. A manuscript file that references an undefined token causes a non-zero exit before the PDF renderer runs.
2. `src/codomyrmex/manuscript_variables.py` is the only file in `src/codomyrmex/` permitted to import `infrastructure.*` (declared in `layer_contract.yaml`). All other colony kernel modules must remain infrastructure-free.
3. Do not hardcode numeric results (test counts, coverage percentages, gate thresholds) directly into manuscript prose. Every claim that can drift must be backed by a token. Use the **Current State** table above when hand-editing prose that cannot use a token.
4. The falsification attack vector for import-cycle detection is `CIRCULAR_ARCHITECTURE`, not `CIRCULAR_DEPS`. The canonical enum lives in `src/codomyrmex/colony_kernel/falsification_worker.py`; do not invent aliases.
5. Avoid boilerplate closers ("In summary", "In conclusion") at the end of sections unless the section genuinely warrants them.
6. When cross-referencing sections, use Pandoc-crossref `[@sec:label]` syntax — never hardcoded section numbers.

## See also

- [`README.md`](README.md) — Quick orientation for this directory
- [`SYNTAX.md`](SYNTAX.md) — Pandoc syntax reference (citations, cross-references)
- [`config.yaml`](config.yaml) — Authoritative source for all configurable parameters
- [`layer_contract.yaml`](layer_contract.yaml) — Infrastructure import boundary declarations
- [`../docs/rendering_pipeline.md`](../rendering_pipeline.md) — Manuscript → PDF flow
- [`../../src/manuscript_variables.py`](../../src/manuscript_variables.py) — Variable computation logic (`compute_variables()`)
- [`../../scripts/z_generate_manuscript_variables.py`](../../scripts/z_generate_manuscript_variables.py) — Thin orchestrator that runs the above and writes output files
