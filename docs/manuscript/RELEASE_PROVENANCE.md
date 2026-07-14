# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Code/enforcement baseline revision: `b533af71c387b306b2c84b07099c49ba402518c5` (`docs: finalize rc2 provenance`)
- Candidate commit: recorded in `output/release_manifest.json` for the immutable tag below
- Release tag: `v1.4.0-rc12` (`v1.4.0` remains held pending external evaluation)
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
candidate is tagged as `v1.4.0-rc12` and the clean-clone release manifest is
reproducible. The provider-backed benchmark is not attached, so `publication_ready`
remains false pending external evaluation evidence and final release publication.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `9a463ff0f52a254115920206a677104423658f3fcb359f6b00e620c70aae9a75` |
| `output/paper.html` | `ec6dcff2a8b4035c63530479b0af279dcd5e5bb79acc22a65df68d50dd4386e2` |
| `output/data/manuscript_variables.json` | `ab097f586bc3039830962988eb9df8ecf64c40d1dcdca0112958e53c9d7e13db` |
| `output/data/colony_kernel_coverage.json` | `abd7dae63df1a6be3e0e4bd3d5c1423d598ac39ea71853bfa6abad69abf23f6b` |
| `output/data/colony_kernel_test_report.xml` | `6c442af40d8005c6bad25b690107a9548252bf96dca621c75b5075a362c9a778` |
| `output/data/colony_kernel_test_status.json` | `859a674b509ae72973ac10b78b5a9c7ef6a6118e4128c16695495781f9910b25` |

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
