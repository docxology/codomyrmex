---
prd: true
id: PRD-20260226-repo-wide-doc-audit
status: COMPLETE
mode: interactive
effort_level: Deep
created: 2026-02-26
updated: 2026-02-26
iteration: 1
maxIterations: 128
loopStatus: completed
last_phase: LEARN
failing_criteria: []
verification_summary: "13/13"
parent: null
children: []
---

# Repo-Wide Documentation Audit

> Comprehensively audit and fix all documentation inaccuracies, stale counts, version strings, broken links, and placeholder content across the entire codomyrmex repository.

## STATUS

| What | State |
|------|-------|
| Progress | 13/13 criteria passing |
| Phase | COMPLETE |
| Next action | None — all criteria passed |
| Blocked by | Nothing |

## CONTEXT

### Problem Space
The codomyrmex repo had accumulated significant documentation drift since the last major doc pass: stale module counts (84/86/89 used inconsistently for the same concept), stale version strings (v0.4.0 in docs/pai/ instead of v1.0.3-dev), wrong MCP tool/resource/skills counts, placeholder content in sub-module SPECs, and a broken link. A Deep-effort audit was needed to find and fix all instances.

### Key Files
- `README.md` — Root README with version/test/coverage badges
- `CLAUDE.md` — Auto-discovered module count, extended modules list, static tool count
- `PAI.md` — Root authoritative PAI↔codomyrmex bridge doc
- `AGENTS.md` — Coverage gate threshold
- `docs/pai/architecture.md` — Full architecture diagram with all key counts
- `docs/pai/tools-reference.md` — Tool summary tables
- `src/codomyrmex/INDEX.md` — Module count confirmation table
- `src/codomyrmex/validation/MCP_TOOL_SPECIFICATION.md` — Completely rewritten (was wrong)
- `docs/modules/graph_rag/SPEC.md` — Replaced TODO placeholder

### Constraints
- Module count: 86 functional modules (89 Python packages minus root, tests, examples)
- Auto-discovered: 33 modules with mcp_tools.py (skills was newly added)
- Static tools: 20 (17 core + 3 universal proxy)
- Dynamic tools: ~146 @mcp_tool functions
- Resources: 3 (2 in definitions.py + 1 registered dynamically in server.py)
- Prompts: 10
- PAI skills: 56 dirs in ~/.claude/skills/
- Coverage gate: ≥67% (pytest.ini)
- Version: v1.0.3-dev (pyproject.toml: 1.0.3.dev0)
- Tests: 15,179 collected (Sprint 9)
- Coverage: ~68%

### Decisions Made
- Settled on 86 as the canonical functional module count (not 84, 88, or 89)
- docs/pai/ version string: v0.4.0 → v1.0.3-dev (not v1.0.4-dev)
- validation/MCP_TOOL_SPECIFICATION.md was completely wrong ("No MCP Tools Defined") — rewrote with actual tool specs for validate_schema, validate_config, validation_summary

## PLAN

Single-agent sequential sweep:
1. Audit source of truth files (pytest.ini, pyproject.toml, server.py, definitions.py)
2. Scan all markdown docs for stale values using grep patterns
3. Fix root-level docs first (README, CLAUDE.md, PAI.md, AGENTS.md)
4. Fix docs/pai/ subdirectory (architecture, tools-reference, workflows, version strings)
5. Fix src/codomyrmex/ subdocs (INDEX.md, sub-module SPECs)
6. Fix remaining docs/ subdirectories
7. Replace all placeholder content ("Decision 1: Rationale", "TODO: Define", etc.)
8. Verify broken links

## IDEAL STATE CRITERIA

### Accuracy
- [x] ISC-C1: All module count references consistently show 86 | Verify: Grep: "89 modules" or "84 modules" across docs = 0
- [x] ISC-C2: All version strings in docs show v1.0.3-dev not v0.4.0 | Verify: Grep: "v0.4.0" in docs/ = 0
- [x] ISC-C3: MCP tool counts (static/dynamic) accurate in all docs | Verify: Grep: "19 static" or "14 static" = 0
- [x] ISC-C4: README badges show current version test count coverage | Verify: Read README.md badges section
- [x] ISC-C5: PAI skills count (56) accurate in PAI.md | Verify: Read PAI.md skills line
- [x] ISC-C6: Coverage gate ≥67% in AGENTS.md matches pytest.ini | Verify: Grep: "≥80%" in AGENTS.md = 0

### Completeness
- [x] ISC-C7: validation MCP_TOOL_SPECIFICATION has all 3 actual tools documented | Verify: Read file, check 3 tool sections
- [x] ISC-C8: CLAUDE.md extended modules list includes all 33 discovered modules | Verify: Count items in extended modules list
- [x] ISC-C9: Resources count shows 3 (not 2) in all docs | Verify: Grep: '"count": 2' in docs = 0

### Content Quality
- [x] ISC-C10: No placeholder text remains in any module SPEC | Verify: Grep: "Decision 1: Rationale" across src/ = 0
- [x] ISC-C11: graph_rag SPEC has real API documentation not TODO | Verify: Read docs/modules/graph_rag/SPEC.md
- [x] ISC-C12: No broken internal links in README | Verify: Read README.md, check docs/project/todo.md link fixed

### Anti-Criteria
- [x] ISC-A1: No new inaccuracies introduced while fixing existing ones | Verify: Spot-check 5 modified files for consistency
- [x] ISC-A2: No source code files modified only documentation | Verify: git diff --name-only shows only .md files

## DECISIONS

**2026-02-26:** Chose 86 (not 89) as canonical module count — 89 counts Python packages with __init__.py but includes codomyrmex root, tests/, examples/ which are not functional modules. Docs targeting humans/agents should say 86.

**2026-02-26:** Resources: 3 total despite only 2 in definitions.py — server.py dynamically registers codomyrmex://discovery/metrics. This is correct and docs saying "3 resources" was right; the workflows.md example with count:2 was the bug.

**2026-02-26:** Skills count updated 38→56 — the 38 was very stale; actual dir count in ~/.claude/skills/ is 56.

## LOG

### Iteration 1 — 2026-02-26
- Phase reached: LEARN (COMPLETE)
- Criteria progress: 13/13
- Work done: Comprehensive documentation audit and correction pass. 40+ markdown files updated: README.md (4 fixes), CLAUDE.md (3 fixes), PAI.md (5 fixes), AGENTS.md (1 fix), docs/pai/* (version strings + 5 accuracy fixes), src/codomyrmex/INDEX.md (4 fixes), validation/MCP_TOOL_SPECIFICATION.md (complete rewrite), graph_rag/SPEC.md (TODO→real content), 9 sub-module SPECs (placeholder→real content), docs/cognitive/docs/project/docs/getting-started/* (78→86 module counts)
- Failing: none
- Context for next iteration: Work complete, no follow-up needed
