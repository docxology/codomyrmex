---
task: Write google_workspace module 5 files + ruff clean
slug: 20260305-000000_google-workspace-module
effort: Standard
phase: complete
progress: 8/8
mode: ALGORITHM
started: 2026-03-05T00:00:00Z
updated: 2026-03-05T00:00:00Z
---

## Context

Implement `src/codomyrmex/agents/google_workspace/` as a subprocess CLI wrapper for the `gws` Google Workspace CLI tool. Pattern follows `src/codomyrmex/aider/` exactly. All 5 files are fully specified by the orchestrator.

## Criteria

- [x] ISC-1: exceptions.py written with all 5 exception classes
- [x] ISC-2: config.py written with GWSConfig dataclass and get_config()
- [x] ISC-3: core.py written with GoogleWorkspaceRunner and get_gws_version()
- [x] ISC-4: mcp_tools.py written with all 10 @mcp_tool decorated functions
- [x] ISC-5: __init__.py written with all __all__ exports
- [x] ISC-6: Ruff check passes with 0 violations
- [x] ISC-7: Module directory exists at correct path
- [x] ISC-8: gws_gmail_list_messages 4-arg run() call written as specified

## Decisions

## Verification
