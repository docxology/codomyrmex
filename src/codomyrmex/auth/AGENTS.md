# Codomyrmex Agents — src/codomyrmex/auth

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Authentication and authorization with API key management, OAuth integration, and access control. Provides provider-agnostic auth interface with support for username/password, API key, and token-based authentication.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `api_key_manager.py` – API key generation and validation manager
- `authenticator.py` – User authentication and authorization
- `token.py` – Token management and validation

## Key Classes and Functions

### Authenticator (`authenticator.py`)
- `Authenticator()` – Authenticator for user authentication and authorization
- `authenticate(credentials: dict) -> Optional[Token]` – Authenticate a user with provided credentials (username/password or API key)
- `authorize(token: Token, resource: str, permission: str) -> bool` – Check if a token has permission to access a resource
- `refresh_token(token: Token) -> Optional[Token]` – Refresh an expired or soon-to-expire token
- `revoke_token(token: Token) -> bool` – Revoke a token

### Token (`token.py`)
- `Token` (dataclass) – Authentication token:
  - `token_id: str` – Unique token identifier
  - `user_id: str` – User identifier
  - `permissions: list[str]` – List of permissions
  - `expires_at: Optional[float]` – Expiration timestamp
  - `created_at: float` – Creation timestamp
  - `secret: Optional[str]` – Secret for token signing
- `is_expired() -> bool` – Check if token is expired
- `to_dict() -> dict` – Convert token to dictionary
- `from_dict(data: dict) -> Token` – Create token from dictionary

### TokenManager (`token.py`)
- `TokenManager(secret: Optional[str] = None)` – Manager for token operations
- `create_token(user_id: str, permissions: list[str] = None, ttl: int = 3600) -> Token` – Create a new authentication token
- `validate_token(token: Token) -> bool` – Validate a token's signature and expiration
- `revoke_token(token: Token) -> bool` – Revoke a token
- `refresh_token(token: Token, ttl: int = 3600) -> Optional[Token]` – Refresh an expired or soon-to-expire token

### APIKeyManager (`api_key_manager.py`)
- `APIKeyManager()` – Manager for API key generation and validation
- `generate_api_key(user_id: str, permissions: list[str] = None) -> str` – Generate a new API key for a user
- `validate_api_key(api_key: str) -> Optional[dict]` – Validate an API key and return associated user/permission information
- `revoke_api_key(api_key: str) -> bool` – Revoke an API key

### Module Functions (`__init__.py`)
- `authenticate(credentials: dict) -> Optional[Token]` – Authenticate with credentials
- `authorize(token: Token, resource: str, permission: str) -> bool` – Check authorization
- `get_authenticator() -> Authenticator` – Get an authenticator instance

### Exceptions
- `AuthenticationError` – Raised when authentication operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation