# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Evaluated implementation revision: `f22384acf925cebdd819915d17d530592d9ffba3`
- Release tag: `v1.4.0-rc1` (candidate; `v1.4.0` remains held pending external evaluation)
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
candidate is tagged as `v1.4.0-rc1` and the clean-clone release manifest is
reproducible. The provider-backed benchmark is not attached, so `publication_ready`
remains false pending external evaluation evidence and final release publication.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `4de816030843c5d43255dfb6a8d0a8056091689ad6d667d08d6569a5529f92c2` |
| `output/paper.html` | `7b1f10d08475204af555e798de31c13158c9a7112586717c7aba906230cd1200` |
| `output/data/manuscript_variables.json` | `3fc5e6ef13443a1a214722f24332b8db0fcd3fbce3c3bcda69af7dbb43e080de` |
| `output/data/colony_kernel_coverage.json` | `e5f1b3ac69ebeda28cded7cd28ed5a9c2e03c7a772222857a08143a7dc37b2b6` |
| `output/data/colony_kernel_test_report.xml` | `832bc840a1c36264c34e7169e9b7e3bff58b41b6c58ff6e09aff4dcce31dceba` |
| `output/data/colony_kernel_test_status.json` | `88e9076c9961a314a2394dff21917b9ccbd490c9bcbabca7ea4c41b4d4efdf35` |

The corresponding benchmark-manifest hash is
`03b791c91c89e4de4d4844c7376142a8ad1ca2ab22ec5a8811f4f963d3b931d6`.

The deterministic clean-clone replay at the implementation revision regenerated the
same PDF, HTML, evidence, and figure hashes. The release manifest remains
`publication_ready: false` because provider-backed benchmark results are missing.
The shared development checkout retains unrelated changes outside the candidate; the
tagged clean-clone evaluation is clean.

The rendered candidate uses 0.20-inch left/right and 0.55-inch top/bottom margins in
both the PDF layout and the HTML print stylesheet.
