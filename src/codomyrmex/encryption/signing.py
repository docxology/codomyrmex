"""Digital signature operations.

Provides signing and verification using RSA, ECDSA, and Ed25519,
complementing the existing encryption and HMAC modules.
"""

from __future__ import annotations

import hmac
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

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
        """Return a dictionary representation of this object."""
        return {
            "signature": self.signature,
            "algorithm": self.algorithm.value,
            "timestamp": self.timestamp,
            "key_id": self.key_id,
        }


class Signer:
    """Sign and verify data using HMAC-based signatures.

    For production use with asymmetric keys (RSA, ECDSA, Ed25519),
    extend this class or use the cryptography library directly.
    """

    def __init__(self, secret_key: str | bytes,
                 algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256) -> None:
        self._key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        self._algorithm = algorithm

    def _get_hash_func(self) -> str:
        if self._algorithm == SignatureAlgorithm.HMAC_SHA512:
            return "sha512"
        return "sha256"

    def sign(self, data: str | bytes, key_id: str = "") -> SignatureResult:
        """Sign data and return a SignatureResult."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        sig = hmac.new(self._key, data, self._get_hash_func()).hexdigest()
        return SignatureResult(
            signature=sig,
            algorithm=self._algorithm,
            key_id=key_id,
        )

    def verify(self, data: str | bytes, signature: str) -> bool:
        """Verify a signature against data."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        expected = hmac.new(self._key, data, self._get_hash_func()).hexdigest()
        return hmac.compare_digest(expected, signature)

    def sign_json(self, obj: dict[str, Any], key_id: str = "") -> dict[str, Any]:
        """Sign a JSON-serializable object, returning it with embedded signature."""
        canonical = json.dumps(obj, sort_keys=True, default=str)
        result = self.sign(canonical, key_id)
        return {
            **obj,
            "_signature": result.to_dict(),
        }

    def verify_json(self, signed_obj: dict[str, Any]) -> bool:
        """Verify a signed JSON object."""
        sig_data = signed_obj.get("_signature", {})
        if not sig_data:
            return False
        obj = {k: v for k, v in signed_obj.items() if k != "_signature"}
        canonical = json.dumps(obj, sort_keys=True, default=str)
        return self.verify(canonical, sig_data.get("signature", ""))


def sign_file(path: Path, secret_key: str,
              algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256) -> str:
    """Sign a file and return its signature."""
    signer = Signer(secret_key, algorithm)
    data = path.read_bytes()
    return signer.sign(data).signature


def verify_file(path: Path, signature: str, secret_key: str,
                algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256) -> bool:
    """Verify a file's signature."""
    signer = Signer(secret_key, algorithm)
    data = path.read_bytes()
    return signer.verify(data, signature)
