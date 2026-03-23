"""SecretVault: simple encrypted secret storage."""

import base64
import hashlib
import json
import os
import string
import sys
from pathlib import Path


class SecretVault:
    """
    Simple encrypted secret storage.

    Usage:
        vault = SecretVault("secrets.vault", "master_password")
        vault.set("api_key", "my-secret-key")
        api_key = vault.get("api_key")
        vault.save()
    """

    def __init__(self, path: str | None = None, master_password: str | None = None):
        self.path = Path(path) if path else None
        self._secrets: dict[str, str] = {}
        self._key = self._derive_key(master_password) if master_password else None

        if self.path and self.path.exists() and self._key:
            self._load()

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            b"codomyrmex-vault-salt",
            iterations=600_000,
        )

    def _encrypt(self, value: str) -> str:
        """Simple XOR encryption (use proper encryption in production)."""
        if not self._key:
            return base64.b64encode(value.encode()).decode()
        key = self._key
        encrypted = bytes(c ^ key[i % len(key)] for i, c in enumerate(value.encode()))
        return base64.b64encode(encrypted).decode()

    def _decrypt(self, encrypted: str) -> str:
        """Decrypt a value."""
        data = base64.b64decode(encrypted)
        if not self._key:
            return data.decode()
        key = self._key
        decrypted = bytes(c ^ key[i % len(key)] for i, c in enumerate(data))
        return decrypted.decode()

    def set(self, name: str, value: str) -> None:
        """Store a secret."""
        self._secrets[name] = self._encrypt(value)

    def get(self, name: str, default: str | None = None) -> str | None:
        """Retrieve a secret."""
        if name not in self._secrets:
            return default
        return self._decrypt(self._secrets[name])

    def delete(self, name: str) -> bool:
        """Delete a secret."""
        if name in self._secrets:
            del self._secrets[name]
            return True
        return False

    def list_names(self) -> list[str]:
        """list all secret names."""
        return list(self._secrets.keys())

    def save(self) -> None:
        """Save vault to disk."""
        if self.path:
            with open(self.path, "w") as f:
                json.dump(self._secrets, f)

    def _load(self) -> None:
        """Load vault from disk."""
        if self.path and self.path.exists():
            with open(self.path) as f:
                self._secrets = json.load(f)


def get_secret_from_env(name: str, default: str | None = None) -> str | None:
    """Get a secret from environment variables."""
    return os.environ.get(name, default)


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret for display."""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return (
        value[:show_chars] + "*" * (len(value) - show_chars * 2) + value[-show_chars:]
    )


def generate_secret(length: int = 32, include_special: bool = True) -> str:
    """Generate a random secret."""
    # The stdlib 'secrets' module is shadowed by this package
    # (codomyrmex.security.secrets). Temporarily remove our package from
    # sys.modules so importlib resolves to the stdlib module.
    our_module = sys.modules.pop("secrets", None)
    try:
        import secrets as _stdlib_secrets
    finally:
        if our_module is not None:
            sys.modules["secrets"] = our_module

    chars = string.ascii_letters + string.digits
    if include_special:
        chars += "!@#$%^&*"

    return "".join(_stdlib_secrets.choice(chars) for _ in range(length))
