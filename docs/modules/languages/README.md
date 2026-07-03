# Languages Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: April 2026

## Overview

`codomyrmex.languages` provides language runtime adapters and shared abstractions for Python, JavaScript, TypeScript, Go, Java, Rust, Ruby, Swift, R, PHP, Elixir, C++, C#, and shell workflows. The package-level source lives in [src/codomyrmex/languages/](../../../src/codomyrmex/languages/).

## Key Surfaces

- `base.py` — common adapter contracts and shared language-runtime utilities.
- Per-language subpackages such as `python/`, `javascript/`, `typescript/`, `go/`, `java/`, and `rust/`.
- `mcp_tools.py` — MCP-facing language tooling surface.
- Source-level docs: [README](../../../src/codomyrmex/languages/README.md), [SPEC](../../../src/codomyrmex/languages/SPEC.md), [PAI](../../../src/codomyrmex/languages/PAI.md), and [AGENTS](../../../src/codomyrmex/languages/AGENTS.md).

## Usage Pattern

Use this module when code generation, static checks, formatting, execution, or tool-routing needs language-specific behavior behind a common Codomyrmex interface. Prefer adding new language support as a subpackage with its own `README.md`, `SPEC.md`, and `AGENTS.md` rather than expanding `base.py` with language-specific branches.

## Navigation

- **Parent**: [../README.md](../README.md)
- **Source**: [../../../src/codomyrmex/languages/](../../../src/codomyrmex/languages/)
- **Spec**: [SPEC.md](SPEC.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
