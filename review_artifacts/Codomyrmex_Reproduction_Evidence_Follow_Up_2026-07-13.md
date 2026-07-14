# Codomyrmex publication-readiness follow-up

This follow-up preserves the historical second-pass audit of
`e85aee6758726ca1fbba202d0ef1a09d524029e3` and records the implementation and
release checks performed against the reviewed baseline
`4bd6c1804f2caa905d36bcb39d67bdf8c1d86837` and the final candidate revision
identified by the clean-clone manifest for tag `v1.4.0-rc12`.

The result is a dual-profile candidate. The advisory profile preserves
`caller_reported_unattested` input; the strict profile enforces only the governed
action scope through signed, single-use Ed25519 capabilities and executor receipts.
`FAILURE` means a caller-reported or attested adverse outcome; policy rejection is
`POLICY_REJECTION`; prospective falsification findings use `RISK`. The PDF-producing
source and generated outputs are synchronized in this worktree. A clean clone of the
candidate regenerated the exact PDF, HTML, evidence, and figure hashes; the candidate
is tagged as `v1.4.0-rc12` and remains on hold until the provider-backed
benchmark is completed and the final release is published.

## Reproduction snapshot

The fail-closed generator wrote `output/data/colony_kernel_test_status.json` and
`output/data/colony_kernel_coverage.json` from one run:

| Measure | Result |
| --- | ---: |
| Required tests collected | 833 (834 pytest items collected; 1 deselected) |
| Required tests passed | 833 |
| Required skips | 0 |
| Required failures | 0 |
| Required errors | 0 |
| Branch coverage | 74.37185929648241% (592/796) |
| Line coverage | 82.59604190919674% (2,246/2,640) |
| Executable coverage floor | 60.0% |
| Full local colony-kernel suite | 833 selected and passed; 0 skipped, failed, or errored |

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
| `output/paper.pdf` | `9a463ff0f52a254115920206a677104423658f3fcb359f6b00e620c70aae9a75` |
| `output/paper.html` | `ec6dcff2a8b4035c63530479b0af279dcd5e5bb79acc22a65df68d50dd4386e2` |
| `output/data/manuscript_variables.json` | `ab097f586bc3039830962988eb9df8ecf64c40d1dcdca0112958e53c9d7e13db` |
| `output/data/colony_kernel_coverage.json` | `abd7dae63df1a6be3e0e4bd3d5c1423d598ac39ea71853bfa6abad69abf23f6b` |
| `output/data/colony_kernel_test_report.xml` | `6c442af40d8005c6bad25b690107a9548252bf96dca621c75b5075a362c9a778` |
| `output/data/colony_kernel_test_status.json` | `859a674b509ae72973ac10b78b5a9c7ef6a6118e4128c16695495781f9910b25` |

The clean-clone manifest for `v1.4.0-rc12` reports `publication_ready=false` because provider-backed
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
key/endpoint configuration remain explicitly pending. No production-safety or
repository-wide governance claim is made.
