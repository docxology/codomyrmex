# Codomyrmex Glossary

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

Terminology reference for the Codomyrmex platform and PAI integration system.

## Terms

### Algorithm (The Algorithm)

PAI's 7-phase execution pipeline that runs on every Claude Code prompt:
**OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN**.
Defined in `~/.claude/PAI/Algorithm/v3.5.0.md`. Each phase maps to specific Codomyrmex modules.

### @mcp_tool decorator

Python decorator from `src/codomyrmex/model_context_protocol/decorators.py` that marks a function for automatic discovery as an MCP tool. Any function with this decorator in any `mcp_tools.py` submodule is surfaced to PAI automatically (5-minute TTL cache).

### Dynamic Tools (Auto-Discovered Tools)

MCP tools discovered at runtime via `@mcp_tool` decorators across 74 auto-discovered module `mcp_tools.py` files. Currently ~347 dynamic tools. Run `/codomyrmexVerify` for the current exact count.

### Foundation / Core / Service / Application Layers

The four dependency tiers of Codomyrmex's architecture. Dependencies flow upward only — Foundation has no dependencies on higher layers.

- **Foundation**: logging_monitoring, environment_setup, model_context_protocol, terminal_interface
- **Core**: agents, coding, git_operations, llm, static_analysis
- **Service**: orchestrator, documentation, containerization, ci_cd_automation
- **Application**: cli, system_discovery

### Hard-Right Execution Standard

The governing principle for all agent decisions: bias toward correct, auditable, reversible solutions over convenient shortcuts. Prefer real measurements over estimates; favour documented changes over quick hacks; never trade correctness for short-term convenience.

### ISC (Ideal State Criteria)

Atomic, binary-testable success criteria used in Algorithm PRDs. Each criterion covers exactly one independently verifiable end-state, ≤12 words. If a criterion contains "and" joining two verifiable things, it must be split into two criteria.

### MCP (Model Context Protocol)

The protocol used to expose Codomyrmex tools to PAI/Claude. Standardized interface defined in `src/codomyrmex/model_context_protocol/`. Tools are JSON-schema-typed functions called over stdio or HTTP.

### PAIBridge

The Python class (`src/codomyrmex/agents/pai/pai_bridge.py`) that discovers and validates the PAI installation, enumerating skills, hooks, agents, memory stores, and Algorithm version.

### RASP

The four-document pattern every Codomyrmex module follows:

- **R**EADME.md — Human overview, key exports, quick start
- **A**GENTS.md — AI agent coordination rules and operating contracts
- **S**PEC.md — Functional specification and design rationale
- **P**AI.md — Algorithm phase → tool mapping for this module

### Sprint

A focused development cycle in the project's history, referenced in MEMORY.md and commit history (e.g., "Sprint 8 — Zero-Policy Compliance", "Sprint 16 — Ruff Zero"). Not calendar-fixed; each Sprint targets a specific quality or capability theme.

### Static Tools

The 20 MCP tools always available from the Codomyrmex bridge (17 core + 3 universal proxy), defined in `src/codomyrmex/agents/pai/mcp/definitions.py`. These do not require `@mcp_tool` decoration — they are registered statically.

### TELOS

PAI's north-star objective system stored in `~/.claude/USER/TELOS.md`. Guides Algorithm prioritization and long-term decision-making across sessions.

### Trust Gateway

The three-tier security model gating Codomyrmex MCP tools (`src/codomyrmex/agents/pai/trust_gateway.py`):

- **UNTRUSTED**: No tools executable
- **VERIFIED**: Safe static tools + all dynamic safe tools (via `/codomyrmexVerify`)
- **TRUSTED**: All 5 destructive tools enabled (via `/codomyrmexTrust`): `write_file`, `run_command`, `run_tests`, `call_module_function`, `execute_workflow`

### Zero-Mock Policy

Codomyrmex's absolute testing rule: no `unittest.mock`, `MagicMock`, `monkeypatch`, or `pytest-mock` in production tests. External dependencies use `@pytest.mark.skipif` guards. Unimplemented features raise `NotImplementedError`. See [testing-strategy.md](../development/testing-strategy.md).

## Navigation

- **Parent**: [Reference](README.md)
- **Root**: [docs/](../README.md)
- **Testing Strategy**: [../development/testing-strategy.md](../development/testing-strategy.md)
- **PAI Integration**: [../pai/README.md](../pai/README.md)
- **Architecture**: [../ARCHITECTURE.md](../ARCHITECTURE.md)
