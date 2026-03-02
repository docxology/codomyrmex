# Codomyrmex Agents -- src/codomyrmex/auth/google

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides `GoogleAuthenticator` for OAuth2 authentication with Google services (Calendar, Gmail). Handles token caching, automatic refresh, and interactive browser-based authorization flows using `google-auth-oauthlib`.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `authenticator.py` | `GoogleAuthenticator` | OAuth2 authentication manager with token caching and refresh |
| `authenticator.py` | `DEFAULT_SCOPES` | Default OAuth2 scopes: Calendar full access and Gmail modify |

## Operating Contracts

- `GoogleAuthenticator.__init__()` raises `ImportError` if `google-auth-oauthlib` is not installed.
- `get_credentials()` returns valid `google.oauth2.credentials.Credentials`; automatically refreshes expired tokens or initiates interactive browser flow.
- Token cache file defaults to `~/.codomyrmex/auth/google/token.json` with `0o600` permissions.
- `_run_interactive_flow()` raises `FileNotFoundError` if `client_secrets_file` does not exist.
- Malformed token cache files are silently discarded and re-authentication is triggered.

## Agent Testing Notes

- This module triggers blocking interactive browser prompts. Never call `get_credentials()` in headless test suites without a skip guard.
- Use `@pytest.mark.skipif(os.environ.get("CODOMYRMEX_RUN_LIVE_AUTH_TESTS") != "1")` for live auth tests.
- Under zero-mock policy, focus testing on schema validation, `FileNotFoundError` for missing client secrets, and invalid `token.json` handling.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client` (all optional, guarded by `try/except ImportError`)
- **Used by**: `calendar_integration.gcal.GoogleCalendar`, `email.gmail.provider`

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../README.md](../../../README.md)
