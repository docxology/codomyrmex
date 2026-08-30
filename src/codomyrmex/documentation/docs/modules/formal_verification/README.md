<!-- readme: generated -->

# formal_verification

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/formal_verification/`

## Overview

Codomyrmex Formal Verification Module — constraint solving via Z3/SMT.

Integrates constraint solving capabilities into the Codomyrmex platform,
inspired by szeider/mcp-solver and proposed in PAI Discussion #707 by Spirotot.

Provides:
    - Z3 SMT solver backend with a mcp-solver-compatible 9-tool interface
    - PAI Algorithm ISC criteria consistency verification
    - MCP tools for Claude Code integration
    - Extensible backend architecture for SAT/MaxSAT/ASP solvers

## Submodules

| Submodule | Description |
|-----------|-------------|
| `backends` | — Pluggable solver backend implementations (Z3 primary) |
| `solver` | — High-level ConstraintSolver API |
| `mcp_tools` | — MCP tool definitions for agent integration |
| `verify_isc` | — PAI Algorithm ISC constraint verification bridge |

## Public Exports

`formal_verification` exports 24 public symbols via `__all__`:

`BackendNotAvailableError`, `ChangeProposal`, `CodeChangeVerifier`, `ConstraintSolver`, `GateDecision`, `GatedRewriter`, `ISCVerificationResult`, `InvalidConstraintError`, `ModelBuildError`, `RewriteGate`, `RewriteProposal`, `RuleResult`, `SolverBackend`, `SolverError`, `SolverResult`, `SolverStatus`, `SolverTimeoutError`, `UnsatisfiableError`, `VerificationResult`, `Z3Verifier`, `__version__`, `pop`, `push`, `verify_criteria_consistency`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../formal_verification/](../../../../formal_verification/)
