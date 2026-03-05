---
task: Implement Google Workspace CLI + SDK Integration
slug: 20260305-061651_google-workspace-integration
effort: Comprehensive
phase: complete
progress: 80/80
mode: ALGORITHM
started: 2026-03-05T06:16:51
updated: 2026-03-05T06:16:51
---

## Context

Add two complementary Google Workspace modules to codomyrmex:
1. `agents/google_workspace/` — subprocess wrapper around `gws` CLI (like aider)
2. `cloud/google_workspace/` — direct google-api-python-client SDK layer (like infomaniak/)

Both expose @mcp_tool-decorated tools auto-discovered by PAI. The plan is fully specified:
- 6 source files in agents track (exceptions, config, core, mcp_tools, __init__)
- 9 files in cloud track (exceptions, auth, base, drive, gmail, calendar, sheets, docs, chat, __init__)
- 4 new tools appended to cloud/mcp_tools.py
- pyproject.toml + pytest.ini updated
- Zero-mock tests across 4 test files
- 8 RASP markdown files (README, AGENTS, SPEC, PAI.md for each module)

### Risks
- `gws` CLI may not be installed in test environment — all tests that call subprocess must have @pytest.mark.skipif(shutil.which("gws") is None)
- `google-api-python-client` may conflict with existing google-cloud-storage dep — need to check pyproject.toml carefully
- Cloud track's `from_env()` must raise GoogleWorkspaceAuthError (not silent fallback) when no creds set — zero-mock policy
- MCP auto-discovery scans `mcp_tools.py` — both new modules must expose @mcp_tool at module level (no __main__ guard)
- `cloud/mcp_tools.py` already has 3 tools; must append without breaking existing tools

### Plan
Parallel agent team: Track 1 agent handles agents/google_workspace/, Track 2 agent handles cloud/google_workspace/ + cloud/mcp_tools.py additions, Track 3 handles tests, Track 4 handles pyproject.toml + pytest.ini + RASP docs.

## Criteria

### Track 1: agents/google_workspace/ (subprocess/CLI layer)
- [ ] ISC-1: `agents/google_workspace/exceptions.py` created with 5 exception classes
- [ ] ISC-2: GWSError base class inherits from Exception
- [ ] ISC-3: GWSNotInstalledError inherits from GWSError
- [ ] ISC-4: GWSTimeoutError inherits from GWSError
- [ ] ISC-5: GWSAuthError inherits from GWSError
- [ ] ISC-6: GWSCommandError with message, returncode, stderr attrs
- [ ] ISC-7: `agents/google_workspace/config.py` created with GWSConfig dataclass
- [ ] ISC-8: GWSConfig reads GOOGLE_WORKSPACE_CLI_TOKEN from os.getenv
- [ ] ISC-9: GWSConfig reads GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE from os.getenv
- [ ] ISC-10: GWSConfig reads GOOGLE_WORKSPACE_CLI_ACCOUNT from os.getenv
- [ ] ISC-11: GWSConfig.timeout reads GWS_TIMEOUT env var (default 60)
- [ ] ISC-12: GWSConfig.page_all reads GWS_PAGE_ALL env var
- [ ] ISC-13: GWSConfig.has_token property returns bool
- [ ] ISC-14: GWSConfig.has_credentials property returns bool
- [ ] ISC-15: GWSConfig.has_auth property returns has_token or has_credentials
- [ ] ISC-16: get_config() function returns GWSConfig instance
- [ ] ISC-17: `agents/google_workspace/core.py` created with GoogleWorkspaceRunner class
- [ ] ISC-18: GoogleWorkspaceRunner._find_gws() raises GWSNotInstalledError if binary not in PATH
- [ ] ISC-19: GoogleWorkspaceRunner._build_env() copies os.environ and injects config vars
- [ ] ISC-20: GoogleWorkspaceRunner._build_cmd() builds ["gws", service, resource, method] base
- [ ] ISC-21: _build_cmd() appends --params json.dumps(params) when params given
- [ ] ISC-22: _build_cmd() appends --json json.dumps(body) when body given
- [ ] ISC-23: _build_cmd() appends --page-all flag when page_all=True
- [ ] ISC-24: _build_cmd() appends --dry-run flag when dry_run=True
- [ ] ISC-25: GoogleWorkspaceRunner._run_subprocess() raises GWSTimeoutError on TimeoutExpired
- [ ] ISC-26: GoogleWorkspaceRunner._parse_output() tries json.loads first, then NDJSON split
- [ ] ISC-27: GoogleWorkspaceRunner.run() returns dict with stdout, stderr, returncode keys
- [ ] ISC-28: GoogleWorkspaceRunner.schema() calls ["gws", "schema", tool_path]
- [ ] ISC-29: GoogleWorkspaceRunner.check() calls ["gws", "--version"] and returns stdout
- [ ] ISC-30: get_gws_version() module-level function uses shutil.which + subprocess
- [ ] ISC-31: `agents/google_workspace/mcp_tools.py` with 10 @mcp_tool decorated functions
- [ ] ISC-32: gws_check tool returns status/installed/version/has_auth/account
- [ ] ISC-33: gws_run tool with service/resource/method/params/body/page_all/dry_run/account/timeout
- [ ] ISC-34: gws_schema tool returns status/schema/tool_path
- [ ] ISC-35: gws_drive_list_files tool with query/page_size/fields/account/timeout
- [ ] ISC-36: gws_gmail_list_messages tool with query/max_results/account/timeout
- [ ] ISC-37: gws_calendar_list_events with calendar_id/time_min/time_max/max_results/account/timeout
- [ ] ISC-38: gws_sheets_get_values tool with spreadsheet_id/range_/account/timeout
- [ ] ISC-39: gws_tasks_list tool with tasklist_id/show_completed/account/timeout
- [ ] ISC-40: gws_mcp_start tool returns command string (does NOT spawn process)
- [ ] ISC-41: gws_config tool returns full configuration status dict
- [ ] ISC-42: All mcp_tools use lazy imports inside function body
- [ ] ISC-43: All mcp_tools wrap body in try/except Exception returning {"status":"error","message":str(exc)}
- [ ] ISC-44: `agents/google_workspace/__init__.py` exports all public names + HAS_GWS bool

### Track 2: cloud/google_workspace/ (SDK layer)
- [ ] ISC-45: `cloud/google_workspace/exceptions.py` with 5 exception classes
- [ ] ISC-46: GoogleWorkspaceAuthError inherits from GoogleWorkspaceError
- [ ] ISC-47: GoogleWorkspaceNotFoundError inherits from GoogleWorkspaceError
- [ ] ISC-48: GoogleWorkspaceQuotaError inherits from GoogleWorkspaceError
- [ ] ISC-49: GoogleWorkspaceAPIError with status_code and reason attrs
- [ ] ISC-50: `cloud/google_workspace/auth.py` with GoogleCredentials class
- [ ] ISC-51: GoogleCredentials.from_env() reads GWS_SERVICE_ACCOUNT_FILE first, then GOOGLE_APPLICATION_CREDENTIALS
- [ ] ISC-52: GoogleCredentials.from_env() raises GoogleWorkspaceAuthError if neither env var set
- [ ] ISC-53: GoogleCredentials.build_service() wraps googleapiclient.discovery.build()
- [ ] ISC-54: `cloud/google_workspace/base.py` with GoogleWorkspaceBase class
- [ ] ISC-55: GoogleWorkspaceBase.from_env() classmethod creates instance via credentials
- [ ] ISC-56: GoogleWorkspaceBase._get_service() lazily builds + caches API service
- [ ] ISC-57: GoogleWorkspaceBase._safe_call() has same signature as InfomaniakOpenStackBase._safe_call
- [ ] ISC-58: GoogleWorkspaceBase implements context manager (__enter__/__exit__)
- [ ] ISC-59: `cloud/google_workspace/drive.py` GoogleDriveClient with _api_name="drive" _api_version="v3"
- [ ] ISC-60: GoogleDriveClient.list_files(query, page_size, fields) calls Drive API
- [ ] ISC-61: GoogleDriveClient.get_file(id), upload_file(), share_file(), delete_file() implemented
- [ ] ISC-62: `cloud/google_workspace/gmail.py` GoogleGmailClient with list/get/send methods
- [ ] ISC-63: `cloud/google_workspace/calendar.py` GoogleCalendarClient with list_events/create_event
- [ ] ISC-64: `cloud/google_workspace/sheets.py` GoogleSheetsClient with get_values/update_values
- [ ] ISC-65: `cloud/google_workspace/docs.py` GoogleDocsClient with get_document/append_text
- [ ] ISC-66: `cloud/google_workspace/chat.py` GoogleChatClient with send_message
- [ ] ISC-67: `cloud/google_workspace/__init__.py` exports all clients + exceptions + auth + base
- [ ] ISC-68: `cloud/mcp_tools.py` gets 4 new gws_sdk_* tools appended (not overwriting existing)
- [ ] ISC-69: gws_sdk_drive_list_files, gws_sdk_gmail_list_messages, gws_sdk_calendar_list_events, gws_sdk_sheets_get_values tools present

### Track 3: Config files
- [ ] ISC-70: pyproject.toml gets google_workspace optional dep group with 4 packages
- [ ] ISC-71: google-api-python-client>=2.100.0 in optional deps
- [ ] ISC-72: google-auth>=2.23.0 in optional deps
- [ ] ISC-73: pytest.ini gets google_workspace marker added

### Track 4: Tests
- [ ] ISC-74: `tests/unit/agents/google_workspace/__init__.py` and `test_gws_runner.py` created
- [ ] ISC-75: test_gws_runner.py has skip guard for shutil.which("gws") is None
- [ ] ISC-76: TestGWSConfig class tests all env var reading without real gws binary
- [ ] ISC-77: TestGWSRunnerBuildCmd tests _build_cmd without subprocess call
- [ ] ISC-78: `tests/unit/cloud/google_workspace/__init__.py` and test files created
- [ ] ISC-79: cloud tests have skip guard for missing googleapiclient import
- [ ] ISC-80: All new tests pass `uv run pytest` without errors (skips for missing deps OK)

## Decisions

- No CLIAgentBase inheritance for agents track (aider pattern is simpler/more appropriate)
- gws_mcp_start returns command string only, does NOT spawn a process (safety)
- SDK layer uses lazy googleapiclient import inside _get_service() to avoid import-time failure
- _safe_call() mirrors InfomaniakOpenStackBase signature exactly for consistency

## Verification
