# Google Auth for Codomyrmex

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

This submodule handles interactive and cached OAuth 2.0 device/server flows for integrating Google Cloud services programmatically.

## Configuration

Before running any scripts, ensure you have downloaded a `client_secrets.json` containing your OAuth2 Client ID and Client Secret from the Google Cloud Console.

```python
from codomyrmex.auth.google import GoogleAuthenticator

auth = GoogleAuthenticator(client_secrets_file="path/to/client_secrets.json")

# Starts an interactive browser flow if `token.json` is not found or expired
creds = auth.get_credentials()
```

By default it grabs scopes for both Calendar read/write and Gmail modify permissions, fulfilling bidirectional needs for the `calendar` and `email` packages. It caches the long-lived refresh tokens dynamically at `~/.codomyrmex/auth/google/token.json`.
