# Authentication Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Auth module provides authentication and authorization capabilities for Codomyrmex, including API key management, OAuth integration, token handling, and access control.

## Key Features

- **Authenticator**: Core authentication logic with credential validation
- **Token Management**: Create, validate, and refresh tokens
- **API Key Manager**: Secure API key storage and validation
- **Access Control**: Resource-based permission checking

## Quick Start

```python
from codomyrmex.auth import (
    authenticate,
    authorize,
    get_authenticator,
    Token,
    TokenManager,
    APIKeyManager,
)

# Authenticate with credentials
credentials = {"username": "user", "password": "pass"}
token = authenticate(credentials)

if token:
    # Check authorization for a resource
    can_read = authorize(token, resource="documents", permission="read")
    can_write = authorize(token, resource="documents", permission="write")
    
    print(f"Read access: {can_read}")
    print(f"Write access: {can_write}")

# API Key Management
key_manager = APIKeyManager()
api_key = key_manager.create_key(name="my-integration")
is_valid = key_manager.validate_key(api_key)

# Token operations
token_manager = TokenManager()
new_token = token_manager.create(user_id="user123", permissions=["read"])
refreshed = token_manager.refresh(new_token)
```

## Core Classes

| Class | Description |
|-------|-------------|
| `Authenticator` | Core authentication with credential validation |
| `Token` | Token representation with claims and expiration |
| `TokenManager` | Token lifecycle management (create, refresh, revoke) |
| `APIKeyManager` | API key creation, storage, and validation |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `authenticate(credentials)` | Authenticate with credentials dict |
| `authorize(token, resource, permission)` | Check token permissions |
| `get_authenticator()` | Get an authenticator instance |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `AuthenticationError` | Authentication operations failed |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
