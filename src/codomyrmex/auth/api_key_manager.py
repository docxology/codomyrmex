from typing import Optional

import hashlib
import secrets

from codomyrmex.logging_monitoring.logger_config import get_logger




























"""
API key management.
"""



logger = get_logger(__name__)


class APIKeyManager:
    """Manager for API key generation and validation."""

    def __init__(self):
        """Initialize API key manager."""
        # In a real implementation, this would use a database
        self._api_keys: dict[str, dict] = {}

    def generate_api_key(self, user_id: str, permissions: list[str] = None) -> str:
        """Generate a new API key for a user.

        Args:
            user_id: User identifier
            permissions: Optional list of permissions

        Returns:
            Generated API key
        """
        api_key = f"codomyrmex_{secrets.token_urlsafe(32)}"
        self._api_keys[api_key] = {
            "user_id": user_id,
            "permissions": permissions or ["read"],
        }
        logger.info(f"Generated API key for user: {user_id}")
        return api_key

    def validate_api_key(self, api_key: str) -> Optional[dict]:
        """Validate an API key and return associated user/permission information.

        Args:
            api_key: API key to validate

        Returns:
            User/permission info if valid, None otherwise
        """
        return self._api_keys.get(api_key)

    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key.

        Args:
            api_key: API key to revoke

        Returns:
            True if revocation successful
        """
        if api_key in self._api_keys:
            del self._api_keys[api_key]
            logger.info(f"Revoked API key: {api_key[:20]}...")
            return True
        return False


