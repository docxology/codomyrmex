# Codomyrmex publication-readiness follow-up

This follow-up preserves the historical second-pass audit of
`e85aee6758726ca1fbba202d0ef1a09d524029e3` and records the implementation and
release checks performed against the reviewed baseline
`4bd6c1804f2caa905d36bcb39d67bdf8c1d86837` and implementation candidate
`1db2b7a326b468a6c33ce9af7adb8e2ddd5d8025`.

The result is a dual-profile candidate. The advisory profile preserves
`caller_reported_unattested` input; the strict profile enforces only the governed
action scope through signed, single-use Ed25519 capabilities and executor receipts.
`FAILURE` means a caller-reported or attested adverse outcome; policy rejection is
`POLICY_REJECTION`; prospective falsification findings use `RISK`. The PDF-producing
source and generated outputs are synchronized in this worktree. A clean clone of the
implementation candidate regenerated the exact PDF, HTML, and figure hashes; publication
remains on hold until the candidate is published under an immutable tag and benchmarked.

## Reproduction snapshot

The fail-closed generator wrote `output/data/colony_kernel_test_status.json` and
`output/data/colony_kernel_coverage.json` from one run:

| Measure | Result |
| --- | ---: |
| Required tests collected | 815 |
| Required tests passed | 815 |
| Required skips | 0 |
| Required failures | 0 |
| Required errors | 0 |
| Branch coverage | 74.29667519181585% (581/782) |
| Line coverage | 82.57419923596827% (2,229/2,621) |
| Executable coverage floor | 60.0% |
| Full local colony-kernel suite | 816 passed |

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
| `output/paper.pdf` | `36ebc8982f92d5bd007b92f9415d029dfc26ee4c5aa185c0345fc8b48b1f0f76` |
| `output/paper.html` | `6d999977449e85e979992f07c16472bdea07e5ab8e8018ce34a421e0938120df` |
| `output/data/manuscript_variables.json` | `6b424188e10d340dce60cb520809ab30ab3014fb9681b7935befa63271b86c98` |
| `output/data/colony_kernel_coverage.json` | `117dcb7145d1455a2f0125e954c92ff016012622e7e1f6a951b26996541cceb2` |
| `output/data/colony_kernel_test_report.xml` | `0dad5f0f470c4bf770bf7bb3f15169099113e4e28a8f6af203caf232c7102355` |
| `output/data/colony_kernel_test_status.json` | `abe20b74d40742d444770bc68e96979f916c8766971eaca62759d01ee12657af` |

The manifest reports `publication_ready=false` because the worktree contains unrelated
changes and provider-backed benchmark results are missing; its required artifact
freshness and required test gates are true. The
historical reviewed PDF remains preserved in the Downloads package and is not
overwritten by this follow-up.

## Action disposition

The workbook follow-up reclassifies the implemented enforcement, persistence,
semantic, and documentation actions as `Addressed - verify` against this candidate;
A-001 and A-016 remain release blockers until an immutable release is published.
Provider-backed benchmark execution, clean-clone replay, and external key/endpoint
configuration remain explicitly pending. No production-safety or repository-wide
governance claim is made.
