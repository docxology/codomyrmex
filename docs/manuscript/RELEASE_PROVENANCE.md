# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Evaluated implementation revision: `1db2b7a326b468a6c33ce9af7adb8e2ddd5d8025`
- Release tag: pending a clean immutable release
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
local worktree still contains unrelated changes and the provider-backed benchmark is
not attached; `publication_ready` therefore remains false until the immutable release
tag and external evaluation evidence exist.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `36ebc8982f92d5bd007b92f9415d029dfc26ee4c5aa185c0345fc8b48b1f0f76` |
| `output/paper.html` | `6d999977449e85e979992f07c16472bdea07e5ab8e8018ce34a421e0938120df` |
| `output/data/manuscript_variables.json` | `6b424188e10d340dce60cb520809ab30ab3014fb9681b7935befa63271b86c98` |
| `output/data/colony_kernel_coverage.json` | `117dcb7145d1455a2f0125e954c92ff016012622e7e1f6a951b26996541cceb2` |
| `output/data/colony_kernel_test_report.xml` | `0dad5f0f470c4bf770bf7bb3f15169099113e4e28a8f6af203caf232c7102355` |
| `output/data/colony_kernel_test_status.json` | `abe20b74d40742d444770bc68e96979f916c8766971eaca62759d01ee12657af` |

The corresponding benchmark-manifest hash is
`03b791c91c89e4de4d4844c7376142a8ad1ca2ab22ec5a8811f4f963d3b931d6`.

The deterministic clean-clone replay at the implementation revision regenerated the
same PDF, HTML, and figure hashes. The release manifest remains
`publication_ready: false` because the local checkout is not an immutable tag and
provider-backed benchmark results are missing.

The rendered candidate uses 0.20-inch left/right and 0.55-inch top/bottom margins in
both the PDF layout and the HTML print stylesheet.
