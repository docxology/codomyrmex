# SPEC.md — agents/google_workspace

## Module Specification

### Purpose
Provide a subprocess-based wrapper around the `gws` CLI for accessing all Google Workspace APIs without SDK dependencies.

### Architecture
- **Pattern**: Standalone runner (same as `aider` module)
- **Binary**: `gws` from `@googleworkspace/cli` npm package
- **Auth**: Via `gws auth login` or environment variables
- **Output**: JSON-parsed or NDJSON-parsed or raw string

### Public API

#### `GoogleWorkspaceRunner(account, timeout)`
Main class. Methods:
- `run(service, resource, method, *, params, body, page_all, dry_run)` -> `dict[str, str]`
- `schema(tool_path)` -> `dict[str, str]`
- `check()` -> `str`

#### `get_gws_version()` -> `str`
Returns installed gws version or empty string.

#### `HAS_GWS: bool`
Module-level flag indicating if gws binary is available.

#### `GWSConfig`
Dataclass: `token`, `credentials_file`, `account`, `timeout`, `page_all`.
Properties: `has_token`, `has_credentials`, `has_auth`.

### Exceptions
- `GWSError` — base
- `GWSNotInstalledError` — binary not in PATH
- `GWSTimeoutError` — subprocess timeout
- `GWSAuthError` — auth missing/invalid
- `GWSCommandError(message, returncode, stderr)` — non-zero exit code

### Zero-Mock Policy
Tests use `@pytest.mark.skipif(shutil.which("gws") is None)` for subprocess tests.
No mocking of subprocess calls.
