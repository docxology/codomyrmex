# Google Auth Submodule Testing Rules

## Instructions

1. This module triggers blocking, interactive HTTP server prompts requesting user authorization.
2. Ensure you **never** accidentally trigger `get_credentials()` inside headless integration test suites without mocking the browser interaction, OR gracefully skip the tests via `@pytest.mark.skipif(os.environ.get("CODOMYRMEX_RUN_LIVE_AUTH_TESTS") != "1")`.
3. Under the "Zero-Mock" architecture of Codomyrmex, active browser flows are difficult to automate. Focus testing on schema validation, missing file errors (`FileNotFoundError` on missing `client_secrets`), and ensuring robust handling of invalid `token.json` structures.
