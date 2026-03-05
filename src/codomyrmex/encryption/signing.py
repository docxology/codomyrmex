"""Digital signature operations.

Provides signing and verification using HMAC for fast, simple JSON and file
signing, complementing the existing RSA signature module.
"""

from __future__ import annotations

import hmac
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class SignatureAlgorithm(Enum):
    """Supported signature algorithms."""

    HMAC_SHA256 = "hmac-sha256"
    HMAC_SHA512 = "hmac-sha512"


@dataclass
class SignatureResult:
    """Result of a signing operation."""

    signature: str
    algorithm: SignatureAlgorithm
    timestamp: float = field(default_factory=time.time)
    key_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this result."""
        return {
            "signature": self.signature,
            "algorithm": self.algorithm.value,
            "timestamp": self.timestamp,
            "key_id": self.key_id,
        }


class Signer:
    """Sign and verify data using HMAC-based signatures.

    Useful for ensuring message integrity and authenticity with symmetric keys.
    """

    def __init__(
        self,
        secret_key: str | bytes,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
    ) -> None:
        """Initialize signer.

        Args:
            secret_key: Shared secret key for HMAC.
            algorithm: HMAC algorithm to use.
        """
        self._key = (
            secret_key.encode("utf-8") if isinstance(secret_key, str) else secret_key
        )
        self._algorithm = algorithm

    def _get_hash_func(self) -> str:
        """Return hash function name for hmac."""
        if self._algorithm == SignatureAlgorithm.HMAC_SHA512:
            return "sha512"
        return "sha256"

    def sign(self, data: str | bytes, key_id: str = "") -> SignatureResult:
        """Sign data using HMAC.

        Args:
            data: Raw bytes or string to sign.
            key_id: Optional key identifier to include in result.

        Returns:
            SignatureResult containing hex signature and metadata.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        sig = hmac.new(self._key, data, self._get_hash_func()).hexdigest()
        return SignatureResult(
            signature=sig,
            algorithm=self._algorithm,
            key_id=key_id,
        )

    def verify(self, data: str | bytes, signature: str) -> bool:
        """Verify an HMAC signature using constant-time comparison.

        Args:
            data: Data to verify signature against.
            signature: Hex signature to check.

        Returns:
            True if signature matches, False otherwise.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        expected = hmac.new(self._key, data, self._get_hash_func()).hexdigest()
        return hmac.compare_digest(expected, signature)

    def sign_json(self, obj: dict[str, Any], key_id: str = "") -> dict[str, Any]:
        """Sign a JSON object and return it with an embedded signature field.

        Args:
            obj: Dictionary to sign.
            key_id: Optional key identifier.

        Returns:
            The original dictionary plus a `_signature` field.
        """
        canonical = json.dumps(obj, sort_keys=True, default=str)
        result = self.sign(canonical, key_id)
        return {
            **obj,
            "_signature": result.to_dict(),
        }

    def verify_json(self, signed_obj: dict[str, Any]) -> bool:
        """Verify a signed JSON object's embedded signature.

        Args:
            signed_obj: Object with a `_signature` field.

        Returns:
            True if the signature is valid, False otherwise.
        """
        sig_data = signed_obj.get("_signature")
        if not sig_data or not isinstance(sig_data, dict):
            return False

        signature = sig_data.get("signature")
        if not signature:
            return False

        # Exclude _signature for canonicalization
        obj = {k: v for k, v in signed_obj.items() if k != "_signature"}
        canonical = json.dumps(obj, sort_keys=True, default=str)
        return self.verify(canonical, signature)


def sign_file(
    path: str | Path,
    secret_key: str | bytes,
    algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
) -> str:
    """Sign a file and return its hex signature string.

    Args:
        path: Path to file.
        secret_key: Secret key.
        algorithm: HMAC algorithm.

    Returns:
        Hexadecimal signature string.
    """
    signer = Signer(secret_key, algorithm)
    data = Path(path).read_bytes()
    return signer.sign(data).signature


def verify_file(
    path: str | Path,
    signature: str,
    secret_key: str | bytes,
    algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
) -> bool:
    """Verify a file's signature.

    Args:
        path: Path to file.
        signature: Hex signature string.
        secret_key: Secret key.
        algorithm: HMAC algorithm.

    Returns:
        True if valid.
    """
    signer = Signer(secret_key, algorithm)
    data = Path(path).read_bytes()
    return signer.verify(data, signature)
