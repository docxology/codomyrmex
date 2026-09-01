# Agent-Ergonomics Deep Pass - codomyrmex - 2026-08-31

Agent: codomyrmex lane of the agent-ergonomics fleet. Pre-existing dirty files at dispatch: 69 (all left untouched).

## PHASE 0 - Preflight

- Repo path confirmed per brief; branch `main`, remote origin present. At fetch: `ahead 1, behind 4`.
- Inventory: entry docs README.md (852 lines), AGENTS.md (500), CLAUDE.md, INDEX.md, MODULES.md, RULES.md, TODO.md (46). Executable-truth generators present: `scripts/doc_inventory.py`, `scripts/rasp_gap_report.py`. TODO.md exists; table-by-section conventions preserved.

## PHASE 1 - Cold-start audit

- (a) Current status: PASS - snapshot counts carry their verification command and canonical home (docs/reference/inventory.md). Weak spot: INDEX.md shows 36,028 tests vs README/inventory 36,049 with no supersede marker.
- (b) What to do next: FAIL - no entry doc linked TODO.md (verified by grep across README/AGENTS/CLAUDE/docs/README; only INDEX.md's table mentioned it).
- (c) Primary verification: PASS - `uv sync` then `uv run codomyrmex doctor --all`; `make test` / coverage-gate command with HYPOTHESIS_NO_NPY=1 caveat in CLAUDE.md. Commands not executed this pass (full collect on the slow external drive exceeds the 120s budget; claims carry their verify command inline).
- Link check (scripted scan of all root *.md relative links): 0 broken.
- SECURITY_AUDIT_REPORT.md at root is a dated 2026-07-31 point-in-time audit with internally superseded counts (says 655 tools vs canonical 627), not linked from any entry doc.

## PHASE 2 - Scope (entries added to TODO.md)

- M-ERG-1 (Minor): INDEX.md test-count snapshot conflict, no supersede marker.
- M-ERG-2 (Medium): backlog unreachable from README.md / AGENTS.md.
- M-ERG-3 (Medium): stale root security audit reads as current.
- M-ERG-4 (Minor): no dated review log convention; created this file.

## PHASE 3 - Implement

1. INDEX.md: 36,049 with explicit supersede note; inventory.md remains canonical.
2. README.md Documentation Hub and AGENTS.md Key Files now name TODO.md as the authoritative backlog (one-hop reachability from both entry docs).
3. SECURITY_AUDIT_REPORT.md moved to docs/compliance/SECURITY_AUDIT_REPORT_2026-07-31.md (git mv, dated name marks it historical; no entry doc linked it, so nothing dangles).
4. This log created.
- Deferred: none.

## PHASE 4 - Verify and close

- Link checker re-run on touched docs: 0 broken.
- Path-scoped adds only; `git status --porcelain -- <paths>` checked pre-commit; no pre-existing dirty file swept in.
- Fast gate: not run (doc-only changes; declared docs gates unverified for runtime on this drive - disclosed, not invented).

## Addendum — inventory re-verification (2026-08-31, evening lane)

- Executable truth via `scripts/doc_inventory.py`: top-level 130, mcp_tools.py 151, @mcp_tool 627, workflows 37 — all match docs.
- Drift found: inventory said **39** agent packages; live count is **40** (41 child dirs incl. dirty `open_gauss` submodule, no `__init__.py`). Fixed in `docs/reference/inventory.md` (definition row + value row, with clarifying note).
- Drift found: docs markdown count 1,204 documented vs 1,208 live (docs/security lane additions). Fixed in `docs/reference/inventory.md`, README.md (4 occurrences), and INDEX.md if present. `Last updated` bumped to 2026-08-31.
- `docs/agents/AGENTS.md` "41 top-level agent packages" left as-is — it mirrors the tree (41 child dirs), not the `__init__.py` count; both figures now traceable.
