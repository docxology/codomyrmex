# SPEC.md — cloud/google_workspace

## Module Specification

### Purpose
Provide typed Python SDK clients for Google Workspace APIs using service account authentication.

### Architecture
- **Pattern**: SDK wrapper (same as `cloud/infomaniak/` modules)
- **Auth**: `GoogleCredentials` with `google.oauth2.service_account`
- **Service**: `googleapiclient.discovery.build()` (lazy-loaded)
- **Base**: `GoogleWorkspaceBase` with `_safe_call()` pattern

### Public API

#### `GoogleCredentials`
- `from_env()` — reads `GWS_SERVICE_ACCOUNT_FILE` or `GOOGLE_APPLICATION_CREDENTIALS`
- `from_service_account_file(path, scopes)` — explicit file path
- `get_credentials()` — returns google.oauth2 credentials
- `build_service(name, version)` — builds API service client

#### `GoogleWorkspaceBase`
- `from_env()` — class method, creates credentials + instance
- `_get_service()` — lazy-builds + caches service client
- `_safe_call(fn, verb, resource, default)` — error-safe API call
- `__enter__` / `__exit__` — context manager

#### SDK Clients
All extend `GoogleWorkspaceBase`:
- `GoogleDriveClient` — `list_files`, `get_file`, `upload_file`, `share_file`, `delete_file`
- `GoogleGmailClient` — `list_messages`, `get_message`, `send_message`
- `GoogleCalendarClient` — `list_events`, `create_event`
- `GoogleSheetsClient` — `get_values`, `update_values`
- `GoogleDocsClient` — `get_document`, `append_text`
- `GoogleChatClient` — `send_message`

### Exceptions
- `GoogleWorkspaceError` — base
- `GoogleWorkspaceAuthError` — missing/invalid credentials
- `GoogleWorkspaceNotFoundError` — resource not found
- `GoogleWorkspaceQuotaError` — quota exceeded
- `GoogleWorkspaceAPIError(status_code, reason)` — API response error

### Zero-Mock Policy
Tests use `@pytest.mark.skipif(importlib.util.find_spec("googleapiclient") is None)` for SDK tests. All `from_env()` calls without credentials raise `GoogleWorkspaceAuthError` (no silent fallback).
