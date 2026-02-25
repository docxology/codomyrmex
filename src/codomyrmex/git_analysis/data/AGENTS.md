# git_analysis/data — Agent Context

## Purpose

This directory stores persisted output from `git_analysis` operations — primarily
cached analysis results and generated reports for the codomyrmex repository itself.

## Key Facts for Agents

- `codomyrmex_description.md` is the live analysis output for this repo
- Files here are **tracked in git** — safe to read, careful about overwriting
- Do NOT store large binary blobs or `.gitnexus/` graph data here
- This is output storage, not source code

## When to Use This Directory

**Read `codomyrmex_description.md` when you need:**
- Quick overview of the codomyrmex codebase structure
- Contributor statistics without running a live analysis
- Historical snapshot of the module layout

**Write to this directory when:**
- Running a documentation sprint or codebase audit
- Generating fresh analysis reports to commit as living docs
- Updating the description after major structural changes

## Quick Analysis Commands

```bash
# Read cached description
cat src/codomyrmex/git_analysis/data/codomyrmex_description.md

# Generate fresh contributor stats
uv run python -c "
from codomyrmex.git_analysis import GitHistoryAnalyzer
a = GitHistoryAnalyzer('.')
for s in a.get_contributor_stats(max_count=10):
    print(s['author'], s['commit_count'])
"

# Get recent hotspots
uv run python -c "
from codomyrmex.git_analysis import GitHistoryAnalyzer
a = GitHistoryAnalyzer('.')
for h in a.get_hotspot_analysis(top_n=5):
    print(h['file_path'], h['change_count'])
"
```

## What NOT to Put Here

- Raw git objects or pack files
- `.gitnexus/` graph database files (these are gitignored at repo root)
- Temporary analysis artifacts from a single session
- Binary files of any kind
