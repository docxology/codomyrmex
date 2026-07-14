# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Evaluated current revision: `4bd6c1804f2caa905d36bcb39d67bdf8c1d86837`
- Release tag: pending a clean immutable release
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the same post-render manifest run as the PDF and
evidence bundle. The worktree remains dirty because this implementation revision is
not yet committed or tagged; `publication_ready` therefore remains false until a
clean immutable release is created and the provider-backed benchmark is attached.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `b560d7bfbe8ce5785536fef8f7c6d31d89658b887752883e6798531e292067be` |
| `output/paper.html` | `2dd8c4768682ef9339d63309e8ed3de0c70c6961c6f433743af895dc64d66a5e` |
| `output/data/manuscript_variables.json` | `c81fc49cb865e698e3bbef2f0816b8d6b4946a8d06ebd84511b69fb660ee3689` |
| `output/data/colony_kernel_coverage.json` | `eddb1a9090c16ac2e5a8e5830c73994482d24713d049753187e6b480f74d4489` |
| `output/data/colony_kernel_test_report.xml` | `ad6f6a0ab82dc5df20fae378d420f8b210b24e086543e8f8721c6687effdc08f` |
| `output/data/colony_kernel_test_status.json` | `a6ce71a6cd0cc7fda17191ab6c06ab1159e5bd2ca0b046c38849335b6a42cec3` |

The corresponding benchmark-manifest hash is
`03b791c91c89e4de4d4844c7376142a8ad1ca2ab22ec5a8811f4f963d3b931d6`.

The release manifest records `publication_ready: false` for this dirty, untagged
candidate because provider-backed benchmark results and immutable clean-clone
verification are still required.

The rendered candidate uses 0.20-inch left/right and 0.55-inch top/bottom margins in
both the PDF layout and the HTML print stylesheet.
