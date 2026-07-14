# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Code/enforcement baseline revision: `b533af71c387b306b2c84b07099c49ba402518c5` (`docs: finalize rc2 provenance`)
- Candidate commit: recorded in `output/release_manifest.json` for the immutable tag below
- Release tag: `v1.4.0-rc9` (`v1.4.0` remains held pending external evaluation)
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
candidate is tagged as `v1.4.0-rc9` and the clean-clone release manifest is
reproducible. The provider-backed benchmark is not attached, so `publication_ready`
remains false pending external evaluation evidence and final release publication.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `69fdbb018d81b7b5dd0ae170187842ef30647b8f6864af91f615fa23ea6ac706` |
| `output/paper.html` | `cb0f7bd1546dc8acca60dccc355e4093ad1a2bd7e9f878dad7a9413e2b0641f5` |
| `output/data/manuscript_variables.json` | `865ba48c143b1b5fbfb98a79cf94638b9c38b673d0ec208acc68a95857d64410` |
| `output/data/colony_kernel_coverage.json` | `7dc284a8b6d29c163eb2185e1372795dfb3da8eb22977c66a289286249239ccf` |
| `output/data/colony_kernel_test_report.xml` | `677e30d935cc5e09849d92e9d6ea3c014d8d8ee076aaa5dd8573d9cc7002a1ce` |
| `output/data/colony_kernel_test_status.json` | `53be36e539e2e45ea55b78758280cb9e5a1e81f30968619a326618123b070dbf` |

The corresponding benchmark-manifest hash is
`03b791c91c89e4de4d4844c7376142a8ad1ca2ab22ec5a8811f4f963d3b931d6`.

The deterministic clean-clone replay at the implementation revision regenerated the
same PDF, HTML, evidence, and figure hashes. The release manifest remains
`publication_ready: false` because provider-backed benchmark results are missing.
The shared development checkout retains unrelated changes outside the candidate; the
tagged clean-clone evaluation is clean. The local manifest sidecar records the
candidate's dirty state explicitly; the clean-clone manifest records the same
revision and tag with no status output.

The rendered candidate uses 0.20-inch left/right and 0.55-inch top/bottom margins in
both the PDF layout and the HTML print stylesheet.
