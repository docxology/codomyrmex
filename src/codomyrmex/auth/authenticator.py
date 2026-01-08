"""
Authentication and authorization.
"""

from typing import Optional

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

from .api_key_manager import APIKeyManager
from .token import Token, TokenManager

logger = get_logger(__name__)


class AuthenticationError(CodomyrmexError):
    """Raised when authentication fails."""

    pass


class Authenticator:
    """Authenticator for user authentication and authorization."""

    def __init__(self):
        """Initialize authenticator."""
        self.token_manager = TokenManager()
        self.api_key_manager = APIKeyManager()
        # In a real implementation, this would connect to a user database
        self._users: dict[str, dict] = {}

    def authenticate(self, credentials: dict) -> Optional[Token]:
        """Authenticate a user with provided credentials.

        Args:
            credentials: User credentials (username/password, API key, etc.)

        Returns:
            Authentication token if successful, None otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Check for API key authentication
            if "api_key" in credentials:
                api_key = credentials["api_key"]
                user_info = self.api_key_manager.validate_api_key(api_key)
                if user_info:
                    return self.token_manager.create_token(
                        user_id=user_info["user_id"],
                        permissions=user_info.get("permissions", [])
                    )

            # Check for username/password authentication
            if "username" in credentials and "password" in credentials:
                username = credentials["username"]
                password = credentials["password"]
                if self._validate_password(username, password):
                    return self.token_manager.create_token(
                        user_id=username,
                        permissions=["read", "write"]  # Default permissions
                    )

            logger.warning("Authentication failed: invalid credentials")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError(f"Authentication failed: {str(e)}") from e

    def authorize(self, token: Token, resource: str, permission: str) -> bool:
        """Check if a token has permission to access a resource.

        Args:
            token: Authentication token
            resource: Resource identifier
            permission: Permission type (read, write, execute, etc.)

        Returns:
            True if authorized, False otherwise
        """
        if not self.token_manager.validate_token(token):
            return False

        # Check if token has the required permission
        if permission in token.permissions or "admin" in token.permissions:
            return True

        return False

    def refresh_token(self, token: Token) -> Optional[Token]:
        """Refresh an expired or soon-to-expire token.

        Args:
            token: Current authentication token

        Returns:
            New token if refresh successful, None otherwise
        """
        return self.token_manager.refresh_token(token)

    def revoke_token(self, token: Token) -> bool:
        """Revoke a token.

        Args:
            token: Token to revoke

        Returns:
            True if revocation successful
        """
        return self.token_manager.revoke_token(token)

    def _validate_password(self, username: str, password: str) -> bool:
        """Validate username and password.

        Args:
            username: Username
            password: Password

        Returns:
            True if valid
        """
        # In a real implementation, this would check against a user database
        # For now, this is a placeholder
        return username in self._users and self._users[username].get("password") == password


