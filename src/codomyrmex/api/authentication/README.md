# api/authentication

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

API authentication utilities. Provides pluggable authentication mechanisms for API endpoints including API key, bearer token, HTTP basic auth, and HMAC signature verification. All authenticators implement a common `Authenticator` abstract base class and return standardized `AuthResult` objects.

## Key Exports

### Enums

- **`AuthType`** -- Authentication type enumeration (API_KEY, BEARER_TOKEN, BASIC_AUTH, OAUTH2, HMAC, JWT)

### Data Classes

- **`AuthCredentials`** -- Authentication credentials container holding auth_type, identifier, secret, and metadata
- **`AuthResult`** -- Result of an authentication attempt with authenticated flag, identity, roles, scopes, expiry, and error fields; includes `to_dict()` for serialization

### Abstract Base

- **`Authenticator`** -- ABC defining the `authenticate(request)` interface all authenticators implement

### Authenticator Implementations

- **`APIKeyAuthenticator`** -- API key authentication via header or query parameter; supports `register_key()`, `revoke_key()`, and `generate_key()` for key lifecycle management
- **`BearerTokenAuthenticator`** -- Bearer token authentication with built-in token store and TTL; supports `create_token()` and optional custom validator callable
- **`BasicAuthenticator`** -- HTTP Basic authentication with SHA-256 password hashing; supports `register_user()` with role assignment
- **`HMACAuthenticator`** -- HMAC signature-based authentication with timestamp replay protection; supports `register_client()` and `sign_request()` for both verification and signing

### Factory

- **`create_authenticator()`** -- Factory function to instantiate authenticators by `AuthType`

## Directory Contents

- `__init__.py` - Package init; contains all authentication classes inline (single-file module)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [api](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
