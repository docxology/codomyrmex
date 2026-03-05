"""
Authentication and authorization module.
"""

from __future__ import annotations

import threading
from typing import Any

from codomyrmex.auth.providers.api_key_manager import APIKeyManager
from codomyrmex.auth.rbac.permissions import PermissionRegistry
from codomyrmex.auth.tokens.token import Token, TokenManager
from codomyrmex.exceptions import AuthenticationError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class Authenticator:
    """Authenticator for user authentication and authorization.

    This class serves as the main orchestrator for authentication and authorization.
    It manages users, tokens, API keys, and RBAC permissions.
    """

    _instance: Authenticator | None = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensures Authenticator is a singleton to maintain shared state across imports."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        """Initialize authenticator."""
        if getattr(self, "_initialized", False):
            return

        self.token_manager = TokenManager()
        self.api_key_manager = APIKeyManager()
        self.permissions = PermissionRegistry()
        # User database for demonstration purposes
        self._users: dict[str, dict[str, Any]] = {}
        self._initialized = True
        logger.debug("Authenticator initialized")

    def register_user(
        self, username: str, password: str, roles: list[str] | None = None
    ) -> bool:
        """Register a new user.

        Args:
            username: Unique username
            password: Password (plaintext for demonstration, should be hashed in production)
            roles: Initial roles to assign

        Returns:
            True if registration was successful, False if username exists
        """
        if username in self._users:
            logger.warning(
                "User registration failed: username '%s' already exists", username
            )
            return False

        self._users[username] = {"password": password, "roles": roles or ["default"]}

        # Register user in RBAC
        for role in roles or ["default"]:
            self.permissions.assign_role(username, role)

        logger.info("User registered: %s", username)
        return True

    def authenticate(self, credentials: dict[str, Any]) -> Token | None:
        """Authenticate a user with provided credentials.

        Args:
            credentials: User credentials (username/password, api_key, etc.)

        Returns:
            Authentication token if successful, None otherwise

        Raises:
            AuthenticationError: If an error occurs during authentication
        """
        try:
            # 1. Check for API key authentication
            if "api_key" in credentials:
                api_key_str = credentials["api_key"]
                api_key_info = self.api_key_manager.validate(api_key_str)
                if api_key_info:
                    logger.info(
                        "Authenticated via API key for user: %s", api_key_info.user_id
                    )
                    return self.token_manager.create_token(
                        user_id=api_key_info.user_id,
                        permissions=api_key_info.permissions,
                    )

            # 2. Check for username/password authentication
            if "username" in credentials and "password" in credentials:
                username = credentials["username"]
                password = credentials["password"]
                if self._validate_password(username, password):
                    # Get user's effective permissions from RBAC
                    user_permissions = list(
                        self.permissions.get_user_permissions(username)
                    )
                    logger.info("Authenticated via password for user: %s", username)
                    return self.token_manager.create_token(
                        user_id=username, permissions=user_permissions
                    )

            logger.warning("Authentication failed: invalid credentials")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError(f"Authentication failed: {e!s}") from e

    def authorize(self, token: Token | str, resource: str, permission: str) -> bool:
        """Check if a token has permission to access a resource.

        Args:
            token: Authentication token object or signed string
            resource: Resource identifier
            permission: Permission type (e.g., "read", "write", "data.read")

        Returns:
            True if authorized, False otherwise
        """
        # If token is a string, we need to convert it or validate it
        if isinstance(token, str):
            # Try to find the token object in the manager
            valid = self.token_manager.validate_token(token)
            if not valid:
                return False
            # Extract data from the string to get user_id
            data = self.token_manager.validator.validate_signed_token(token)
            if not data:
                return False
            user_id = data.get("user_id")
            token_permissions = data.get("permissions", [])
        else:
            if not self.token_manager.validate_token(token):
                return False
            user_id = token.user_id
            token_permissions = token.permissions

        # 1. Check direct permissions from token
        if "admin" in token_permissions or permission in token_permissions:
            return True

        # 2. Check wildcard permissions from token
        for tp in token_permissions:
            if tp.endswith(".*") and permission.startswith(tp[:-1]):
                return True
            if tp == "*":
                return True

        # 3. Check RBAC (allows dynamic updates to permissions without re-issuing tokens)
        if self.permissions.check(user_id, permission, resource):
            return True

        logger.warning(
            "Authorization failed for user '%s' on resource '%s' with permission '%s'",
            user_id,
            resource,
            permission,
        )
        return False

    def refresh_token(self, token: Token) -> Token | None:
        """Refresh an authentication token."""
        return self.token_manager.refresh_token(token)

    def revoke_token(self, token: Token | str) -> bool:
        """Revoke a token."""
        return self.token_manager.revoke_token(token)

    def _validate_password(self, username: str, password: str) -> bool:
        """Validate username and password."""
        user = self._users.get(username)
        return bool(user and user.get("password") == password)
