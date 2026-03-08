---
task: agents/openfang — Full Submodule Integration
slug: agents-openfang-integration
effort: Advanced
phase: execute
progress: 0/12
mode: ALGORITHM
started: 2026-03-07T16:00:00
updated: 2026-03-07T16:00:00
---

## Context
Implement openfang Agent OS integration following the aider/soul subprocess+submodule pattern.
28 new files: 7 source + 6 RASP docs + 6 test files + 3 config changes.

## Criteria
- [ ] ISC-1: Core module files created (exceptions, config, core, hands, update, __init__, py.typed)
- [ ] ISC-2: mcp_tools.py with 7 @mcp_tool functions
- [ ] ISC-3: Test files created (6 files, ~145 tests total)
- [ ] ISC-4: RASP documentation (README, AGENTS, SPEC, PAI, MCP_TOOL_SPECIFICATION, API_SPECIFICATION)
- [ ] ISC-5: .gitmodules entry added
- [ ] ISC-6: pyproject.toml optional dep + pytest marker added
- [ ] ISC-7: agents/__init__.py lazy import added
- [ ] ISC-8: Module imports cleanly (no errors)
- [ ] ISC-9: Tests pass (skipif guards for binary-dependent)
- [ ] ISC-10: Ruff zero violations
- [ ] ISC-11: @mcp_tool auto-discovery works
- [ ] ISC-12: vendor/ directory exists for submodule

## Verification
```bash
uv run python -c "from codomyrmex.agents.openfang import HAS_OPENFANG; print('OK', HAS_OPENFANG)"
uv run pytest src/codomyrmex/tests/unit/agents/openfang/ -v --tb=short
uv run ruff check src/codomyrmex/agents/openfang/
```
