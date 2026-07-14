# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Code/enforcement baseline revision: `b533af71c387b306b2c84b07099c49ba402518c5` (`docs: finalize rc2 provenance`)
- Candidate commit: recorded in `output/release_manifest.json` for the immutable tag below
- Release tag: `v1.4.0-rc11` (`v1.4.0` remains held pending external evaluation)
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
candidate is tagged as `v1.4.0-rc11` and the clean-clone release manifest is
reproducible. The provider-backed benchmark is not attached, so `publication_ready`
remains false pending external evaluation evidence and final release publication.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `e98b781bc0e816514435ed87daa27350febbf5e3040073421a3ebfb126ce20e0` |
| `output/paper.html` | `d88b892ed58e0b7d53d776e68b1c722014987cb72cc28695819c266b11555d13` |
| `output/data/manuscript_variables.json` | `eb3117407a1d4bd18350d0f2e4d4adae65334816ece8028b8d75d341dd5cbb80` |
| `output/data/colony_kernel_coverage.json` | `9628a231d58035ae1b19dd8bc9545ec262a043e925969024f0bedd4052b2ce1e` |
| `output/data/colony_kernel_test_report.xml` | `fad2d4b11b0c191edda20e109a0e19fd16eeb638f3ce30922d46f3c79a4b9b09` |
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
