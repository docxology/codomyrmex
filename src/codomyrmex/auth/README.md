# auth

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Authentication and authorization with API key management, OAuth integration, and access control. Provides provider-agnostic auth interface with support for username/password, API key, and token-based authentication with permission checking and token refresh capabilities.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `api_key_manager.py` – File
- `authenticator.py` – File
- `token.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.auth import Authenticator, APIKeyManager, TokenManager

# Authentication
authenticator = Authenticator()
token = authenticator.authenticate({"username": "user", "password": "pass"})
token = authenticator.authenticate({"api_key": "codomyrmex_..."})

# Authorization
is_authorized = authenticator.authorize(token, "resource", "read")

# API key management
api_key_manager = APIKeyManager()
api_key = api_key_manager.generate_api_key("user123", permissions=["read", "write"])
user_info = api_key_manager.validate_api_key(api_key)

# Token management
token_manager = TokenManager()
new_token = token_manager.create_token("user123", permissions=["read"], ttl=3600)
is_valid = token_manager.validate_token(new_token)
refreshed = token_manager.refresh_token(new_token)
```

