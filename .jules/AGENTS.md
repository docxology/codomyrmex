# AGENTS.md — `codomyrmex/.jules`

## Purpose

Configuration for the Jules agent runtime: one Markdown file per scheduled Jules
persona (Bolt, Palette, Sentinel). Each file pairs the persona's mandatory
session rules with a dated record of learnings, merged-PR dispositions, and
retired topics that later sessions must read before proposing a change.

## Key Files

- [`bolt.md`](bolt.md) — Bolt performance journal: dated learnings (sync/async
  wrappers, hoisted type maps, O(1) cache eviction), the mandatory
  dedupe-before-optimizing session rules, and the retired-topic list with the
  PR numbers that already landed each optimization.
- [`palette.md`](palette.md) — Palette UI/UX and accessibility spec: owned
  surfaces (`src/codomyrmex/pai_pm/server/spa/`, `src/codomyrmex/pai_pm/server/routes/`),
  session rules, surface notes, and the disposition of earlier a11y PR floods.
- [`sentinel.md`](sentinel.md) — Sentinel security journal: dated vulnerability
  learnings, session rules, and dispositions for intentional shell executors and
  already-fixed injection paths that must not be re-proposed.
- [`README.md`](README.md) — human signpost for the three persona files.

## Dependencies

- Read by the external Jules runtime at session start; no code under `src/`
  imports these files. The in-repo Jules client lives in
  [`src/codomyrmex/agents/jules/`](../src/codomyrmex/agents/jules/README.md).
- [`scripts/maintenance/close_duplicate_prs.py`](../scripts/maintenance/close_duplicate_prs.py)
  treats every `.jules/` path as a journal note (`JOURNAL_PREFIXES`), so a PR
  that only touches these files never represents a duplicate-PR family.
- `.github/workflows/jules-dispatch.yml` dispatches Jules tasks from its own
  prompt templates and does not read these files.
- Parent: [../README.md](../README.md) · Root contract: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- These files are instructions for an external agent runtime; treat edits as
  behavior changes and review them like code.
- Add journal entries under a dated `## YYYY-MM-DD - Title` heading and keep
  earlier entries: the retired-topic and disposition lists are what stop
  sessions from re-proposing merged work.
- When a persona's fix merges, record it (with its PR number) in that file's
  retired-topic or disposition list.
- The persona rules reject journal-only `.jules/` diffs; a persona PR needs a
  real code change with `file:line` evidence from `main`.
