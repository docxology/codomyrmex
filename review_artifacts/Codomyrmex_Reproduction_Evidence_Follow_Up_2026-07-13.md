# Codomyrmex publication-readiness follow-up

This follow-up preserves the historical second-pass audit of
`e85aee6758726ca1fbba202d0ef1a09d524029e3` and records the implementation and
release checks performed against the reviewed baseline
`4bd6c1804f2caa905d36bcb39d67bdf8c1d86837` and implementation candidate
`fc318a55be5cb46ff7850cec3bc547401b407701`.

The result is a dual-profile candidate. The advisory profile preserves
`caller_reported_unattested` input; the strict profile enforces only the governed
action scope through signed, single-use Ed25519 capabilities and executor receipts.
`FAILURE` means a caller-reported or attested adverse outcome; policy rejection is
`POLICY_REJECTION`; prospective falsification findings use `RISK`. The PDF-producing
source and generated outputs are synchronized in this worktree. A clean clone of the
implementation candidate regenerated the exact PDF, HTML, evidence, and figure hashes;
the candidate is tagged as `v1.4.0-rc1` and remains on hold until the provider-backed
benchmark is completed and the final release is published.

## Reproduction snapshot

The fail-closed generator wrote `output/data/colony_kernel_test_status.json` and
`output/data/colony_kernel_coverage.json` from one run:

| Measure | Result |
| --- | ---: |
| Required tests collected | 822 |
| Required tests passed | 822 |
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
| `output/paper.pdf` | `37bc6ba55b8208a8a455c8e82371b848a5378c82b5a6d0f72ce43a1ee58894bd` |
| `output/paper.html` | `f930564711c845f6e6abc494ed81a463202efce466929ea23a83d85110151df3` |
| `output/data/manuscript_variables.json` | `2445b34cdaa162b0ee27ae050316b42e7ba09e2a5ecf4b09623f443f3a28e52d` |
| `output/data/colony_kernel_coverage.json` | `e5f1b3ac69ebeda28cded7cd28ed5a9c2e03c7a772222857a08143a7dc37b2b6` |
| `output/data/colony_kernel_test_report.xml` | `59498b92044f4082c05d1a60fdb482ea9efe4fb761e79db0d4a7077f5fb7694f` |
| `output/data/colony_kernel_test_status.json` | `ad5ee65f8e1933d05928cf59a555c56f48cb0a47510972b8d0006ecd09bc9d19` |

The clean-clone manifest reports `publication_ready=false` because provider-backed
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
