# auth

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Authentication and authorization module providing API key management, token-based authentication, and permission-based access control. The `Authenticator` class validates credentials and checks authorization against resources and permissions. Tokens are managed through `TokenManager` with validation handled by `TokenValidator`. The `PermissionRegistry` maintains resource-permission mappings for fine-grained access control.

## Key Exports

### Core Classes

- **`Authenticator`** -- Central authentication engine that validates credentials and checks authorization against resources and permissions
- **`Token`** -- Token data class representing an authenticated session with metadata
- **`TokenManager`** -- Manages token lifecycle including creation, refresh, and revocation
- **`APIKeyManager`** -- Manages API key generation, storage, rotation, and validation
- **`PermissionRegistry`** -- Registry of resource-to-permission mappings for authorization checks
- **`TokenValidator`** -- Validates token integrity, expiration, and claims

### Convenience Functions

- **`authenticate()`** -- Authenticate with a credentials dictionary, returns a Token or None
- **`authorize()`** -- Check if a token has a specific permission on a resource, returns bool
- **`get_authenticator()`** -- Get an Authenticator instance with default configuration

## Directory Contents

- `__init__.py` - Module entry point with convenience authenticate/authorize functions
- `authenticator.py` - Core `Authenticator` class for credential validation and authorization
- `token.py` - `Token` data class and `TokenManager` for token lifecycle
- `api_key_manager.py` - `APIKeyManager` for API key generation, rotation, and validation
- `permissions.py` - `PermissionRegistry` for resource-permission mappings
- `validator.py` - `TokenValidator` for token integrity and expiration checks

## Navigation

- **Full Documentation**: [docs/modules/auth/](../../../docs/modules/auth/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
