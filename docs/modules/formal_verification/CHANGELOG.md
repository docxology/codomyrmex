# Formal Verification — Changelog

## [0.1.0] - 2026-02-17

### Added
- Initial module implementation
- Z3 SMT solver backend via z3-solver pip package
- Z3 source as git submodule at vendor/z3/
- ConstraintSolver class with mcp-solver 6-tool interface
- SolverBackend abstract base class for multi-backend support
- 6 MCP tools: clear_model, add_item, delete_item, replace_item, get_model, solve_model
- PAI ISC verification bridge (verify_criteria_consistency)
- Natural language numeric constraint extraction
- ISCVerificationResult dataclass for structured verification output
- CLI commands: solver:status, solver:backends, solver:check
- Full module documentation (README, PAI, AGENTS, SPEC, API, MCP, SECURITY)
- Unit test suite

### References
- Inspired by PAI Discussion #707 (Spirotot)
- mcp-solver architecture: github.com/szeider/mcp-solver
- Z3 Prover: github.com/Z3Prover/z3
