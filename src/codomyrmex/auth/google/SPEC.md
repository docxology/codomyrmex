# Google Auth -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Wraps `google-auth-oauthlib` to provide OAuth2 credential acquisition, caching, and refresh for Google Calendar and Gmail APIs. Supports the InstalledAppFlow (local browser redirect) for interactive authorization.

## Architecture

Single-class design: `GoogleAuthenticator` encapsulates the full OAuth2 lifecycle. Token cache uses a local JSON file with restricted permissions (`0o600`). The credential acquisition flow is:

1. Load cached token from `token.json`
2. If valid, return immediately
3. If expired with refresh token, attempt silent refresh
4. If refresh fails or no cached token, run interactive browser flow
5. Cache new credentials to `token.json`

## Key Classes

### `GoogleAuthenticator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `client_secrets_file: str, token_cache_file: str or None, scopes: list or None` | -- | Initialize with client secrets path; raises `ImportError` if deps missing |
| `get_credentials` | -- | `Credentials` | Acquire valid credentials (cache, refresh, or interactive flow) |
| `_run_interactive_flow` | -- | `Credentials` | Launch local browser-based OAuth2 authorization |

### Constants

| Name | Value | Description |
|------|-------|-------------|
| `DEFAULT_SCOPES` | `["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/gmail.modify"]` | Default OAuth2 scopes |
| `AUTH_AVAILABLE` | `bool` | Whether Google auth libraries are installed |

## Token Cache Behavior

- Default path: `~/.codomyrmex/auth/google/token.json`
- Parent directory created automatically via `os.makedirs(exist_ok=True)`
- File permissions set to `0o600` (owner read/write only)
- Malformed cache files are silently ignored and trigger re-authentication

## Dependencies

- **Internal**: None (standalone auth module)
- **External**: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client` (all optional; install via `uv sync --extra calendar --extra email`)

## Constraints

- Interactive flow requires a desktop environment with a browser.
- Client secrets file must be downloaded from Google Cloud Console.
- Zero-mock: real OAuth2 flows only, `ImportError` when dependencies are missing.
- Token refresh failures are logged at warning level before falling back to interactive flow.

## Error Handling

- `ImportError`: raised at init if Google auth libraries are not installed.
- `FileNotFoundError`: raised if `client_secrets_file` does not exist when interactive flow is triggered.
- Malformed `token.json`: logged as warning, silently ignored, re-authentication initiated.
- OAuth refresh failures: logged as warning, falls back to interactive flow.
