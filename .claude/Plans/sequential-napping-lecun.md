# Plan: Comprehensive Codomyrmex-PAI Integration Audit & Remediation

## Context

Daniel requested a comprehensive review ensuring all Codomyrmex tools are fully documented, tested, validated, modular, and available via PAI (Skills, Workflows, Hooks backend) AND browser interface. This is a full-system audit covering 106 modules across MCP bridge, trust gateway, browser dashboard, PAI skill system, and test infrastructure.

### Current State (Audit Findings)

**Overall health: 97.2%** — 103/106 modules COMPLETE. The system is mature but has specific gaps:

| Layer | Status | Key Gap |
|-------|--------|---------|
| MCP Bridge | 18 static + dynamic tools | Knowledge scope only covers 52/106 modules |
| Trust Gateway | 3-tier model working | Only 4 hardcoded destructive tools |
| Browser Dashboard | 11 pages, 16+ API endpoints | No MCP tools page, no trust status view |
| PAI Skill | SKILL.md + 2 workflows | No hooks, tool count may drift from runtime |
| Tests | 1,070 lines for PAI bridge | 5 modules missing tests, no dynamic discovery test |
| Documentation | 100% README/PAI.md/AGENTS.md/SPEC.md | 2 modules missing MCP_TOOL_SPECIFICATION.md |

---

## Implementation Plan (5 Workstreams)

### Workstream 1: Backend — MCP Bridge & Knowledge Scope Expansion

**Files to modify:**
- `src/codomyrmex/agents/pai/mcp_bridge.py` (lines 800-900, knowledge scope in `get_skill_manifest()`)
- `~/.claude/skills/Codomyrmex/SKILL.md` (lines 171-181, Knowledge Scope table)

**Tasks:**

1. **Expand knowledge scope** to cover all 106 modules organized by domain. Current 7 domains cover 52 modules. Add missing modules to appropriate domains or create new domains:
   - New domain "Collaboration & Social": `collaboration`, `relations`, `notification`, `meme`
   - New domain "Data Processing": `fpf`, `scrape`, `search`, `streaming`, `documents`, `serialization`
   - New domain "Platform": `plugin_system`, `scheduler`, `rate_limiting`, `migration`, `service_mesh`
   - New domain "AI/ML Ops": `model_ops`, `model_registry`, `model_evaluation`, `inference_optimization`, `prompt_testing`, `feature_store`, `feature_flags`
   - New domain "Specialized": `quantum`, `smart_contracts`, `dark`, `physical_management`, `chaos_engineering`, `cost_management`
   - New domain "UI & Interface": `website`, `ide`, `observability_dashboard`, `terminal_interface`, `visualization`, `video`, `audio`, `multimodal`, `accessibility`, `i18n`, `templating`
   - Existing domains expanded: add missing modules (`api`, `tool_use`, `tools`, `skills`, `workflow_testing`, `dependency_injection`, `edge_computing`, `module_template`, `examples`)

2. **Expand dynamic discovery scan targets** in `_discover_dynamic_tools()` (line 610-623). Add modules that have `@mcp_tool` decorated functions beyond the current 13. Use `discover_all_public_tools()` (Phase 2) as the catch-all.

3. **Update codomyrmexVerify workflow** (`~/.claude/skills/Codomyrmex/Workflows/codomyrmexVerify.md`) — fix tool count references from "15 MCP tools" to match actual count (53+ static + dynamic).

4. **Validate trust gateway classification** — run `verify_capabilities()` and confirm all 53+ tools are correctly classified as safe vs destructive based on pattern matching in `trust_gateway.py` (lines 66-83).

### Workstream 2: Frontend — Browser Dashboard Enhancements

**Files to modify:**
- `src/codomyrmex/website/server.py` — add GET `/api/tools` endpoint
- `src/codomyrmex/website/data_provider.py` — add `get_mcp_tools()` method
- `src/codomyrmex/website/templates/tools.html` — new template (CREATE)
- `src/codomyrmex/website/templates/base.html` — add "Tools" nav link
- `src/codomyrmex/website/templates/modules.html` — enhance module cards
- `src/codomyrmex/website/templates/awareness.html` — add skills/workflows section
- `src/codomyrmex/website/generator.py` — register tools.html generation

**Reuse existing patterns:**
- `data_provider.py:DataProvider.get_modules()` pattern for `get_mcp_tools()`
- `server.py` GET handler routing pattern (line 60+)
- `templates/modules.html` card/modal pattern for tools page
- `templates/awareness.html` metrics section pattern

**Tasks:**

1. **Create `/api/tools` endpoint** in server.py:
   - Import from `codomyrmex.agents.pai.mcp_bridge` to get tool registry
   - Import from `codomyrmex.agents.pai.trust_gateway` for trust levels
   - Return JSON: `{tools: [{name, description, category, trust_level, is_destructive}], resources: [...], prompts: [...], total: N}`

2. **Create `tools.html` template** following existing template patterns:
   - Tool listing with search/filter
   - Trust level badges (UNTRUSTED=red, VERIFIED=yellow, TRUSTED=green)
   - Safe vs Destructive classification
   - Tool detail modal with input schema
   - Resources section
   - Prompts section

3. **Add "Tools" to navigation** in `base.html` header nav group

4. **Enhance modules.html** module cards to show PAI.md and MCP spec presence badges

5. **Enhance awareness.html** to show PAI skills, workflows, and hooks alongside existing mission/project data

### Workstream 3: Documentation Completeness

**Files to modify:**
- `src/codomyrmex/examples/MCP_TOOL_SPECIFICATION.md` (CREATE)
- `src/codomyrmex/tests/MCP_TOOL_SPECIFICATION.md` (CREATE)
- `~/.claude/skills/Codomyrmex/SKILL.md` — sync tool table with runtime

**Tasks:**

1. **Create MCP_TOOL_SPECIFICATION.md** for `examples` and `tests` modules — follow the standard template used by other modules

2. **Sync SKILL.md tool table** with runtime output from `get_skill_manifest()`:
   - Create `scripts/sync_skill_manifest.py` that reads runtime manifest and updates SKILL.md tool table
   - Or manually verify the 53 tools listed match current runtime

### Workstream 4: Test Coverage

**Files to modify/create:**
- `src/codomyrmex/tests/unit/logistics/test_logistics.py` (CREATE)
- `src/codomyrmex/tests/unit/spatial/test_spatial.py` (CREATE)
- `src/codomyrmex/tests/unit/testing/test_testing.py` (CREATE)
- `src/codomyrmex/tests/unit/agents/test_mcp_bridge.py` — add dynamic discovery test
- `src/codomyrmex/tests/unit/website/unit/test_server.py` — extend API coverage

**Tasks:**

1. **Create test stubs** for modules missing tests: logistics, spatial, testing. Each test file should:
   - Test module importability
   - Test key exports exist
   - Test basic functionality of public functions
   - Follow zero-mock testing policy

2. **Add dynamic tool discovery test** to `test_mcp_bridge.py`:
   ```python
   def test_dynamic_tool_discovery_returns_tools():
       from codomyrmex.agents.pai.mcp_bridge import _discover_dynamic_tools
       tools = _discover_dynamic_tools()
       assert len(tools) > 0
       # Verify tool tuple structure: (name, description, handler, schema)
       for name, desc, handler, schema in tools:
           assert isinstance(name, str)
           assert callable(handler)
   ```

3. **Extend website API tests** to cover `/api/tools` endpoint (new), and verify `/api/modules`, `/api/health` return expected data

### Workstream 5: Integration Validation & Hooks

**Files to create:**
- `scripts/validate_pai_integration.py` (CREATE)

**Tasks:**

1. **Create validation script** `scripts/validate_pai_integration.py` that checks:
   - Module count matches across: `codomyrmex.list_modules()`, dashboard `/api/modules`, SKILL.md knowledge scope
   - Tool count matches: `get_tool_registry()` vs SKILL.md tool table
   - Trust gateway covers all registered tools
   - All modules have README.md, PAI.md, AGENTS.md, SPEC.md, API_SPECIFICATION.md, MCP_TOOL_SPECIFICATION.md
   - All critical modules have tests
   - Dashboard health endpoint returns 200
   - Exit 0 on success, exit 1 with details on failure

2. **Evaluate hook need** — Codomyrmex hooks in PAI would fire on events like "module imported", "test run complete", "trust level changed". Given the current architecture uses CLI tools and skill workflows, hooks add complexity without clear benefit. Recommend: document the hook integration points but defer implementation unless Daniel wants specific event-driven behavior.

---

## Execution Order

```
Phase 1: Workstream 3 (Docs) — lightweight, no code changes risk
Phase 2: Workstream 1 (Backend) — knowledge scope + discovery expansion
Phase 3: Workstream 2 (Frontend) — dashboard enhancements
Phase 4: Workstream 4 (Tests) — cover gaps and new code
Phase 5: Workstream 5 (Integration) — validation script + final verification
```

Phases 1-2 can be parallelized. Phase 3 depends on Phase 2 (needs backend API). Phase 4 depends on Phases 2-3 (needs code to test). Phase 5 is final validation.

---

## Verification

### Per-Workstream Verification

| Workstream | Verification Command |
|-----------|---------------------|
| Backend | `uv run python -c "from codomyrmex.agents.pai.mcp_bridge import get_skill_manifest; m=get_skill_manifest(); print(f'Tools: {len(m[\"tools\"])}, Scope modules listed')"` |
| Frontend | `curl -s http://localhost:8787/api/tools \| python -m json.tool` + visual check of tools.html page |
| Docs | `find src/codomyrmex/*/MCP_TOOL_SPECIFICATION.md \| wc -l` should equal 106 |
| Tests | `uv run pytest src/codomyrmex/tests/ -v --tb=short` — 0 failures |
| Integration | `uv run python scripts/validate_pai_integration.py` — exit 0 |

### End-to-End Verification

1. Run `/codomyrmexVerify` workflow — should report all modules, accurate tool counts, all trust levels correct
2. Start dashboard (`python scripts/launch_dashboard.py`) — verify all 11+ pages load
3. Navigate to Tools page — verify all MCP tools visible with trust badges
4. Navigate to Modules page — verify PAI/MCP badges on module cards
5. Run full test suite: `uv run pytest` — 0 failures, no regressions
6. Run validation script: `python scripts/validate_pai_integration.py` — exit 0

---

## Critical Files Reference

| File | Role | Lines |
|------|------|-------|
| `src/codomyrmex/agents/pai/mcp_bridge.py` | MCP tool registration + discovery | ~900 |
| `src/codomyrmex/agents/pai/trust_gateway.py` | Trust enforcement | ~589 |
| `src/codomyrmex/agents/pai/pai_bridge.py` | PAI subsystem discovery | ~800 |
| `src/codomyrmex/website/server.py` | HTTP server + API | ~561 |
| `src/codomyrmex/website/data_provider.py` | Data aggregation | ~1148 |
| `src/codomyrmex/website/generator.py` | Static HTML generation | ~98 |
| `src/codomyrmex/website/templates/base.html` | Navigation template | base |
| `~/.claude/skills/Codomyrmex/SKILL.md` | PAI skill manifest | ~182 |
| `~/.claude/skills/Codomyrmex/Workflows/codomyrmexVerify.md` | Verify workflow | ~46 |

## ISC Summary

- **17 criteria** (13 positive + 4 anti-criteria) across 5 domains
- Domains: Backend (4), Frontend (4), Docs (3), Tests (3), Integration (3)
- Anti-criteria: no module removal, no page breakage, no test regressions, no credential exposure
