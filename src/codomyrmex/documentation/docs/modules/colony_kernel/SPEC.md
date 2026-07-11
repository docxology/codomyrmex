# colony_kernel - Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Provide documentation mirror coverage for the colony kernel module and keep the
generated documentation tree link-complete.

## Functional Requirements

1. Preserve generated documentation navigation for the colony kernel.
2. Link to module overview and agent guidance.
3. Keep mirror docs aligned with source-level kernel contracts.
4. Record the kernel as an explicit module in source-structure audits.
5. Keep trust, status, proposal, and outcome-recording concepts visible in the
   documentation tree.
6. Avoid claiming networked or external kernel behavior from this mirror page;
   runtime guarantees belong in the source module and tests.

## Design Principles

- **Kernel centrality**: documentation should make the colony kernel visible as
  an orchestration and trust surface.
- **Gate compatibility**: source-structure and docs checks must agree that the
  module has complete documentation coverage.
- **Implementation humility**: generated mirror docs summarize contracts without
  replacing source-level API specifications or tests.

## Interface Expectations

The documentation mirror represents the public documentation footprint for the
kernel. Runtime callers should use the source module and its API docs for exact
behavior, while release and quality tooling can use this page as evidence that
the module is represented in generated documentation.

## Validation

```bash
make docs-check
uv run pytest src/codomyrmex/tests/unit/system_discovery/test_structure_audit.py -q
```

## Navigation

- **Module Overview**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
