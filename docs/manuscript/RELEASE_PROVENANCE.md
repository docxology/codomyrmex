# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Code/enforcement baseline revision: `b533af71c387b306b2c84b07099c49ba402518c5` (`docs: finalize rc2 provenance`)
- Candidate commit: recorded in `output/release_manifest.json` for the immutable tag below
- Release tag: `v1.4.0-rc18` (`v1.4.0` remains held pending external evaluation)
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
candidate is tagged as `v1.4.0-rc18` and the clean-clone release manifest is
reproducible. The provider-backed benchmark is not attached, so `publication_ready`
remains false pending external evaluation evidence and final release publication.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `3e15c79ee15f174bac784a05fa1ebceaed25a8741305f974d51bb3960744503d` |
| `output/paper.html` | `7f42c41a1f42127cf9b06ebc5a53384ecaa5a57fd51a7e2feb84cc0b29999355` |
| `output/data/manuscript_variables.json` | `49ba171b55cd8946d1024dbcbbca12fbe1986e90d3ed152d695c1501f1b44e85` |
| `output/data/colony_kernel_coverage.json` | `e7134083deb0d91cb91bfed463ae7809d3d461d22a067c85ac84fe740d004e57` |
| `output/data/colony_kernel_test_report.xml` | `cbcfc215fee2cf2200ee0c1ae18e2adf5a2ec9d58c360ef8e691b0b5be963e5eb` |
| `output/data/colony_kernel_test_status.json` | `fc2f174b03c69d8d3bf038e6e49c11b1c86d39aa74920aa7c226211e6e4a1ecf` |

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
