# Manuscript release provenance

This companion file is part of the manuscript source package but is deliberately
not rendered into `output/paper.pdf`: embedding a PDF's own SHA-256 would make the
identity self-referential. The machine-readable source of truth is
`output/release_manifest.json`; this file is finalized after the PDF render.

## Candidate identity

- Historical audit anchor: `e85aee6758726ca1fbba202d0ef1a09d524029e3`
- Implementation baseline revision: `4bd6c1804f2caa905d36bcb39d67bdf8c1d86837`
- Candidate commit: recorded in `output/release_manifest.json` for the immutable tag below
- Candidate hardening commit: `0f20fc108c98388d9c7b3fa6aa777fed4376f371`
- Release tag: `v1.4.0-rc20` (`v1.4.0` remains held pending external evaluation)
- Scope: dual-profile Colony Kernel candidate; strict enforcement applies only to the declared action scope, while advisory compatibility remains available

## Artifact hashes

These values were captured from the deterministic post-render candidate build. The
candidate is tagged as `v1.4.0-rc20` and the clean-clone release manifest is
reproducible. The provider-backed benchmark is not attached, so `publication_ready`
remains false pending external evaluation evidence and final release publication.

| Artifact | SHA-256 |
| --- | --- |
| `output/paper.pdf` | `8dc89701bcfb5b4ece4475b4015071470bfc74034f8d85aecd5aa716ea8e4857` |
| `output/paper.html` | `99846d4132f1a42e59b422f46bc80960cf123ef6f2a527d27a841c7937f55092` |
| `output/data/manuscript_variables.json` | `b70e43d0785976eeea88c51f2f71a22d13d4e78ac019e19c4c93ce912ba22d63` |
| `output/data/colony_kernel_coverage.json` | `e7134083deb0d91cb91bfed463ae7809d3d461d22a067c85ac84fe740d004e57` |
| `output/data/colony_kernel_test_report.xml` | `50f2c14555ec754fdf085fcc7377ad3fa230a8dc93c78ff080b59836801a1d1d` |
| `output/data/colony_kernel_test_status.json` | `ce9a8aa6c490a73dc58e53184b6ef19a47cd5be722afc8dd69bd62a5573ed376` |

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
