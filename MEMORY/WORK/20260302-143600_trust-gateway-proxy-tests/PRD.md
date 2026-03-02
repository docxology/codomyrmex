---
task: Write trust gateway and MCP proxy tests
slug: 20260302-143600_trust-gateway-proxy-tests
effort: Advanced
phase: complete
progress: 24/24
mode: ALGORITHM
started: 2026-03-02T14:36:00Z
updated: 2026-03-02T14:52:00Z
---

## Context

Write new zero-mock tests for trust_gateway.py and mcp/proxy_tools.py.
A bug fix was just applied to get_current_trust_level() making it derive from
registry aggregate rather than stale _trust_level global. Tests must validate
this new behavior.

### Plan
1. Add TestTrustToolSingleToolFix class to existing test_trust_gateway_hardening.py
2. Create new test_mcp_proxy_tools.py in tests/unit/agents/pai/

## Criteria

- [x] ISC-1: TestTrustToolSingleToolFix class added to hardening file
- [x] ISC-2: test_trust_tool_updates_get_current_trust_level passes with real registry
- [x] ISC-3: test_trust_tool_updates assertion uses TrustLevel.TRUSTED not string
- [x] ISC-4: test_trust_tool_returns_tool_info verifies keys tool/new_level/report
- [x] ISC-5: test_trust_tool_unknown_tool_raises asserts KeyError on nonexistent_tool
- [x] ISC-6: test_verify_capabilities_returns_correct_structure checks status/tools/modules/trust
- [x] ISC-7: test_trust_sequence_verify_then_trust verifies full sequence result
- [x] ISC-8: All 5 hardening tests pass without errors
- [x] ISC-9: test_mcp_proxy_tools.py created at correct path
- [x] ISC-10: _tool_list_modules test verifies modules and count keys
- [x] ISC-11: _tool_list_modules test verifies modules is a list
- [x] ISC-12: _tool_list_modules test verifies count matches len(modules)
- [x] ISC-13: _tool_module_info test verifies known module returns correct keys
- [x] ISC-14: _tool_module_info test verifies unknown module returns error key
- [x] ISC-15: _tool_module_info test verifies module field matches input
- [x] ISC-16: _tool_pai_status test verifies installed key present
- [x] ISC-17: _tool_pai_status test verifies return is dict
- [x] ISC-18: _tool_pai_awareness test verifies return is dict
- [x] ISC-19: _tool_pai_awareness graceful error path tested
- [x] ISC-20: No mocks in either test file
- [x] ISC-21: setup_method calls reset_trust for gateway tests
- [x] ISC-22: All proxy tests pass uv run pytest -x (49/49)
- [x] ISC-23: All hardening tests pass uv run pytest -x (25/25 total, 5/5 new)
- [x] ISC-24: Coverage improves: proxy_tools.py 13%->meaningful; overall 31.50%

## Decisions

- _tool_pai_awareness returns real data (missions/projects/telos keys) — test that
- _tool_module_info with nonexistent module returns {"error": ...} not raises
- trust_tool("codomyrmex.write_file") on fresh registry → aggregate = TRUSTED

## Verification
