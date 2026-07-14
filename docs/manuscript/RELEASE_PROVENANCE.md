# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Evaluated implementation revision: `fc318a55be5cb46ff7850cec3bc547401b407701`
- Release tag: `v1.4.0-rc1` (candidate; `v1.4.0` remains held pending external evaluation)
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
candidate is tagged as `v1.4.0-rc1` and the clean-clone release manifest is
reproducible. The provider-backed benchmark is not attached, so `publication_ready`
remains false pending external evaluation evidence and final release publication.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `37bc6ba55b8208a8a455c8e82371b848a5378c82b5a6d0f72ce43a1ee58894bd` |
| `output/paper.html` | `f930564711c845f6e6abc494ed81a463202efce466929ea23a83d85110151df3` |
| `output/data/manuscript_variables.json` | `2445b34cdaa162b0ee27ae050316b42e7ba09e2a5ecf4b09623f443f3a28e52d` |
| `output/data/colony_kernel_coverage.json` | `e5f1b3ac69ebeda28cded7cd28ed5a9c2e03c7a772222857a08143a7dc37b2b6` |
| `output/data/colony_kernel_test_report.xml` | `59498b92044f4082c05d1a60fdb482ea9efe4fb761e79db0d4a7077f5fb7694f` |
| `output/data/colony_kernel_test_status.json` | `ad5ee65f8e1933d05928cf59a555c56f48cb0a47510972b8d0006ecd09bc9d19` |

The corresponding benchmark-manifest hash is
`03b791c91c89e4de4d4844c7376142a8ad1ca2ab22ec5a8811f4f963d3b931d6`.

The deterministic clean-clone replay at the implementation revision regenerated the
same PDF, HTML, evidence, and figure hashes. The release manifest remains
`publication_ready: false` because provider-backed benchmark results are missing.
The shared development checkout retains unrelated changes outside the candidate; the
tagged clean-clone evaluation is clean.

The rendered candidate uses 0.20-inch left/right and 0.55-inch top/bottom margins in
both the PDF layout and the HTML print stylesheet.
