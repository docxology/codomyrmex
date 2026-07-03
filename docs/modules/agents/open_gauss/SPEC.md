# open_gauss — Documentation Mirror Specification

**Version**: v1.3.0 | **Status**: Mirror Stub | **Last Updated**: July 2026

## Navigation

- **README**: [README.md](README.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **Source Submodule Root**: [../../../../src/codomyrmex/agents/open_gauss/](../../../../src/codomyrmex/agents/open_gauss/)

## Purpose

This directory is a documentation mirror for the `codomyrmex.agents.open_gauss`
submodule boundary. The source package is a nested git checkout under
`src/codomyrmex/agents/open_gauss/`; this mirror must not claim source files
inside that checkout unless they are present in the current working tree.

## Contract

- Keep mirror links pointed either at files in this docs directory or at the
  source submodule root directory.
- Do not add links to source `README.md`, `AGENTS.md`, or `SPEC.md` unless those
  files exist in the nested checkout.
- Treat implementation counts in this mirror as descriptive of the embedded
  upstream agent, not as Codomyrmex package-wide manuscript metrics.
