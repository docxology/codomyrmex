# Codomyrmex Agents — src/codomyrmex/auth

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Auth module provides authentication and authorization capabilities for the Codomyrmex ecosystem. It supports API key management, token-based authentication with configurable TTL, role-based access control through a permission registry, and user credential validation for securing access to Codomyrmex services and resources.

## Active Components

### Core Infrastructure

- `authenticator.py` - Main authentication and authorization logic
  - Key Classes: `Authenticator`, `AuthenticationError`
  - Key Functions: `authenticate()`, `authorize()`, `refresh_token()`, `revoke_token()`
- `token.py` - Token management and validation
  - Key Classes: `Token`, `TokenManager`
  - Key Functions: `create_token()`, `validate_token()`, `revoke_token()`, `refresh_token()`
- `api_key_manager.py` - API key generation and validation
  - Key Classes: `APIKeyManager`
  - Key Functions: `generate_api_key()`, `validate_api_key()`, `revoke_api_key()`
- `permissions.py` - Role-based permission management
  - Key Classes: `PermissionRegistry`
- `validator.py` - Token validation utilities
  - Key Classes: `TokenValidator`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `Authenticator` | authenticator | Central authentication and authorization |
| `Token` | token | Authentication token data class |
| `TokenManager` | token | Token lifecycle management |
| `APIKeyManager` | api_key_manager | API key generation and validation |
| `PermissionRegistry` | permissions | Role-based permission registry |
| `TokenValidator` | validator | Token signature and expiration validation |
| `AuthenticationError` | authenticator | Exception for authentication failures |
| `authenticate()` | __init__ | Module-level authentication function |
| `authorize()` | __init__ | Module-level authorization function |
| `get_authenticator()` | __init__ | Get authenticator instance |
| `create_token()` | token | Create new authentication token |
| `validate_token()` | token | Validate token validity |
| `revoke_token()` | token | Revoke an active token |
| `refresh_token()` | token | Refresh expiring token |
| `generate_api_key()` | api_key_manager | Generate new API key |
| `validate_api_key()` | api_key_manager | Validate API key |
| `revoke_api_key()` | api_key_manager | Revoke API key |
| `is_expired()` | token | Check if token is expired |
| `to_dict()` | token | Serialize token to dictionary |
| `from_dict()` | token | Deserialize token from dictionary |
| `has_permission()` | permissions | Check role permissions |

## Operating Contracts

1. **Logging**: All operations use `logging_monitoring` for structured logging
2. **Error Handling**: Operations raise `AuthenticationError` for consistent error handling
3. **Token TTL**: Default token lifetime of 3600 seconds (configurable)
4. **API Key Format**: Keys prefixed with `codomyrmex_` followed by URL-safe token
5. **Permission Model**: Role-based with fallback to direct token permissions

## Token Structure

| Field | Type | Description |
| :--- | :--- | :--- |
| `token_id` | str | Unique token identifier (UUID) |
| `user_id` | str | Associated user identifier |
| `permissions` | list[str] | List of granted permissions |
| `expires_at` | float | Expiration timestamp |
| `created_at` | float | Creation timestamp |

## Integration Points

- **logging_monitoring** - Structured logging for all operations
- **exceptions** - Base exception classes (`CodomyrmexError`)
- **encryption** - Secure token signing and credential storage
- **api** - API authentication middleware

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| encryption | [../encryption/AGENTS.md](../encryption/AGENTS.md) | Cryptographic operations |
| api | [../api/AGENTS.md](../api/AGENTS.md) | API endpoints |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security analysis |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
