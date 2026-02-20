"""MCP tools for the crypto module."""

from typing import Any, Dict, Optional

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="crypto")
def hash_data(
    data: str,
    algorithm: str = "sha256",
) -> dict:
    """Compute a cryptographic hash of the input data.

    Args:
        data: String data to hash
        algorithm: Hash algorithm ('sha256', 'sha384', 'sha512', 'sha3_256', 'blake2b')

    Returns:
        Dictionary with the hex digest and algorithm used.
    """
    import hashlib

    try:
        if algorithm not in {"sha256", "sha384", "sha512", "sha3_256", "blake2b"}:
            return {"status": "error", "message": f"Unsupported algorithm: {algorithm}"}

        h = hashlib.new(algorithm)
        h.update(data.encode("utf-8"))
        return {
            "status": "success",
            "algorithm": algorithm,
            "digest": h.hexdigest(),
            "digest_length": h.digest_size * 2,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="crypto")
def verify_hash(
    data: str,
    expected_hash: str,
    algorithm: str = "sha256",
) -> dict:
    """Verify that data matches an expected hash.

    Args:
        data: String data to verify
        expected_hash: Expected hex digest
        algorithm: Hash algorithm used for the expected hash

    Returns:
        Dictionary indicating whether the hash matches.
    """
    import hashlib
    import hmac

    try:
        h = hashlib.new(algorithm)
        h.update(data.encode("utf-8"))
        actual = h.hexdigest()
        # Constant-time comparison to prevent timing attacks
        match = hmac.compare_digest(actual, expected_hash)
        return {
            "status": "success",
            "match": match,
            "algorithm": algorithm,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="crypto")
def generate_key(
    algorithm: str = "aes256",
    encoding: str = "hex",
) -> dict:
    """Generate a cryptographic key.

    Args:
        algorithm: Key type ('aes128', 'aes256', 'hmac256')
        encoding: Output encoding ('hex', 'base64')

    Returns:
        Dictionary with the generated key material.
    """
    import base64
    import secrets

    try:
        key_sizes = {"aes128": 16, "aes256": 32, "hmac256": 32}
        size = key_sizes.get(algorithm)
        if size is None:
            return {"status": "error", "message": f"Unsupported algorithm: {algorithm}"}

        key_bytes = secrets.token_bytes(size)
        if encoding == "base64":
            key_str = base64.b64encode(key_bytes).decode("ascii")
        else:
            key_str = key_bytes.hex()

        return {
            "status": "success",
            "algorithm": algorithm,
            "encoding": encoding,
            "key": key_str,
            "key_bits": size * 8,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
