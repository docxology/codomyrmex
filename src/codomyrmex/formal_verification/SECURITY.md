# Formal Verification — Security Considerations

## Code Execution

The Z3 backend uses `exec()` to evaluate constraint model items. This is by design — mcp-solver's architecture requires executing user-provided Z3 Python code.

### Mitigations

- Items execute in a restricted namespace containing only Z3 imports
- No file system access, network access, or OS operations in the namespace
- Solver timeout prevents resource exhaustion (default 30s)
- The module is intended for use by trusted AI agents within the PAI system, not as a public API

### Recommendations

- Do not expose MCP tools to untrusted external inputs without additional sandboxing
- Use the `coding.sandbox` module for full isolation if running untrusted constraints
- Review constraint strings before execution in security-sensitive contexts

## Dependencies

- `z3-solver`: Pre-built wheels from PyPI (Microsoft Research, MIT licensed)
- Z3 git submodule: Reference only, not used at runtime by default
