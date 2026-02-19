# Auth Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `auth` module handles authentication and authorization within Codomyrmex. It manages API keys, token generation, and permissions checks.

## 2. Core Components

### 2.1 Main Interface
- **`authenticate(credentials: dict) -> Optional[Token]`**: Verify credentials and issue a token.
- **`authorize(token: Token, resource: str, permission: str) -> bool`**: Check if a token allows a specific action.
- **`get_authenticator() -> Authenticator`**: Get the main authenticator instance.

### 2.2 Classes
- **`Authenticator`**: Central logic for auth flows.
- **`Token`**: Data structure representing an authenticated session.
- **`TokenManager`**: Handles token lifecycle and validation.
- **`APIKeyManager`**: CRUD operations for API keys.

## 3. Exceptions
- **`AuthenticationError`**: Raised on login failure or invalid token.

## 4. Usage Example

```python
from codomyrmex.auth import authenticate, authorize

# Login
token = authenticate({"api_key": "sk_12345"})

# Check permission
if authorize(token, "database", "read"):
    print("Access granted")
```
