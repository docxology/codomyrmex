# Codomyrmex Manuscript Red-Team Review — 2026-08-01

## Scope and posture

This is an adversarial review of the complete manuscript-to-release chain for the
v1.3.0 technical report: source prose, claims, citations, formalisms, statistics,
figure producers and metadata, hydrated Markdown, HTML/PDF outputs, validation
receipts, and the publication bundle. The review treats every generated number as
untrusted until its producer, source/configuration identity, denominator, estimand,
and rendered representation agree.

The review phase did not itself authorize publication, DOI assignment, external
benchmark execution, production deployment, or modification of the dirty
`src/codomyrmex/agents/open_gauss` submodule. A subsequent explicit release
instruction authorized the production Zenodo/GitHub publication pass; that pass
uses the DOI and release receipts recorded in the final bundle. The root checkout
baseline was `1356691fea4cb2d6ef5ed0fa656e82460106e4a2`; the nested submodule remains
a separate ownership boundary.

## Findings and disposition

| ID | Severity | Evidence and precondition | Impact | Mitigation in this pass | Residual risk / status |
|:---|:---|:---|:---|:---|:---|
| RT-01 | High | Existing release `source-state.json` recorded an older commit (`6b936d9...`) while the checkout and generated variable snapshot described different states. A reader could receive internally coherent but source-stale artifacts. | Reproducibility and scholarly attribution can silently bind to the wrong source. | Added `--require-source-current`; compare current commit, dirty state, config digest, first-party source digest, hydrated Markdown, HTML/PDF text, release receipts, manifest source state, and released artifact hashes. | Resolved for the current working tree after producer-order regeneration and a passing final source-current run; future edits require the same gate. |
| RT-02 | High | The six-case research fixture compares the same ordered cases, but its mediator is `ReferenceGate`, not production `ActuationGate`; its intervals are percentile resampling summaries, not population confidence intervals. | A caption or prose shortcut could be read as external effectiveness, calibration, or production-gate evidence. | Added explicit sample unit, pair count, denominators, difference direction, interval interpretation, mediator provenance, parity status, regression tests, and direct figure annotation. | No population, calibration, production-safety, or external-effectiveness inference is permitted; production parity remains `not_established`. |
| RT-03 | High | `max(1, attack_case_count)` could conceal an empty attack denominator in a generalized fixture, and legacy `*_ci` names could be read as inferential intervals. | Invented rates or false precision under an empty stratum; statistical terminology can overstate evidence. | Rates now become `None` when no attack cases are declared; denominator metadata and descriptive interval aliases are retained additively while legacy callable/output keys remain compatible. | Current fixture has declared attack cases, but future adapters must report `not_estimated` rather than substitute a denominator. |
| RT-04 | Medium | Formal sections used overlapping symbols for field state, risk clearance, trust repair, feedback, and statistical conditions. | A reader could mistake a field signal for a latent state, a risk map for a trust term, or a condition label for completeness. | Added authoritative `11_supplemental_notation.md`, updated equations/crosswalk/appendix/captions, and added section-order/source-coverage regression checks. | Notation consistency is a source contract, not a proof that the underlying formal bridge is complete. |
| RT-05 | Medium | The safety–utility figure previously left the paired difference/interval implicit and did not visibly identify the mediator boundary. | Visual readers could infer an unpaired frontier or a production-gate comparison. | Added direct condition labels, axis units, paired arrow and interval annotation, pair count/seed title, mediator footer, and parity language in caption and long description. | Resolved for the current render after pixel inspection of all figure-bearing pages and a browser pass; the evidence boundary remains synthetic and reference-gate mediated. |
| RT-06 | Medium | Figure accessibility metadata is generated from configuration and checked structurally, but semantic equivalence does not prove usability across assistive technologies, displays, or print. | A valid registry could be mistaken for universal accessibility or a PDF/UA certification. | Preserved redundant encodings and explicit alt/long-description validation; both current PDFs now independently pass veraPDF PDF/UA-2. | Current artifact-specific PDF/UA-2 conformance is supported; universal assistive-technology, display, print, and reader usability remains unestablished. |
| RT-07 | Medium | Online bibliography verification passed the cited inventory and title/locator checks, but the official Stirling locator for `marsh1994trust` was access-limited (HTTP 403). | A source can be metadata-resolved without every reader being able to inspect the full text; claim fit must not be overstated. | Recorded the limitation in the scholarship audit and claim ledger; retained primary/authoritative locators and bounded literature-dependent claims. | The audit is not a systematic review and does not turn contextual scholarship into evidence for Codomyrmex outcomes. |
| RT-08 | Medium | The ordinary MCP outcome path accepts caller-reported outcomes; local lifecycle attestation binds local records but does not independently observe external actuation. | Trust, safety, and effectiveness language could be promoted beyond the actual observation boundary. | Preserved negative/conditional claim ledger entries, explicit source/provenance language, and “not exploitable under current scope” checks. | External observation, threat-model validation, restart/concurrency, and production safety remain open R2–R6 work. |
| RT-09 | Low | Generated outputs are easy to copy or render independently of the source templates; prior integrity checks covered tokens and image hashes but did not require current source identity across all outputs. | A stale artifact can look plausible and pass local structural checks. | Extended variable manifest provenance, figure-registry schema 4 provenance, release source receipts, and closed-world current-source validation. | A source-current check can only validate the artifacts present; it cannot attest to an unretained external environment or a remote publication. |

## Scholarship audit

The audit covered all cited records and literature-dependent claims in the active
numbered manuscript sections. DOI, arXiv, and official-locator metadata were checked
against primary or authoritative records, with title/author/date/claim-fit review and
unused or unresolved citation detection. The pre-change online audit resolved the cited
inventory without missing, unused, duplicate, unresolved-locator, online-failure, or DOI
title-mismatch findings. The `marsh1994trust` official locator was retained but marked
access-limited after an HTTP 403 response. No citation was upgraded to support an
implementation outcome, calibration, safety, or generalization claim.

## Statistical audit contract

The research output is a deterministic paired fixture. Its statistical unit is one
declared task case observed once under each condition. For case-level outcomes, rates
use the number of declared task cases in the condition; attack-success rates use the
declared attack-case stratum; trace completeness uses emitted traces; paired deltas use
the same ordered cases and the direction “mediated minus baseline.” The resampling unit
is a paired observation. The interval is a descriptive percentile-resampling interval
at a nominal reference level, not a conventional inferential confidence interval and
not evidence of a population parameter. Calibration remains `not_estimated`.

The plotted mediator is the independent `ReferenceGate` interpreter. No production-gate
claim is permitted without explicit parity evidence against `ActuationGate`; the current
status is `not_established`.

## Not exploitable under current scope

The following possible overclaims were checked and remain intentionally unavailable:

- The red-team pass itself made no publication claim; the subsequent release pass
  records the assigned Zenodo concept/version DOIs and the versioned GitHub release
  separately from this review. Publication does not establish scientific validity.
- No external workload, agent population, production deployment, or effectiveness study
  is executed by this pass.
- No invented p-value, empirical probability, calibration estimate, or population
  confidence interval is added.
- The dirty `open_gauss` submodule is not edited, reset, or cleaned.
- Caller-reported ordinary MCP outcomes remain explicitly distinct from locally
  attested lifecycle records and from independent external observation.
- Tagged-PDF metadata, `qpdf --check`, searchable text, and HTML metadata are treated as
  structural/rendering checks; the current content and distribution PDFs additionally
  have independent veraPDF PDF/UA-2 passes, without implying universal usability.
- Negative controls, failed gates, `not_run` hypotheses, `not_estimated` calibration,
  and conditional claim boundaries remain evidence rather than editorial clutter.

## Acceptance evidence to retain

The final handoff must include successful, source-current evidence for:

1. focused research, manuscript-integrity, notation, figure, and release tests;
2. scoped coverage, Ruff, `ty`, and documentation checks;
3. producer-order regeneration of variables, figures, hydrated Markdown, HTML/PDF, and
   bibliography audit;
4. `qpdf --check`, searchable text with no unresolved tokens/diagnostics, HTML image and
   long-description integrity, a loopback-served browser pass, and independent veraPDF
   PDF/UA-2 validation;
5. Poppler renders inspected for every figure-bearing page and representative section
   transitions; and
6. publication bundle preparation/verification plus
   `scripts/validate_manuscript_integrity.py --require-source-current`.

Those receipts are the release gate for the published technical report. They do not
establish external effectiveness, calibration, production safety, or universal
reader usability; those limitations remain active research and accessibility
boundaries.
