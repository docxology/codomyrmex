# Codomyrmex publication-readiness follow-up

This follow-up preserves the historical second-pass audit of
`e85aee6758726ca1fbba202d0ef1a09d524029e3` and records the implementation and
release checks performed against the reviewed baseline
`4bd6c1804f2caa905d36bcb39d67bdf8c1d86837` and the final candidate revision
identified by the clean-clone manifest for tag `v1.4.0-rc18`.

The result is a dual-profile candidate. The advisory profile preserves
`caller_reported_unattested` input; the strict profile enforces only the governed
action scope through signed, single-use Ed25519 capabilities and executor receipts.
`FAILURE` means a caller-reported or attested adverse outcome; policy rejection is
`POLICY_REJECTION`; prospective falsification findings use `RISK`. The PDF-producing
source and generated outputs are synchronized in this worktree. A clean clone of the
candidate regenerated the exact PDF, HTML, evidence, and figure hashes; the candidate
is tagged as `v1.4.0-rc18` and remains on hold until the provider-backed
benchmark is completed and the final release is published.

## Reproduction snapshot

The fail-closed generator wrote `output/data/colony_kernel_test_status.json` and
`output/data/colony_kernel_coverage.json` from one run:

| Measure | Result |
| --- | ---: |
| Required tests collected | 840 (841 pytest items collected; 1 deselected) |
| Required tests passed | 840 |
| Required skips | 0 |
| Required failures | 0 |
| Required errors | 0 |
| Branch coverage | 74.37185929648241% (592/796) |
| Line coverage | 82.59604190919674% (2,246/2,640) |
| Executable coverage floor | 60.0% |
| Full local colony-kernel suite | 840 selected and passed; 0 skipped, failed, or errored |

Commands and exit codes are captured in `output/release_manifest.json`. The final
render command was:

```text
uv run python scripts/compile_manuscript.py --pdf    # exit 0
```

The scoped generator also reran pytest with branch coverage, Ruff, and ty; all
required commands exited 0. The paired locality contract remains:

The rendered candidate uses a compact print geometry of 0.20 inches on the left and
right and 0.55 inches on the top and bottom; PDF text-bbox inspection measured an
approximately 14.0-point left inset on representative content pages.

| Case | Score | Decision |
| --- | ---: | --- |
| Clear same target | 0.875 | EXECUTE |
| Same target after TEST-source caller-reported FAILURE pressure 3.0 | 0.725 | HOLD |
| Unrelated target after the report | 0.875 | EXECUTE |
| Same target after 20 passive ticks | 0.875 | EXECUTE |

Standalone over-budget evaluation now returns `REFUSE`, score `0.0`, and
`budget_approved=False`; the integrated kernel retains its documented `HOLD`
requeue behavior. SQLite and pure-list trust stores both initialize at `0.10` and
apply the same successful-record delta. Proposal registration is idempotent and
duplicate outcome reports do not increment proposal or accepted counters.

Strict enforcement contracts additionally cover signed capability issuance,
single-use atomic consumption across processes, scope/traversal rejection, expiry,
tampering, cross-agent mismatch, receipt-linked outcomes, quarantine of unattested
reports, durable SQLite signal/budget restart state, supervised read-only evaluation,
and explicit benchmark fail-closed behavior. The pinned SWE-bench Lite manifest names
30 instances at revision `6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2`, split into 20
development and 10 held-out IDs; no provider-backed results are claimed yet.

## Final candidate artifact hashes

These hashes match the post-render provenance companion at
`docs/manuscript/RELEASE_PROVENANCE.md` and the manifest generated from the same
candidate worktree.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `3e15c79ee15f174bac784a05fa1ebceaed25a8741305f974d51bb3960744503d` |
| `output/paper.html` | `7f42c41a1f42127cf9b06ebc5a53384ecaa5a57fd51a7e2feb84cc0b29999355` |
| `output/data/manuscript_variables.json` | `49ba171b55cd8946d1024dbcbbca12fbe1986e90d3ed152d695c1501f1b44e85` |
| `output/data/colony_kernel_coverage.json` | `e7134083deb0d91cb91bfed463ae7809d3d461d22a067c85ac84fe740d004e57` |
| `output/data/colony_kernel_test_report.xml` | `cbcfc215fee2cf2200ee0c1ae18e2adf5a2ec9d58c360ef8e691b0b5be963e5eb` |
| `output/data/colony_kernel_test_status.json` | `fc2f174b03c69d8d3bf038e6e49c11b1c86d39aa74920aa7c226211e6e4a1ecf` |

The clean-clone manifest for `v1.4.0-rc18` reports `publication_ready=false` because provider-backed
benchmark results are missing; its checkout, artifact freshness, and required test
gates are true. The shared development worktree retains unrelated changes outside the
candidate. The
historical reviewed PDF remains preserved in the Downloads package and is not
overwritten by this follow-up.

## Action disposition

The workbook follow-up reclassifies the implemented enforcement, persistence,
semantic, and documentation actions as `Addressed - verify` against this candidate;
A-001 and A-016 remain release blockers until the release candidate is externally
published with its evidence bundle. Provider-backed benchmark execution and external
key/endpoint configuration remain explicitly pending; the release runner now also
requires a trusted executor public-key registry and verifies receipt signatures
cryptographically. No production-safety or
repository-wide governance claim is made.
