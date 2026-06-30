"""SecretVault: simple encrypted secret storage."""

import base64
import functools
import hashlib
import importlib.util
import json
import os
import string
import sysconfig
from pathlib import Path

from codomyrmex.encryption import AESGCMEncryptor


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
        self._salt: bytes | None = None
        self._master_password: str | None = master_password
        self._derived_key: bytes | None = None

        if master_password:
            self._salt = os.urandom(32)
            self._derived_key = self._derive_key(master_password, self._salt)

        if self.path and self.path.exists() and master_password:
            self._load()

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            iterations=600_000,
        )

    def _encrypt(self, value: str) -> str:
        """Encrypt value using AES-GCM."""
        if not self._derived_key:
            return base64.b64encode(value.encode()).decode()
        encryptor = AESGCMEncryptor(self._derived_key)
        encrypted = encryptor.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt(self, encrypted: str) -> str:
        """Decrypt a value."""
        data = base64.b64decode(encrypted)
        if not self._derived_key:
            return data.decode()
        encryptor = AESGCMEncryptor(self._derived_key)
        return encryptor.decrypt(data).decode()

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
            payload: dict[str, object] = {"secrets": self._secrets}
            if self._salt is not None:
                payload["salt"] = base64.b64encode(self._salt).decode()
            with open(self.path, "w") as f:
                json.dump(payload, f)

    def _load(self) -> None:
        """Load vault from disk."""
        if self.path and self.path.exists():
            with open(self.path) as f:
                data = json.load(f)
            if isinstance(data, dict) and "secrets" in data:
                if "salt" in data and self._master_password:
                    self._salt = base64.b64decode(data["salt"])
                    self._derived_key = self._derive_key(
                        self._master_password, self._salt
                    )
                self._secrets = data["secrets"]
            else:
                self._secrets = data


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


@functools.lru_cache(maxsize=1)
def _stdlib_secrets_module():
    """Load CPython stdlib ``secrets`` without touching ``sys.modules['secrets']``.

    Mutating ``sys.modules['secrets']`` (pop/restore) breaks later
    ``from secrets import randbits`` in NumPy's ``random.bit_generator`` and
    anything else that expects the real stdlib module to stay registered.
    """
    path = Path(sysconfig.get_path("stdlib")) / "secrets.py"
    if not path.is_file():
        raise RuntimeError(f"stdlib secrets module not found at {path}")
    name = "_codomyrmex_vault_stdlib_secrets"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load stdlib secrets module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate_secret(length: int = 32, include_special: bool = True) -> str:
    """Generate a random secret."""
    _secrets = _stdlib_secrets_module()
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += "!@#$%^&*"

    return "".join(_secrets.choice(chars) for _ in range(length))
