import hashlib
import hmac

from .models import SignatureAlgorithm


class WebhookSignature:
    """Utility for signing and verifying webhook payloads using HMAC.

    All methods are static so that signing/verification can be performed
    without instantiation.
    """

    _ALGORITHM_MAP: dict[SignatureAlgorithm, str] = {
        SignatureAlgorithm.HMAC_SHA256: "sha256",
        SignatureAlgorithm.HMAC_SHA512: "sha512",
    }

    @staticmethod
    def sign(
        payload: str,
        secret: str,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
    ) -> str:
        """Create an HMAC signature for the given payload.

        Args:
            payload: The string payload to sign.
            secret: The shared secret key.
            algorithm: The HMAC algorithm to use.

        Returns:
            Hex-encoded HMAC signature string.
        """
        hash_func = WebhookSignature._ALGORITHM_MAP[algorithm]
        return hmac.new(
            key=secret.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=getattr(hashlib, hash_func),
        ).hexdigest()

    @staticmethod
    def verify(
        payload: str,
        secret: str,
        signature: str,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
    ) -> bool:
        """Verify an HMAC signature against a payload.

        Uses constant-time comparison to prevent timing attacks.

        Args:
            payload: The string payload that was signed.
            secret: The shared secret key.
            signature: The signature to verify against.
            algorithm: The HMAC algorithm that was used for signing.

        Returns:
            ``True`` if the signature is valid, ``False`` otherwise.
        """
        expected = WebhookSignature.sign(payload, secret, algorithm)
        return hmac.compare_digest(expected, signature)


