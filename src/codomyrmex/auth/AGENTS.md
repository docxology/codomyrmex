# Codomyrmex Agents — src/codomyrmex/auth

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Auth Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Authentication and authorization module providing API key management, OAuth integration, and access control for the Codomyrmex platform. This module enables secure access to platform resources through multiple authentication methods.

The auth module serves as the security layer for authentication and authorization, integrating with the `security` and `api` modules to provide comprehensive access control.

## Module Overview

### Key Capabilities
- **Authentication**: Verify user credentials and issue tokens
- **Authorization**: Check user permissions and access rights
- **Token Management**: Issue, validate, refresh, and revoke tokens
- **API Key Management**: Generate, store, and manage API keys securely
- **OAuth Integration**: OAuth 2.0 flow support for external providers

### Key Features
- Provider-agnostic authentication interface
- Support for multiple authentication methods
- Role-based access control
- Secure credential storage
- Token expiration and refresh handling

## Function Signatures

### Authentication Functions

```python
def authenticate(credentials: dict) -> Optional[Token]
```

Authenticate a user with provided credentials.

**Parameters:**
- `credentials` (dict): User credentials (username/password, API key, etc.)

**Returns:** `Optional[Token]` - Authentication token if successful, None otherwise

**Raises:**
- `AuthenticationError`: If authentication fails

```python
def authorize(token: Token, resource: str, permission: str) -> bool
```

Check if a token has permission to access a resource.

**Parameters:**
- `token` (Token): Authentication token
- `resource` (str): Resource identifier
- `permission` (str): Permission type (read, write, execute, etc.)

**Returns:** `bool` - True if authorized, False otherwise

```python
def refresh_token(token: Token) -> Optional[Token]
```

Refresh an expired or soon-to-expire token.

**Parameters:**
- `token` (Token): Current authentication token

**Returns:** `Optional[Token]` - New token if refresh successful, None otherwise

### Token Management Functions

```python
def validate_token(token: Token) -> bool
```

Validate a token's signature and expiration.

**Parameters:**
- `token` (Token): Token to validate

**Returns:** `bool` - True if token is valid, False otherwise

```python
def revoke_token(token: Token) -> bool
```

Revoke a token, preventing further use.

**Parameters:**
- `token` (Token): Token to revoke

**Returns:** `bool` - True if revocation successful

### API Key Management Functions

```python
def generate_api_key(user_id: str, permissions: list[str] = None) -> str
```

Generate a new API key for a user.

**Parameters:**
- `user_id` (str): User identifier
- `permissions` (list[str]): Optional list of permissions

**Returns:** `str` - Generated API key

```python
def validate_api_key(api_key: str) -> Optional[dict]
```

Validate an API key and return associated user/permission information.

**Parameters:**
- `api_key` (str): API key to validate

**Returns:** `Optional[dict]` - User/permission info if valid, None otherwise

```python
def revoke_api_key(api_key: str) -> bool
```

Revoke an API key.

**Parameters:**
- `api_key` (str): API key to revoke

**Returns:** `bool` - True if revocation successful

### OAuth Functions

```python
def initiate_oauth_flow(provider: str, redirect_uri: str) -> str
```

Initiate OAuth 2.0 authorization flow.

**Parameters:**
- `provider` (str): OAuth provider name
- `redirect_uri` (str): Redirect URI for OAuth callback

**Returns:** `str` - Authorization URL

```python
def complete_oauth_flow(code: str, state: str) -> Optional[Token]
```

Complete OAuth 2.0 flow and exchange code for token.

**Parameters:**
- `code` (str): Authorization code from OAuth provider
- `state` (str): State parameter for CSRF protection

**Returns:** `Optional[Token]` - Authentication token if successful

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `authenticator.py` – Main authentication engine
- `token_manager.py` – Token management and validation
- `api_key_manager.py` – API key generation and management
- `oauth_handler.py` – OAuth 2.0 flow handling

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification
- `SECURITY.md` – Security considerations and best practices

## Operating Contracts

### Universal Auth Protocols

All authentication operations within the Codomyrmex platform must:

1. **Security First** - All credentials and tokens must be handled securely
2. **Token Expiration** - Tokens must have expiration times
3. **Permission Validation** - All authorization checks must be explicit
4. **Audit Logging** - All authentication events must be logged
5. **Error Handling** - Authentication failures must not leak sensitive information

### Integration Guidelines

When integrating with other modules:

1. **Use Security Module** - Integrate with security module for threat detection
2. **API Middleware** - Use auth middleware for API endpoint protection
3. **Secret Management** - Store credentials via config_management module
4. **Logging** - Log all authentication events via logging_monitoring

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [security](../security/AGENTS.md) - Security scanning
    - [api](../api/AGENTS.md) - API framework
    - [config_management](../config_management/AGENTS.md) - Secret management

