---
task: "Implement cloud/google_workspace SDK module with MCP tools"
slug: "20260305-120100_google-workspace-sdk-module"
effort: Advanced
phase: complete
progress: 24/24
mode: ALGORITHM
started: "2026-03-05T12:01:00Z"
updated: "2026-03-05T12:01:00Z"
---

## Context

Implement the `cloud/google_workspace/` Python SDK module inside the codomyrmex project.
The module wraps Google Workspace APIs (Drive, Gmail, Calendar, Sheets, Docs, Chat) using
google-auth and google-api-python-client. A `GoogleCredentials` auth helper reads service
account credentials from env vars. All clients inherit from `GoogleWorkspaceBase` and use
lazy service initialization. Four new MCP tools are appended (not overwritten) to the
existing `cloud/mcp_tools.py`. Ruff must pass with zero violations.

### Risks
- Appending to mcp_tools.py must not touch existing 3 tools
- `_safe_call` must not silently swallow all errors — returns default, logs error
- Zero-mock policy: no stubs, all SDK calls raise real errors
- Ruff E501 or trailing whitespace possible in verbatim content
- `from __future__ import annotations` required for `str | None` in Python 3.10

## Criteria

- [x] ISC-1: `exceptions.py` created with 5 exception classes
- [x] ISC-2: `GoogleWorkspaceAuthError` inherits from `GoogleWorkspaceError`
- [x] ISC-3: `GoogleWorkspaceAPIError.__init__` stores status_code and reason
- [x] ISC-4: `auth.py` created with `GoogleCredentials` class
- [x] ISC-5: `GoogleCredentials.from_env` reads GWS_SERVICE_ACCOUNT_FILE first
- [x] ISC-6: `GoogleCredentials.from_env` falls back to GOOGLE_APPLICATION_CREDENTIALS
- [x] ISC-7: `GoogleCredentials.from_env` raises `GoogleWorkspaceAuthError` if neither set
- [x] ISC-8: `GoogleCredentials.build_service` raises ImportError when SDK not installed
- [x] ISC-9: `base.py` created with `GoogleWorkspaceBase` class
- [x] ISC-10: `GoogleWorkspaceBase.from_env` classmethod builds client from env credentials
- [x] ISC-11: `GoogleWorkspaceBase._safe_call` logs error and returns default on exception
- [x] ISC-12: `drive.py` created with `GoogleDriveClient` (5 methods)
- [x] ISC-13: `gmail.py` created with `GoogleGmailClient` (3 methods)
- [x] ISC-14: `calendar.py` created with `GoogleCalendarClient` (2 methods)
- [x] ISC-15: `sheets.py` created with `GoogleSheetsClient` (2 methods)
- [x] ISC-16: `docs.py` created with `GoogleDocsClient` (2 methods)
- [x] ISC-17: `chat.py` created with `GoogleChatClient` (1 method)
- [x] ISC-18: `__init__.py` exports all 14 public names in `__all__`
- [x] ISC-19: 4 new MCP tools appended to cloud/mcp_tools.py (not overwritten)
- [x] ISC-20: `gws_sdk_drive_list_files` tool returns status/files/count keys
- [x] ISC-21: `gws_sdk_gmail_list_messages` tool returns status/messages/count keys
- [x] ISC-22: `gws_sdk_calendar_list_events` tool returns status/events/count keys
- [x] ISC-23: `gws_sdk_sheets_get_values` tool returns status/values/range keys
- [x] ISC-24: `uv run ruff check` passes with zero violations on all new files

## Decisions

## Verification

- All 11 files parse as valid Python AST (uv run python /tmp/verify_gws.py)
- mcp_tools.py contains 7 tools: 3 original + 4 new GWS tools
- All 4 new tool function names confirmed present in mcp_tools.py
- `uv run ruff check` passes with zero violations on all new files
- `from __future__ import annotations` present in all files
- TYPE_CHECKING guard used in base.py to resolve F821 for GoogleCredentials
- UP037 violations auto-fixed by ruff --fix (quoted annotations removed)
