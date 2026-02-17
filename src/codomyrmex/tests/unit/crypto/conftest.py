"""Shared fixtures for crypto module tests."""

import os
import pytest


@pytest.fixture
def symmetric_key():
    """32-byte AES key for testing."""
    return os.urandom(32)


@pytest.fixture
def sample_plaintext():
    """Standard test plaintext bytes."""
    return b"The quick brown fox jumps over the lazy dog"


@pytest.fixture
def rsa_keypair():
    """Pre-generated RSA-2048 keypair (faster than 4096 for tests)."""
    from cryptography.hazmat.primitives.asymmetric import rsa
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


@pytest.fixture
def ed25519_keypair():
    """Pre-generated Ed25519 keypair."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


@pytest.fixture
def ec_keypair():
    """Pre-generated SECP256R1 keypair."""
    from cryptography.hazmat.primitives.asymmetric import ec
    private_key = ec.generate_private_key(ec.SECP256R1())
    return private_key, private_key.public_key()


@pytest.fixture
def temp_image(tmp_path):
    """Temporary PNG image file for steganography tests."""
    from PIL import Image
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    path = str(tmp_path / "test_image.png")
    img.save(path)
    return path


@pytest.fixture
def known_entropy_data():
    """Data with known Shannon entropy value (all same byte = 0.0 entropy)."""
    return b"\x00" * 1024
