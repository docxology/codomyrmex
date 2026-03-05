---
task: Add zero-mock tests for all untested GWS methods
slug: 20260305-000000_confirm-gws-methods-tested
effort: Advanced
phase: build
progress: 0/24
mode: algorithm
started: 2026-03-05T00:00:00Z
updated: 2026-03-05T00:00:00Z
---

## Context

Google Workspace module (agents/google_workspace + cloud/google_workspace) had untested methods.
Plan: add zero-mock tests using _safe_call fallback path + gws subprocess error path.

### Key insight
`_safe_call` catches all exceptions → returns default type. Instantiating any client with
`GoogleCredentials(credentials_file="/nonexistent.json")` triggers build_service ImportError
(or auth error if SDK present) → _safe_call returns default → correct type checked.

`GoogleWorkspaceRunner._find_gws()` raises `GWSNotInstalledError` when gws absent;
all MCP tool functions catch `Exception` → always returns `{"status": "error"/"success"}`.

### Bug discovered (do NOT fix — test only)
`gws_gmail_list_messages` calls `runner.run("gmail", "users", "messages", "list", params=params)`
with 4 positional args. `run()` only accepts 3 before `*` keyword-only separator.
This always raises `TypeError` caught by outer try/except → always `{"status": "error"}`.

## Criteria

- [ ] ISC-1: test_mcp_tools.py created in agents/google_workspace test dir
- [ ] ISC-2: TestGWSCheckTool class with 5 tests present
- [ ] ISC-3: TestGWSConfigTool class with 6 tests present
- [ ] ISC-4: TestGWSMcpStartTool class with 4 tests present
- [ ] ISC-5: TestGWSRunTool class with 3 tests present
- [ ] ISC-6: TestGWSSchemaTool class with 3 tests present
- [ ] ISC-7: TestGWSDriveListTool class with 3 tests present
- [ ] ISC-8: TestGWSGmailListTool class with 3 tests present
- [ ] ISC-9: TestGWSCalendarTool class with 3 tests present
- [ ] ISC-10: TestGWSSheetsTool class with 3 tests present
- [ ] ISC-11: TestGWSTasksTool class with 3 tests present
- [ ] ISC-12: TestGWSRunnerBuildEnv class with 3 tests present
- [ ] ISC-13: TestGoogleCalendarClientMethods appended to test_gws_sdk.py
- [ ] ISC-14: TestGoogleSheetsClientMethods appended to test_gws_sdk.py
- [ ] ISC-15: TestGoogleDocsClientMethods appended to test_gws_sdk.py
- [ ] ISC-16: TestGoogleChatClientMethods appended to test_gws_sdk.py
- [ ] ISC-17: TestGoogleGmailExtraMethods appended to test_gws_sdk.py
- [ ] ISC-18: TestGoogleDriveUploadFile appended with skipif guard
- [ ] ISC-19: All new tests use zero-mock (no MagicMock/monkeypatch/pytest-mock)
- [ ] ISC-20: test_mcp_tools.py passes pytestmark = pytest.mark.google_workspace
- [ ] ISC-21: uv run pytest agents+cloud google_workspace tests → 0 failures
- [ ] ISC-22: ruff check finds 0 violations in new test files
- [ ] ISC-23: No source file changes made
- [ ] ISC-24: ~44 new test functions added total

## Decisions

- Use `__new__` for _build_env test to bypass config loading
- Guard upload_file test with `skipif(not _SDK_INSTALLED)` + temp file
- For all MCP tools: assert dict type + "status" key present (works for both success/error paths)
- Conditional assertions for gws-absent-specific behavior

## Verification
