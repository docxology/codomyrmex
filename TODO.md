# Codomyrmex TODO — manuscript publication hardening

**Version**: v1.3.0 technical report
**Scope**: source-current manuscript, scholarly audit, statistics, formalism, figures,
rendered QA, and release receipts.

This file contains only open publication blockers and explicitly scoped research
work. Completed historical work belongs in [CHANGELOG.md](CHANGELOG.md). Numeric
release values are evidence-bound outputs, not TODO snapshots.

## Publication blockers

| ID | Status | Artifact | Evidence required | Exit criterion |
|:---|:---|:---|:---|:---|
| P1 | Complete for current checkout | `output/data/manuscript_variables.json`, `output/figures/figure_registry.json`, `output/manuscript/`, `output/paper.html`, `output/paper-content.pdf`, `output/paper.pdf` | Producer-order regeneration from the current checkout and matching config/source hashes | `--require-source-current` passes after variables, figures, Markdown, HTML, PDFs, and receipts are regenerated |
| P2 | Complete for current cited inventory | `docs/manuscript/references.bib`, `docs/manuscript/claim_ledger.yaml`, `docs/plans/manuscript-red-team-review-2026-08-01.md` | Source-current DOI/arXiv/official-locator checks and claim-by-claim fit review; preserve negative, conditional, and unrun claims | Online bibliography audit and claim-ledger coverage pass with access limitations recorded |
| P3 | Complete for current synthetic fixture | `src/codomyrmex/colony_kernel/research/benchmark.py`, `research/metrics.py`, `tests/unit/colony_kernel/test_research_harness.py` | Independent recomputation of estimands, denominators, paired differences, resampling intervals, and mediator provenance | Focused tests pass and no synthetic fixture is described as population, calibration, or production-gate evidence |
| P4 | Complete for current manuscript | `docs/manuscript/11_supplemental_notation.md` and all formal sections/captions | Symbol crosswalk review for indices, field state, hazard/gate, trust, Active Inference, and paired statistics | Notation regression tests pass and equations/captions resolve to one glossary without collisions |
| P5 | Complete for current render | `docs/manuscript/config.yaml`, `src/codomyrmex/manuscript/figures/`, rendered HTML/PDF | Pixel-level review of all 18 figures, metadata, captions, alt text, long descriptions, ranges, contrast, print legibility, and evidence boundaries | Figure registry, HTML image-description checks, rendered-page inspection, and browser pass all pass |
| P6 | Complete for current PDFs; usability remains bounded | `output/paper-content.pdf`, `output/paper.pdf`, `docs/manuscript/06_reproducibility.md` | `qpdf --check`, searchable text, renderer diagnostics, and independent veraPDF PDF/UA-2 validation | Current content and distribution PDFs pass veraPDF PDF/UA-2; retain the limitation that this does not establish universal assistive-technology, display, print, or reader usability |
| P7 | Complete and published for v1.3.0 | `output/release/codomyrmex-1.3.0/`, Zenodo record `10.5281/zenodo.21750801`, and GitHub release `v1.3.0-paper` | Current source-state, config/source hashes, artifact hash agreement, validation receipts, detached manifest verification, and live-record checks | DOI-bearing bundle is source-current, Zenodo is published, and the GitHub release points to the same versioned artifacts |

## Explicitly scoped research items

Each item remains a research question or evidence requirement, not a completed result.

| ID | Status | Artifact | Evidence required | Exit criterion |
|:---|:---|:---|:---|:---|
| R2 | Open | External-actuation observation adapter and retained traces | Independently observed execution/outcomes, adverse cases, restart/concurrency evidence, and a declared baseline | Reproducible externally observed comparison with negative results retained |
| R3 | Open | Adversarial workload adapter and threat-stratified analysis | External or independently curated hostile workloads, held-out protocol, paired assignment, and falsifiers | Predeclared safety/utility analysis is complete and bounded to the workload |
| R4 | Open | Trust calibration study | Attested outcomes, calibration labels, missingness policy, calibration diagnostics, and held-out evaluation | Calibration status changes only after independent outcome evidence supports it |
| R5 | Open | Persistence and concurrency study | Multi-process/restart traces, lock/transaction evidence, crash injection, and recovery analysis | Durability and concurrency claims are supported by retained replayable artifacts |
| R6 | Open | External effectiveness and production-safety evaluation | Independent deployment-specific observation, safety case, rollback evidence, and operational review | No effectiveness or production-safety claim is made until the full evidence bundle passes |
| F3 | Open formalism gap | `docs/manuscript/10_formalism_code_crosswalk.md` and formal bridge | Explicit state/transition mapping, proof obligations, solver assumptions, and failure semantics | Encoded obligations and their limits are independently reviewed; no whole-program proof is implied |
| F5 | Open formalism gap | Active Inference crosswalk and research adapter | Declared observations, latent states, likelihoods, priors, posteriors, policies, preferences, inference procedure, and held-out checks | A probabilistic result is reported only after the model is executed and compared against the deterministic gate |
| F6 | Open formalism gap | Runtime-assurance and attestation formalism | External observation model, authorization/actuation linkage, threat model, and assurance argument | A bounded assurance case is retained; local caller-reported state is not promoted to external safety |

## Working constraints

- v1.3.0 publication is complete: concept DOI `10.5281/zenodo.21750800`, version DOI
  `10.5281/zenodo.21750801`, and GitHub release tag `v1.3.0-paper`. Future manuscript
  changes require a new version and a new source-bound release sequence.
- Preserve the dirty `src/codomyrmex/agents/open_gauss` submodule as a separate ownership
  boundary; no cleanup or edits are authorized.
- Preserve failed gates, negative controls, `not_estimated` calibration status, and
  conditional or `not_run` claims.
- Regenerate in producer order: variables and coverage → figures/registry → hydrated
  Markdown → HTML/content/distribution PDFs → bibliography audit → rendered/link checks
  → release bundle preparation and verification.
