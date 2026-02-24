"""
API authentication utilities.

Provides authentication mechanisms for API endpoints.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from collections.abc import Callable


class AuthType(Enum):
    """Types of authentication."""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    HMAC = "hmac"
    JWT = "jwt"


@dataclass
class AuthCredentials:
    """Authentication credentials."""
    auth_type: AuthType
    identifier: str  # username, client_id, api_key_id
    secret: str      # password, client_secret, api_key
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthResult:
    """Result of authentication attempt."""
    authenticated: bool
    identity: str | None = None
    roles: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)
    expires_at: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "authenticated": self.authenticated,
            "identity": self.identity,
            "roles": self.roles,
            "scopes": self.scopes,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "error": self.error,
        }


class Authenticator(ABC):
    """Abstract base class for authenticators."""

    auth_type: AuthType

    @abstractmethod
    def authenticate(self, request: dict[str, Any]) -> AuthResult:
        """Authenticate a request."""
        pass


class APIKeyAuthenticator(Authenticator):
    """API key based authentication."""

    auth_type = AuthType.API_KEY

    def __init__(
        self,
        header_name: str = "X-API-Key",
        query_param: str | None = None,
    ):
        """Execute   Init   operations natively."""
        self.header_name = header_name
        self.query_param = query_param
        self._keys: dict[str, dict[str, Any]] = {}

    def register_key(
        self,
        key: str,
        identity: str,
        scopes: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> None:
        """Register an API key."""
        self._keys[key] = {
            "identity": identity,
            "scopes": scopes or [],
            "expires_at": expires_at,
            "created_at": datetime.now(),
        }

    def revoke_key(self, key: str) -> None:
        """Revoke an API key."""
        if key in self._keys:
            del self._keys[key]

    def authenticate(self, request: dict[str, Any]) -> AuthResult:
        """Execute Authenticate operations natively."""
        # Extract API key
        headers = request.get("headers", {})
        query = request.get("query", {})

        api_key = headers.get(self.header_name)
        if not api_key and self.query_param:
            api_key = query.get(self.query_param)

        if not api_key:
            return AuthResult(
                authenticated=False,
                error="API key not provided",
            )

        # Validate key
        key_data = self._keys.get(api_key)
        if not key_data:
            return AuthResult(
                authenticated=False,
                error="Invalid API key",
            )

        # Check expiration
        if key_data.get("expires_at"):
            if datetime.now() > key_data["expires_at"]:
                return AuthResult(
                    authenticated=False,
                    error="API key expired",
                )

        return AuthResult(
            authenticated=True,
            identity=key_data["identity"],
            scopes=key_data.get("scopes", []),
            expires_at=key_data.get("expires_at"),
        )

    @staticmethod
    def generate_key(prefix: str = "sk") -> str:
        """Generate a new API key."""
        random_part = secrets.token_hex(24)
        return f"{prefix}_{random_part}"


class BearerTokenAuthenticator(Authenticator):
    """Bearer token authentication."""

    auth_type = AuthType.BEARER_TOKEN

    def __init__(self, validator: Callable[[str], dict | None] | None = None):
        """Execute   Init   operations natively."""
        self._tokens: dict[str, dict[str, Any]] = {}
        self._validator = validator

    def create_token(
        self,
        identity: str,
        scopes: list[str] | None = None,
        ttl_seconds: int = 3600,
    ) -> str:
        """Create a new bearer token."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

        self._tokens[token] = {
            "identity": identity,
            "scopes": scopes or [],
            "expires_at": expires_at,
        }

        return token

    def authenticate(self, request: dict[str, Any]) -> AuthResult:
        """Execute Authenticate operations natively."""
        headers = request.get("headers", {})
        auth_header = headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return AuthResult(
                authenticated=False,
                error="Bearer token not provided",
            )

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Use custom validator if provided
        if self._validator:
            result = self._validator(token)
            if result:
                return AuthResult(
                    authenticated=True,
                    identity=result.get("identity"),
                    scopes=result.get("scopes", []),
                )

        # Check token store
        token_data = self._tokens.get(token)
        if not token_data:
            return AuthResult(
                authenticated=False,
                error="Invalid token",
            )

        if datetime.now() > token_data["expires_at"]:
            del self._tokens[token]
            return AuthResult(
                authenticated=False,
                error="Token expired",
            )

        return AuthResult(
            authenticated=True,
            identity=token_data["identity"],
            scopes=token_data.get("scopes", []),
            expires_at=token_data["expires_at"],
        )


class BasicAuthenticator(Authenticator):
    """HTTP Basic authentication."""

    auth_type = AuthType.BASIC_AUTH

    def __init__(self):
        """Execute   Init   operations natively."""
        self._users: dict[str, dict[str, Any]] = {}

    def register_user(
        self,
        username: str,
        password: str,
        roles: list[str] | None = None,
    ) -> None:
        """Register a user."""
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self._users[username] = {
            "password_hash": password_hash,
            "roles": roles or [],
        }

    def authenticate(self, request: dict[str, Any]) -> AuthResult:
        """Execute Authenticate operations natively."""
        headers = request.get("headers", {})
        auth_header = headers.get("Authorization", "")

        if not auth_header.startswith("Basic "):
            return AuthResult(
                authenticated=False,
                error="Basic auth not provided",
            )

        try:
            encoded = auth_header[6:]  # Remove "Basic " prefix
            decoded = base64.b64decode(encoded).decode('utf-8')
            username, password = decoded.split(':', 1)
        except Exception:
            return AuthResult(
                authenticated=False,
                error="Invalid Basic auth format",
            )

        user = self._users.get(username)
        if not user:
            return AuthResult(
                authenticated=False,
                error="User not found",
            )

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user["password_hash"]:
            return AuthResult(
                authenticated=False,
                error="Invalid password",
            )

        return AuthResult(
            authenticated=True,
            identity=username,
            roles=user.get("roles", []),
        )


class HMACAuthenticator(Authenticator):
    """HMAC signature authentication."""

    auth_type = AuthType.HMAC

    def __init__(
        self,
        signature_header: str = "X-Signature",
        timestamp_header: str = "X-Timestamp",
        max_age_seconds: int = 300,
    ):
        """Execute   Init   operations natively."""
        self.signature_header = signature_header
        self.timestamp_header = timestamp_header
        self.max_age_seconds = max_age_seconds
        self._secrets: dict[str, dict[str, Any]] = {}

    def register_client(
        self,
        client_id: str,
        secret: str,
        scopes: list[str] | None = None,
    ) -> None:
        """Register a client."""
        self._secrets[client_id] = {
            "secret": secret,
            "scopes": scopes or [],
        }

    def sign_request(
        self,
        client_id: str,
        body: str,
        timestamp: int | None = None,
    ) -> str:
        """Generate signature for a request."""
        client = self._secrets.get(client_id)
        if not client:
            raise ValueError(f"Unknown client: {client_id}")

        ts = timestamp or int(time.time())
        message = f"{ts}:{body}"

        signature = hmac.new(
            client["secret"].encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def authenticate(self, request: dict[str, Any]) -> AuthResult:
        """Execute Authenticate operations natively."""
        headers = request.get("headers", {})
        signature = headers.get(self.signature_header)
        timestamp_str = headers.get(self.timestamp_header)
        client_id = headers.get("X-Client-ID")
        body = request.get("body", "")

        if not all([signature, timestamp_str, client_id]):
            return AuthResult(
                authenticated=False,
                error="Missing authentication headers",
            )

        try:
            timestamp = int(timestamp_str)
        except ValueError:
            return AuthResult(
                authenticated=False,
                error="Invalid timestamp",
            )

        # Check timestamp age
        age = abs(int(time.time()) - timestamp)
        if age > self.max_age_seconds:
            return AuthResult(
                authenticated=False,
                error="Request too old",
            )

        client = self._secrets.get(client_id)
        if not client:
            return AuthResult(
                authenticated=False,
                error="Unknown client",
            )

        # Verify signature
        expected = self.sign_request(client_id, body, timestamp)
        if not hmac.compare_digest(signature, expected):
            return AuthResult(
                authenticated=False,
                error="Invalid signature",
            )

        return AuthResult(
            authenticated=True,
            identity=client_id,
            scopes=client.get("scopes", []),
        )


def create_authenticator(
    auth_type: AuthType,
    **kwargs
) -> Authenticator:
    """Factory function for authenticators."""
    authenticators = {
        AuthType.API_KEY: APIKeyAuthenticator,
        AuthType.BEARER_TOKEN: BearerTokenAuthenticator,
        AuthType.BASIC_AUTH: BasicAuthenticator,
        AuthType.HMAC: HMACAuthenticator,
    }

    auth_class = authenticators.get(auth_type)
    if not auth_class:
        raise ValueError(f"Unsupported auth type: {auth_type}")

    return auth_class(**kwargs)


__all__ = [
    "AuthType",
    "AuthCredentials",
    "AuthResult",
    "Authenticator",
    "APIKeyAuthenticator",
    "BearerTokenAuthenticator",
    "BasicAuthenticator",
    "HMACAuthenticator",
    "create_authenticator",
]
