"""Token validation and signature verification."""

import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class TokenValidator:
    """Validates tokens and their signatures.

    Uses HMAC-SHA256 to sign and verify token payloads.
    Provides a base64 encoded string format for tokens.
    """

    def __init__(self, secret: str):
        """Initialize validator.

        Args:
            secret: Secret key for signing.
        """
        if not secret:
            raise ValueError("Secret key cannot be empty")
        self.secret = secret.encode()

    def _generate_signature(self, payload_dict: dict[str, Any]) -> str:
        """Generate a signature for a payload.

        Sorts keys to ensure consistent signature for the same dictionary content.
        """
        payload_json = json.dumps(payload_dict, sort_keys=True).encode()
        signature = hmac.new(self.secret, payload_json, hashlib.sha256).hexdigest()
        return signature

    def sign_token_data(self, token_data: dict[str, Any]) -> str:
        """Add a signature to token data and return as a base64 string.

        Args:
            token_data: Payload to sign.

        Returns:
            Base64 encoded string containing data and signature.
        """
        signature = self._generate_signature(token_data)
        full_token = {
            "data": token_data,
            "signature": signature
        }
        token_bytes = json.dumps(full_token).encode()
        return base64.b64encode(token_bytes).decode()

    def validate_signed_token(self, token_str: str) -> dict[str, Any] | None:
        """Validate a base64 encoded signed token.

        Checks:
        1. Base64 format and JSON structure.
        2. HMAC signature validity.
        3. Expiration if present.

        Args:
            token_str: Signed token string.

        Returns:
            Payload dictionary if valid, None otherwise.
        """
        try:
            token_bytes = base64.b64decode(token_str)
            token_json = json.loads(token_bytes)

            data = token_json.get("data")
            signature = token_json.get("signature")

            if data is None or signature is None:
                logger.warning("Token structure invalid: missing data or signature")
                return None

            # Verify signature
            expected_signature = self._generate_signature(data)
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Token signature mismatch")
                return None

            # Verify expiration
            expires_at = data.get("expires_at")
            if expires_at is not None and time.time() > expires_at:
                logger.warning("Token expired at %s", expires_at)
                return None

            return data
        except binascii.Error:
            logger.error("Token validation error: Invalid base64")
            return None
        except json.JSONDecodeError:
            logger.error("Token validation error: Invalid JSON")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
