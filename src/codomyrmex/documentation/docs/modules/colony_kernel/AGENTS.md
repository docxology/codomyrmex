# Codomyrmex Agents - documentation mirror: colony_kernel

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

This directory mirrors the documentation for `src/codomyrmex/colony_kernel/`.
The source module is the canonical contract for the colony control plane:
proposal falsification, resource-budget checks, trust adaptation, actuation
gating, consequence memory, pheromone deposits, and pruning reports.

## Operating Contracts

- Keep this mirror synchronized with the source module's `AGENTS.md`,
  `README.md`, `SPEC.md`, `API_SPECIFICATION.md`, and
  `MCP_TOOL_SPECIFICATION.md`.
- Preserve the documented eight-tool MCP surface:
  `colony_propose_action`, `colony_record_outcome`, `colony_agent_profile`,
  `colony_status`, `colony_pheromone_query`, `colony_falsify_plan`,
  `colony_pruning_report`, and `colony_tick`.
- Keep examples zero-mock and backed by real `ColonyKernel` instances.
- Update docs and tests together when changing gate decisions, trust deltas,
  resource budgets, or pheromone key semantics.

## Key Files

- `AGENTS.md` - Agent coordination and documentation mirror contract.
- `readme.md` - Generated colony-kernel overview for the docs site.
- `api_specification.md` - Lower-case mirror of the source API specification.
- `mcp_tool_specification.md` - Lower-case mirror of the source MCP contract.

## Validation

After changing this documentation mirror, run:

```bash
make docs-check
uv run pytest src/codomyrmex/tests/unit/colony_kernel/ -q
uv run codomyrmex doctor --all
```

## Navigation

- **Module Overview**: [readme.md](readme.md)
- **API Specification**: [api_specification.md](api_specification.md)
- **MCP Tools**: [mcp_tool_specification.md](mcp_tool_specification.md)
- **Source Module**: [../../../../colony_kernel/README.md](../../../../colony_kernel/README.md)
