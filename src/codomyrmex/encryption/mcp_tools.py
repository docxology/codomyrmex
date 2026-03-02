"""MCP tools for the encryption module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="encryption")
def encryption_encrypt(
    data: str,
    encoding: str = "utf-8",
) -> dict:
    """Encrypt a string using AES-GCM with a freshly generated key.

    Generates a new AES-256-GCM key, encrypts the provided data, and
    returns both the ciphertext and the key (both hex-encoded).

    Args:
        data: Plaintext string to encrypt.
        encoding: Character encoding for the input string (default: utf-8).

    Returns:
        Dictionary with hex-encoded ciphertext and key.
    """
    try:
        import base64

        from codomyrmex.encryption import AESGCMEncryptor, generate_aes_key

        key = generate_aes_key()
        encryptor = AESGCMEncryptor(key)
        ciphertext = encryptor.encrypt(data.encode(encoding))

        return {
            "status": "success",
            "algorithm": "AES-256-GCM",
            "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
            "key_hex": key.hex(),
            "key_bits": len(key) * 8,
            "plaintext_length": len(data),
        }
    except ImportError:
        return {
            "status": "error",
            "message": "cryptography package not installed. Run: uv sync --extra encryption",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="encryption")
def encryption_generate_key(
    algorithm: str = "aes256",
) -> dict:
    """Generate a cryptographic key for the specified algorithm.

    Args:
        algorithm: Key type to generate ('aes128', 'aes256').

    Returns:
        Dictionary with the hex-encoded key and metadata.
    """
    try:
        from codomyrmex.encryption import generate_aes_key

        key_sizes = {"aes128": 16, "aes256": 32}
        size = key_sizes.get(algorithm)
        if size is None:
            return {
                "status": "error",
                "message": f"Unsupported algorithm: {algorithm!r}. Use: {list(key_sizes)}",
            }

        # generate_aes_key always produces 32 bytes; for aes128 use secrets directly
        if algorithm == "aes256":
            key = generate_aes_key()
        else:
            import secrets
            key = secrets.token_bytes(size)

        return {
            "status": "success",
            "algorithm": algorithm,
            "key_hex": key.hex(),
            "key_bits": len(key) * 8,
        }
    except ImportError:
        return {
            "status": "error",
            "message": "cryptography package not installed. Run: uv sync --extra encryption",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
