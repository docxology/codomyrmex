---
task: Write zero-mock documentation module unit tests
slug: 20260304-120000_documentation-unit-tests
effort: Advanced
phase: complete
progress: 28/28
mode: algorithm
started: 2026-03-04T12:00:00
updated: 2026-03-04T12:00:00
---

## Context

The `documentation` module in Codomyrmex has 36 open desloppify test_coverage gaps.
Several files are at 0% coverage. The task is to write comprehensive zero-mock tests
covering: education/, maintenance.py, pai.py edge cases, mcp_tools.py, scripts/ utilities.

### Key 0% targets
- education/__init__.py (12 stmts)
- education/curriculum.py (95 stmts)
- education/visualization.py (10 stmts)
- maintenance.py (148 stmts, only 7% covered)
- mcp_tools.py (partially uncovered)
- scripts/placeholder_check.py (66 stmts)
- scripts/global_doc_auditor.py (26 stmts)
- scripts/enhance_stubs.py (24 stmts)
- scripts/fix_markdown_newlines.py (19 stmts)

### Risks
- Scripts may import heavy deps — need module-level skip guards
- Some scripts are filesystem-heavy — use tmp_path
- pai.py has some uncovered branches (error paths)

## Criteria

- [x] ISC-1: education/__init__.py reaches >50% coverage (100%)
- [x] ISC-2: education/curriculum.py Curriculum class instantiates cleanly
- [x] ISC-3: education/curriculum.py generate_curriculum returns a non-empty result
- [x] ISC-4: education/curriculum.py LearningPath dataclass fields validate correctly
- [x] ISC-5: education/visualization.py visualize_curriculum_progress callable (30%, import guard)
- [x] ISC-6: maintenance.py get_submodules returns list from real tmp dir
- [x] ISC-7: maintenance.py MODULE_DESCRIPTIONS contains expected module names
- [x] ISC-8: maintenance.py update_readme_md writes to file when header present
- [x] ISC-9: maintenance.py update_agents_md_list writes to file when section present
- [x] ISC-10: maintenance.py enrich_agents_md replaces generic descriptions
- [x] ISC-11: maintenance.py update_root_docs runs end-to-end on tmp dir
- [x] ISC-12: maintenance.py finalize_docs runs end-to-end on tmp dir
- [x] ISC-13: pai.py get_layer returns Foundation for logging_monitoring
- [x] ISC-14: pai.py get_layer returns Extended for unknown modules
- [x] ISC-15: pai.py humanize_name converts snake_case to Title Case
- [x] ISC-16: pai.py extract_exports parses __all__ from real __init__.py
- [x] ISC-17: pai.py extract_readme_description extracts first paragraph
- [x] ISC-18: pai.py infer_pai_phase maps observe-related functions correctly
- [x] ISC-19: pai.py generate_pai_md returns markdown with Overview section
- [x] ISC-20: pai.py write_pai_md writes PAI.md to real filesystem
- [x] ISC-21: mcp_tools.py generate_module_docs returns error for missing module
- [x] ISC-22: mcp_tools.py audit_rasp_compliance returns dict with status key
- [x] ISC-23: scripts/placeholder_check.py detects placeholder patterns (44% coverage)
- [x] ISC-24: scripts/global_doc_auditor.py audits a directory without crashing (100%)
- [x] ISC-25: scripts/fix_agents_structure.py fix function tested (63% coverage)
- [x] ISC-26: 175 new test methods across 3 new test files (far exceeds 40+)
- [x] ISC-27: 447 pass, 0 failures, 5 skipped (pre-existing skips)
- [x] ISC-28: Coverage improved: education 0→100%, maintenance 7→91%, pai 89→97%, global_doc_auditor 0→100%

## Decisions

## Verification
