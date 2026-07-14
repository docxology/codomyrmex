# Codomyrmex publication-readiness follow-up

This follow-up preserves the historical second-pass audit of
`e85aee6758726ca1fbba202d0ef1a09d524029e3` and records the implementation and
release checks performed against the current revision named by the review:
`4bd6c1804f2caa905d36bcb39d67bdf8c1d86837`.

The result is a dual-profile candidate. The advisory profile preserves
`caller_reported_unattested` input; the strict profile enforces only the governed
action scope through signed, single-use Ed25519 capabilities and executor receipts.
`FAILURE` means a caller-reported or attested adverse outcome; policy rejection is
`POLICY_REJECTION`; prospective falsification findings use `RISK`. The PDF-producing
source and generated outputs are synchronized in this worktree, but publication
remains on hold until the changes are committed, tagged, benchmarked, and replayed
from a clean clone.

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
| Branch coverage | 74.10714285714286% (581/784) |
| Line coverage | 82.44274809160305% (2,227/2,622) |
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
| `output/paper.pdf` | `b560d7bfbe8ce5785536fef8f7c6d31d89658b887752883e6798531e292067be` |
| `output/paper.html` | `2dd8c4768682ef9339d63309e8ed3de0c70c6961c6f433743af895dc64d66a5e` |
| `output/data/manuscript_variables.json` | `c81fc49cb865e698e3bbef2f0816b8d6b4946a8d06ebd84511b69fb660ee3689` |
| `output/data/colony_kernel_coverage.json` | `eddb1a9090c16ac2e5a8e5830c73994482d24713d049753187e6b480f74d4489` |
| `output/data/colony_kernel_test_report.xml` | `ad6f6a0ab82dc5df20fae378d420f8b210b24e086543e8f8721c6687effdc08f` |
| `output/data/colony_kernel_test_status.json` | `a6ce71a6cd0cc7fda17191ab6c06ab1159e5bd2ca0b046c38849335b6a42cec3` |
| `output/release_manifest.json` | `aa336607eb304523b279a367eedf671218fe15fe017a444ca27e6357ff50b7e2` |
| `output/release_package.tar.gz` | `a418096f6868cc33a4d0b3a26c322c1b9e8e82461987cd74d901e25224a505ab` |

The manifest reports `publication_ready=false` because the worktree is dirty and
provider-backed benchmark results are missing; its required artifact freshness and
required test gates are true. The
historical reviewed PDF remains preserved in the Downloads package and is not
overwritten by this follow-up.

## Action disposition

The workbook follow-up reclassifies the implemented enforcement, persistence,
semantic, and documentation actions as `Addressed - verify` against this candidate;
A-001 and A-016 remain release blockers until an immutable release is published.
Provider-backed benchmark execution, clean-clone replay, and external key/endpoint
configuration remain explicitly pending. No production-safety or repository-wide
governance claim is made.
